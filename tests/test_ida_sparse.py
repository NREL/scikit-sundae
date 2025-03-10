import pytest
import numpy as np

from scipy import sparse
from sksundae import ida
from sksundae._cy_common import config

N = 10  # number of repeats for Robertson problem
has_superlu = config['SUNDIALS_SUPERLUMT_ENABLED']


def resfn_narrow(t, y, yp, res):
    y0, yp0 = y[0::3], yp[0::3]
    y1, yp1 = y[1::3], yp[1::3]
    y2, _ = y[2::3], yp[2::3]

    res[0::3] = yp0 + 0.04*y0 - 1e4*y1*y2
    res[1::3] = yp1 - 0.04*y0 + 1e4*y1*y2 + 3e7*y1**2
    res[2::3] = y0 + y1 + y2 - 1


def resfn_wide(t, y, yp, res):
    y0, yp0 = y[0:N], yp[0:N]
    y1, yp1 = y[N:2*N], yp[N:2*N]
    y2, _ = y[2*N:3*N], yp[2*N:3*N]

    res[0:N] = yp0 + 0.04*y0 - 1e4*y1*y2
    res[N:2*N] = yp1 - 0.04*y0 + 1e4*y1*y2 + 3e7*y1**2
    res[2*N:3*N] = y0 + y1 + y2 - 1


@pytest.mark.skipif(not has_superlu, reason='SuperLU_MT not enabled')
def test_w_sparse_solver():

    tspan = 4*np.logspace(-6, 6, 50)

    # forgot sparsity
    with pytest.raises(ValueError):
        _ = ida.IDA(resfn_narrow, linsolver='sparse')

    # nthreads ignored if linsolver != 'sparse'
    with pytest.warns(UserWarning):
        _ = ida.IDA(resfn_narrow, nthreads=-1)

    # narrow bandwidth repeating Robertson problem, w/ array 'sparsity'
    y0 = np.tile([1, 0, 0], reps=N)
    yp0 = np.tile([-0.04, 0.04, 0], reps=N)
    alg = np.arange(2, 3*N, 3, dtype=int).tolist()

    sparsity = np.zeros((3*N, 3*N))
    for i in range(N):
        sparsity[3*i:3*(i+1), 3*i:3*(i+1)] = np.ones((3, 3))

    solver = ida.IDA(resfn_narrow, rtol=1e-4, atol=1e-8, algebraic_idx=alg,
                     linsolver='sparse', sparsity=sparsity)

    soln = solver.solve(tspan, y0, yp0)
    assert soln.success

    # wide bandwidth repeating Robertson problem, w/ sparse 'sparsity'
    y0 = np.zeros(3*N)
    y0[:N] = 1.

    yp0 = np.zeros(3*N)
    yp0[:N] = -0.04
    yp0[N:2*N] = 0.04

    alg = np.arange(2*N, 3*N, 1, dtype=int).tolist()

    diags = [
        np.ones(N),
        np.ones(2*N),
        np.ones(3*N),
        np.ones(2*N),
        np.ones(N),
    ]
    offsets = [-2*N, -N, 0, N, 2*N]
    sparsity = sparse.diags(diags, offsets, shape=(3*N, 3*N))

    solver = ida.IDA(resfn_wide, rtol=1e-4, atol=1e-8, algebraic_idx=alg,
                     linsolver='sparse', sparsity=sparsity, nthreads=-1)

    soln = solver.solve(tspan, y0, yp0)
    assert soln.success
