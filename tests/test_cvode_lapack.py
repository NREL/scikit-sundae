import pytest
import numpy as np
import numpy.testing as npt

from sksundae import cvode
from sksundae._cy_common import config

has_lapack = config['SUNDIALS_BLAS_LAPACK_ENABLED'] == "True"


def ode(t, y, yp):
    yp[0] = 0.1
    yp[1] = y[1]


def ode_soln(t, y0):
    if hasattr(t, 'size'):
        y = np.zeros([t.size, 2])
        y[:, 0] = 0.1*t + y0[0]
        y[:, 1] = y0[1]*np.exp(t)
    else:
        y = np.zeros([2])
        y[0] = 0.1*t + y0[0]
        y[1] = y0[1]*np.exp(t)
    return y


@pytest.mark.skipif(not has_lapack, reason='LAPACK not enabled')
def test_lapackdense_solver():
    y0 = np.array([1, 2])

    solver = cvode.CVODE(ode, linsolver='lapackdense', rtol=1e-9, atol=1e-12)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    npt.assert_allclose(soln.y, ode_soln(soln.t, y0))


@pytest.mark.skipif(not has_lapack, reason='LAPACK not enabled')
def test_lapackband_solver():
    y0 = np.array([1, 2])

    with pytest.raises(ValueError):  # forgot bandwidth(s)
        _ = cvode.CVODE(ode, rtol=1e-9, atol=1e-12, linsolver='lapackband')

    solver = cvode.CVODE(ode, rtol=1e-9, atol=1e-12, linsolver='lapackband',
                         lband=0, uband=0)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    npt.assert_allclose(soln.y, ode_soln(soln.t, y0))
