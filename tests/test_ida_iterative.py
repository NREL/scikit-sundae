import pytest
import numpy as np

from sksundae.ida import IDA


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

    with pytest.raises(ValueError):
        _ = IDA(dae, linsolver=linsolver, sparisty=np.eye(2))

    with pytest.raises(ValueError):
        _ = IDA(dae, linsolver=linsolver, jacfn=jacfn)
