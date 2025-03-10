import pytest
import numpy as np

from sksundae.cvode import CVODE, CVODEResult


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


def test_cvode_solve():
    y0 = np.array([1, 2])

    solver = CVODE(ode, rtol=1e-9, atol=1e-12)

    tspan = np.linspace(0, 10, 11)  # normal solve - user picks times
    soln = solver.solve(tspan, y0)
    assert len(tspan) > 2 and len(tspan) == len(soln.t)
    assert np.allclose(soln.y, ode_soln(soln.t, y0))

    tspan = np.array([0, 10])  # onestep solve - integrator picks times
    soln = solver.solve(tspan, y0)
    assert len(tspan) == 2 and len(soln.t) > 2
    assert np.allclose(soln.y, ode_soln(soln.t, y0))


def test_cvode_step():
    y0 = np.array([1, 2])

    solver = CVODE(ode, rtol=1e-9, atol=1e-12)

    with pytest.raises(ValueError):  # have to call init_step first
        _ = solver.step(10)

    soln_0 = solver.init_step(0, y0)
    assert np.allclose(soln_0.y, ode_soln(soln_0.t, y0))

    soln_10 = solver.step(10)
    assert np.allclose(soln_10.y, ode_soln(soln_10.t, y0))

    soln_1000 = solver.step(1000, method='onestep', tstop=1000)
    assert soln_1000.t > 10 and soln_1000.t < 1000
    assert np.allclose(soln_1000.y, ode_soln(soln_1000.t, y0))


def test_cvode_userdata():
    y0 = np.array([1, 2])

    def ode_w_data(t, y, yp, userdata):
        yp[0] = userdata['rate']
        yp[1] = y[1]

    with pytest.raises(ValueError):  # userdata keyword arg cannot be None
        _ = CVODE(ode_w_data, rtol=1e-9, atol=1e-12)

    solver = CVODE(ode_w_data, rtol=1e-9, atol=1e-12, userdata={'rate': 0.1})

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert np.allclose(soln.y, ode_soln(soln.t, y0))


def test_cvode_method():
    y0 = np.array([1, 2])

    solver = CVODE(ode, method='Adams', rtol=1e-9, atol=1e-12, max_order=12)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert np.allclose(soln.y, ode_soln(soln.t, y0))


def test_cvode_atol():
    y0 = np.array([1, 2])

    with pytest.raises(ValueError):  # atol dimension doesn't match y
        solver = CVODE(ode, rtol=1e-9, atol=[1e-12, 1e-12, 1e-12])
        _ = solver.init_step(0, y0)

    solver = CVODE(ode, rtol=1e-9, atol=[1e-12, 1e-12])
    soln_0 = solver.init_step(0, y0)
    assert np.allclose(soln_0.y, ode_soln(soln_0.t, y0))


def test_cvode_linsolver():
    y0 = np.array([1, 2])

    with pytest.raises(ValueError):  # forgot bandwidth(s)
        _ = CVODE(ode, rtol=1e-9, atol=1e-12, linsolver='band')

    solver = CVODE(ode, rtol=1e-9, atol=1e-12, linsolver='band', lband=0,
                   uband=0)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert np.allclose(soln.y, ode_soln(soln.t, y0))


@pytest.mark.parametrize('linsolver', ['dense', 'band'])
def test_cvode_sparsity(linsolver):  # using cvLSSparseDQJac for dense/band
    y0 = np.array([1, 2])

    sparsity = np.array([[0, 0], [0, 1]])

    options = {}
    if linsolver == 'band':
        options.update({'lband': 0, 'uband': 0})

    solver = CVODE(ode, rtol=1e-9, atol=1e-12, linsolver=linsolver,
                   sparsity=sparsity, **options)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert np.allclose(soln.y, ode_soln(soln.t, y0))


def test_cvode_constraints():
    y0 = np.array([1, 2])

    # cannot satisfy constraints
    solver = CVODE(ode, rtol=1e-9, atol=1e-12, constraints_idx=[0, 1],
                   constraints_type=[-2, -2])

    _ = solver.init_step(0, y0)
    soln = solver.step(10)
    assert not soln.success

    # can satisfy constraints
    solver = CVODE(ode, rtol=1e-9, atol=1e-12, constraints_idx=[0, 1],
                   constraints_type=[2, 2])

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert np.allclose(soln.y, ode_soln(soln.t, y0))


