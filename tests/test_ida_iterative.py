import pytest
import numpy as np

from sksundae.ida import IDA, IDAPrecond


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


def resfn(t, y, yp, res, userdata):
    res[0] = yp[0] + 0.04*y[0] - 1e4*y[1]*y[2]
    res[1] = yp[1] - 0.04*y[0] + 1e4*y[1]*y[2] + 3e7*y[1]**2
    res[2] = y[0] + y[1] + y[2] - 1


def jacfn(t, y, yp, res, cj, JJ, userdata):
    JJ[0, 0] = 0.04 + cj
    JJ[0, 1] = -1e4*y[2]
    JJ[0, 2] = -1e4*y[1]
    JJ[1, 0] = -0.04
    JJ[1, 1] = 1e4*y[2] + 6e7*y[1] + cj
    JJ[1, 2] = 1e4*y[1]
    JJ[2, 0] = 1
    JJ[2, 1] = 1
    JJ[2, 2] = 1


def psetupfn(t, y, yp, res, cj, userdata):
    Pmat = userdata['Pmat']
    jacfn(t, y, yp, res, cj, Pmat, userdata)


def psolvefn(t, y, yp, res, rvec, zvec, cj, delta, userdata):
    Pmat = userdata['Pmat']
    zvec[:] = np.linalg.solve(Pmat, rvec)


@pytest.mark.parametrize('linsolver', ('gmres', 'bicgstab', 'tfqmr'))
def test_iterative_no_precond(linsolver):
    y0 = np.array([1, 2])
    yp0 = np.array([0.1, 0.2])

    solver = IDA(dae, linsolver=linsolver, rtol=1e-9, atol=1e-12,
                 algebraic_idx=[1])

    tspan = np.linspace(0, 10, 11)  # normal solve - user picks times
    soln = solver.solve(tspan, y0, yp0)
    assert len(tspan) > 2 and len(tspan) == len(soln.t)
    assert np.allclose(soln.y, dae_soln(soln.t, y0))

    tspan = np.array([0, 10])  # onestep solve - integrator picks times
    soln = solver.solve(tspan, y0, yp0)
    assert len(tspan) == 2 and len(soln.t) > 2
    assert np.allclose(soln.y, dae_soln(soln.t, y0))


@pytest.mark.parametrize('linsolver', ('gmres', 'bicgstab', 'tfqmr'))
def test_incompatible_options(linsolver):

    def jacfn(t, y, yp, res, cj, JJ):
        pass

    # iterative solvers don't support jacfn from sparsity or explicit
    with pytest.raises(ValueError):
        _ = IDA(dae, linsolver=linsolver, sparisty=np.eye(2))

    with pytest.raises(ValueError):
        _ = IDA(dae, linsolver=linsolver, jacfn=jacfn)


def test_preconditioner():

    # with psetupfn = None
    precond = IDAPrecond(psolvefn)
    assert precond.side == 'left'

    with pytest.raises(TypeError):
        precond = IDAPrecond(psolvefn, 'psetupfn')

    # with psetupfn defined
    precond = IDAPrecond(psolvefn, psetupfn)
    assert precond.side == 'left'

    with pytest.raises(TypeError):
        precond = IDAPrecond('psolvefn', psetupfn)

    # accidentally switching psolvefn and psetupfn
    precond = IDAPrecond(psetupfn, psolvefn)
    with pytest.raises(ValueError):
        _ = IDA(resfn, linsolver='gmres', precond=precond,
                userdata={})


@pytest.mark.parametrize('linsolver', ('gmres', 'bicgstab', 'tfqmr'))
def test_w_precond_solve(linsolver):
    tspan = np.logspace(-6, 6, 50)
    y0 = np.array([1, 0, 0])
    yp0 = np.zeros_like(y0)

    precond = IDAPrecond(psolvefn, psetupfn)
    userdata = {'Pmat': np.zeros((y0.size, y0.size))}

    solver = IDA(resfn, algebraic_idx=[2], calc_initcond='yp0',
                 atol=1e-12, linsolver=linsolver, precond=precond,
                 userdata=userdata)

    soln = solver.solve(tspan, y0, yp0)
    assert soln.success
