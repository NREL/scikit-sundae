import pytest
import numpy as np

from scipy import sparse
from sksundae import cvode
from sksundae._cy_common import config

N = 10  # number of repeats for Van der Pol problem
has_superlu = config['SUNDIALS_SUPERLUMT_ENABLED'] == "True"


def rhsfn_narrow(t, y, yp):
    y0 = y[0::2]
    y1 = y[1::2]

    yp[0::2] = y1
    yp[1::2] = 1000*(1 - y0**2)*y1 - y0


def rhsfn_wide(t, y, yp):
    y0 = y[:N]
    y1 = y[N:]

    yp[:N] = y1
    yp[N:] = 1000*(1 - y0**2)*y1 - y0


@pytest.mark.skipif(not has_superlu, reason='SuperLU_MT not enabled')
def test_sparse_err_warn():

    # forgot sparsity
    with pytest.raises(ValueError):
        _ = cvode.CVODE(rhsfn_narrow, linsolver='sparse')

    # nthreads ignored if linsolver != 'sparse'
    with pytest.warns(UserWarning):
        _ = cvode.CVODE(rhsfn_narrow, nthreads=-1)


@pytest.mark.skipif(not has_superlu, reason='SuperLU_MT not enabled')
def test_sparse_solver():

    tspan = np.linspace(0, 3000, 1000)

    # narrow bandwidth repeating Van der Pol problem, w/ array 'sparsity'
    y0 = np.tile([2, 0], reps=N)

    sparsity = np.zeros((2*N, 2*N))
    for i in range(N):
        sparsity[2*i:2*(i+1), 2*i:2*(i+1)] = np.array([[0, 1], [1, 1]])

    solver = cvode.CVODE(rhsfn_narrow, atol=1e-8, linsolver='sparse',
                         sparsity=sparsity)

    soln = solver.solve(tspan, y0)
    assert soln.success

    # wide bandwidth repeating Van der Pol problem, w/ sparse 'sparsity'
    y0 = np.zeros(2*N)
    y0[:N] = 2.

    diags = [
        np.ones(N),
        np.hstack([np.zeros(N), np.ones(N)]),
        np.ones(N),
    ]
    offsets = [-N, 0, N]
    sparsity = sparse.diags(diags, offsets, shape=(2*N, 2*N))

    solver = cvode.CVODE(rhsfn_wide, atol=1e-8, linsolver='sparse',
                         sparsity=sparsity, nthreads=-1)

    soln = solver.solve(tspan, y0)
    assert soln.success