def test_cvode_eventsfn():
    y0 = np.array([1, 2])

    def eventsfn(t, y, events):
        events[0] = y[0] - 1.55

    with pytest.raises(ValueError):  # forgot num_events
        _ = CVODE(ode, rtol=1e-9, atol=1e-12, eventsfn=eventsfn)

    solver = CVODE(ode, rtol=1e-9, atol=1e-12, eventsfn=eventsfn, num_events=1)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert soln.t[-1] < tspan[-1]  # event was terminal
    assert np.allclose(soln.y, ode_soln(soln.t, y0))

    assert np.isclose(soln.i_events[0], [1])  # event detected correctly
    assert np.isclose(soln.y_events[0][0], 1.55)

    assert np.isclose(soln.t_events[0], soln.t[-1])  # event was concatenated
    assert np.allclose(soln.y_events[0], soln.y[-1])

    eventsfn.terminal = [False]

    solver = CVODE(ode, rtol=1e-9, atol=1e-12, eventsfn=eventsfn, num_events=1)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert np.isclose(soln.t[-1], tspan[-1])  # event wasn't terminal
    assert np.allclose(soln.y, ode_soln(soln.t, y0))

    assert np.isclose(soln.i_events[0], [1])  # event detected correctly
    assert np.isclose(soln.y_events[0][0], 1.55)

    assert not np.isclose(soln.t_events[0], soln.t[-1])  # didn't concatenate
    assert not np.allclose(soln.y_events[0], soln.y[-1])

    eventsfn.direction = [-1]

    solver = CVODE(ode, rtol=1e-9, atol=1e-12, eventsfn=eventsfn, num_events=1)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert np.isclose(soln.t[-1], tspan[-1])  # event didn't trigger
    assert np.allclose(soln.y, ode_soln(soln.t, y0))

    assert soln.i_events is None  # event didn't trigger
    assert soln.t_events is None
    assert soln.y_events is None


def test_cvode_jacfn():
    y0 = np.array([1, 2])

    def jacfn(t, y, fy, JJ):
        JJ[1, 1] = 1

    # preference between sparsity and jacfn
    with pytest.warns(UserWarning):
        _ = CVODE(ode, jacfn=jacfn, sparsity=np.ones((2, 2)))

    solver = CVODE(ode, rtol=1e-9, atol=1e-12, jacfn=jacfn)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert np.allclose(soln.y, ode_soln(soln.t, y0))

    solver = CVODE(ode, rtol=1e-9, atol=1e-12, linsolver='band',
                   lband=0, uband=0, jacfn=jacfn)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)
    assert np.allclose(soln.y, ode_soln(soln.t, y0))


def test_failures_on_exceptions():

    # exception in rhsfn
    def bad_ode(t, y, yp):
        if t > 1:
            raise ValueError("propagated exception")

        yp[0] = 0.1
        yp[1] = y[1]

    y0 = np.array([1, 2])

    solver = CVODE(bad_ode, rtol=1e-9, atol=1e-12)

    tspan = np.linspace(0, 10, 11)
    with pytest.raises(ValueError, match='propagated exception'):
        _ = solver.solve(tspan, y0)

    # exceptions in eventsfn
    def eventsfn(t, y, events):
        if t > 1:
            raise ValueError("propagated exception")

        events[0] = y[0] - 1.55

    solver = CVODE(ode, rtol=1e-9, atol=1e-12, eventsfn=eventsfn, num_events=1)

    tspan = np.linspace(0, 10, 11)
    with pytest.raises(ValueError, match='propagated exception'):
        _ = solver.solve(tspan, y0)

    # exceptions in jacfn
    def jacfn(t, y, fy, JJ):
        if t > 1:
            raise ValueError("propagated exception")

        JJ[1, 1] = 1

    solver = CVODE(ode, rtol=1e-9, atol=1e-12, jacfn=jacfn)

    tspan = np.linspace(0, 10, 11)
    with pytest.raises(ValueError, match='propagated exception'):
        _ = solver.solve(tspan, y0)


def test_CVODEResult():
    y0 = np.array([1, 2])

    solver = CVODE(ode, rtol=1e-9, atol=1e-12)

    tspan = np.linspace(0, 10, 11)
    soln = solver.solve(tspan, y0)

    result = CVODEResult(**soln.__dict__)
    assert result.message == soln.message
    assert result.success == soln.success
    assert result.status == result.status
    assert np.allclose(result.t, soln.t)
    assert np.allclose(result.y, soln.y)
    assert result.i_events == soln.i_events  # Don't use allclose here b/c
    assert result.t_events == soln.t_events  # all events are None.
    assert result.y_events == soln.y_events
    assert result.nfev == soln.nfev
    assert result.njev == soln.njev
