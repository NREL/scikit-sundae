import pytest
import numpy as np

from sksundae.cvode import CVODE
from sksundae.precond import CVODEPrecond


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


@pytest.mark.parametrize('linsolver', ('gmres', 'bicgstab', 'tfqmr'))
def test_iterative_no_precond(linsolver):
    y0 = np.array([1, 2])

    solver = CVODE(ode, linsolver=linsolver, rtol=1e-9, atol=1e-12)

    tspan = np.linspace(0, 10, 11)  # normal solve - user picks times
    soln = solver.solve(tspan, y0)
    assert len(tspan) > 2 and len(tspan) == len(soln.t)
    assert np.allclose(soln.y, ode_soln(soln.t, y0))

    tspan = np.array([0, 10])  # onestep solve - integrator picks times
    soln = solver.solve(tspan, y0)
    assert len(tspan) == 2 and len(soln.t) > 2
    assert np.allclose(soln.y, ode_soln(soln.t, y0))


@pytest.mark.parametrize('linsolver', ('gmres', 'bicgstab', 'tfqmr'))
def test_incompatible_options(linsolver):

    def jacfn(t, y, yp, JJ):
        pass

    with pytest.raises(ValueError):
        _ = CVODE(ode, linsolver=linsolver, sparisty=np.eye(2))

    with pytest.raises(ValueError):
        _ = CVODE(ode, linsolver=linsolver, jacfn=jacfn)


def rhsfn(t, y, yp, userdata):
    yp[0] = y[1]
    yp[1] = 1000*(1 - y[0]**2)*y[1] - y[0]


def jacfn(t, y, yp, JJ, userdata):
    JJ[0, 0] = 0
    JJ[0, 1] = 1
    JJ[1, 0] = -2000*y[0]*y[1] - 1
    JJ[1, 1] = 1000*(1 - y[0]**2)


def psetupfn(t, y, yp, jok, jnew, gamma, userdata):
    if jok:
        jnew[0] = 0
    else:
        jnew[0] = 1
        Pmat = userdata['Pmat']
        jacfn(t, y, yp, Pmat, userdata)


def psolvefn(t, y, yp, rvec, zvec, gamma, delta, lr, userdata):
    Pmat = userdata['Pmat']
    zvec[:] = np.linalg.solve(Pmat, rvec)


@pytest.mark.parametrize(('linsolver', 'side'), (('gmres', 'left'),
                         ('bicgstab', 'right'), ('tfqmr', 'both')))
def test_preconditioners(linsolver, side):
    tspan = np.array([0, 3000])
    y0 = np.array([2, 0])

    precond = CVODEPrecond(psetupfn, psolvefn, side)
    userdata = {'Pmat': np.zeros((y0.size, y0.size))}

    solver = CVODE(rhsfn, linsolver=linsolver, precond=precond,
                   userdata=userdata)

    soln = solver.solve(tspan, y0)
    assert soln.success
