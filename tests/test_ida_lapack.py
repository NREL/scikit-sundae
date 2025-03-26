import pytest
import numpy as np

from sksundae import ida
from sksundae._cy_common import config

has_lapack = config['SUNDIALS_BLAS_LAPACK_ENABLED'] == "True"


def dae(t, y, yp, res):
    res[0] = yp[0] - 0.1
    res[1] = 2*y[0] - y[1]


def dae_soln(t, y0):
    if hasattr(t, 'size'):
        y = np.zeros([t.size, 2])
        y[:, 0] = 0.1*t + y0[0]
        y[:, 1] = 2*y[:, 0]
    else:
        y = np.zeros([2])
        y[0] = 0.1*t + y0[0]
        y[1] = 2*y[0]
    return y


@pytest.mark.skipif(not has_lapack, reason='LAPACK not enabled')
def test_lapackdense_solver():
    y0 = np.array([1, 2])
    yp0 = np.array([0.1, 0.2])

    solver = ida.IDA(dae, linsolver='lapackdense', rtol=1e-9, atol=1e-12,
                     algebraic_idx=[1])

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0, yp0)
    assert np.allclose(soln.y, dae_soln(soln.t, y0))


@pytest.mark.skipif(not has_lapack, reason='LAPACK not enabled')
def test_lapackband_solver():
    y0 = np.array([1, 2])
    yp0 = np.array([0.1, 0.2])

    with pytest.raises(ValueError):  # forgot bandwidth(s)
        _ = ida.IDA(dae, rtol=1e-9, atol=1e-12, linsolver='lapackband')

    solver = ida.IDA(dae, rtol=1e-9, atol=1e-12, algebraic_idx=[1],
                     linsolver='lapackband', lband=0, uband=0)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0, yp0)
    assert np.allclose(soln.y, dae_soln(soln.t, y0))
