import pytest
import numpy as np
import sksundae as sun

from scipy import sparse

N = 10  # number of repeats for Van der Pol (and Robertson) problems


def cvode_narrow(t, y, yp):
    y0 = y[0::2]
    y1 = y[1::2]

    yp[0::2] = y1
    yp[1::2] = 1000*(1 - y0**2)*y1 - y0


def cvode_wide(t, y, yp):
    y0 = y[:N]
    y1 = y[N:]

    yp[:N] = y1
    yp[N:] = 1000*(1 - y0**2)*y1 - y0


def ida_narrow(t, y, yp, res):
    y0, yp0 = y[0::3], yp[0::3]
    y1, yp1 = y[1::3], yp[1::3]
    y2, _ = y[2::3], yp[2::3]

    res[0::3] = yp0 + 0.04*y0 - 1e4*y1*y2
    res[1::3] = yp1 - 0.04*y0 + 1e4*y1*y2 + 3e7*y1**2
    res[2::3] = y0 + y1 + y2 - 1


def ida_wide(t, y, yp, res):
    y0, yp0 = y[0:N], yp[0:N]
    y1, yp1 = y[N:2*N], yp[N:2*N]
    y2, _ = y[2*N:3*N], yp[2*N:3*N]

    res[0:N] = yp0 + 0.04*y0 - 1e4*y1*y2
    res[N:2*N] = yp1 - 0.04*y0 + 1e4*y1*y2 + 3e7*y1**2
    res[2*N:3*N] = y0 + y1 + y2 - 1


def test_cvode_jpattern():

    # wrong number of arguments
    with pytest.raises(ValueError):
        t0, y0 = 0., np.zeros(2*N)

        def ida_wide_wdata(t, y, yp, res, _):
            ida_wide(t, y, yp, res)

        _ = sun.jacband.j_pattern(ida_wide_wdata, t0, y0, userdata=('none',))

    # expected non-None userdata
    with pytest.warns(UserWarning):
        t0, y0 = 0., np.zeros(2*N)

        def cvode_wide_wdata(t, y, yp, _):
            cvode_wide(t, y, yp)

        _ = sun.jacband.j_pattern(cvode_wide_wdata, t0, y0)

    # Van der Pol with narrow pattern
    t0 = 0.
    y0 = np.tile([2, 0], reps=N)

    correct = np.zeros((2*N, 2*N))
    for i in range(N):
        correct[2*i:2*(i+1), 2*i:2*(i+1)] = np.array([[0, 1], [1, 1]])

    approx = sun.jacband.j_pattern(cvode_narrow, t0, y0)
    np.testing.assert_allclose(correct, approx)

    # Van der Pol with wide pattern
    t0 = 0.
    y0 = np.zeros(2*N)
    y0[:N] = 2.

    diags = [
        np.ones(N),
        np.hstack([np.zeros(N), np.ones(N)]),
        np.ones(N),
    ]
    offsets = [-N, 0, N]
    correct = sparse.diags(diags, offsets, shape=(2*N, 2*N)).toarray()

    approx = sun.jacband.j_pattern(cvode_wide, t0, y0)
    np.testing.assert_allclose(correct, approx)


def test_ida_jpattern():

    # wrong number of arguments
    with pytest.raises(ValueError):
        t0, y0, yp0 = 0., np.zeros(3*N), np.zeros(3*N)
        _ = sun.jacband.j_pattern(cvode_wide, t0, y0, yp0)

    # expected non-None userdata
    with pytest.warns(UserWarning):
        t0, y0, yp0 = 0., np.zeros(3*N), np.zeros(3*N)

        def ida_wide_wdata(t, y, yp, res, _):
            ida_wide(t, y, yp, res)

        _ = sun.jacband.j_pattern(ida_wide_wdata, t0, y0, yp0)

    # Robertson with narrow pattern
    t0 = 0.
    y0 = np.tile([1, 0, 0], reps=N)
    yp0 = np.tile([-0.04, 0.04, 0], reps=N)

    correct = np.zeros((3*N, 3*N))
    for i in range(N):
        correct[3*i:3*(i+1), 3*i:3*(i+1)] = np.ones((3, 3))

    approx = sun.jacband.j_pattern(ida_narrow, t0, y0, yp0)
    np.testing.assert_allclose(correct, approx)

    # Robertson with wide pattern
    t0 = 0.

    y0 = np.zeros(3*N)
    y0[:N] = 1.

    yp0 = np.zeros(3*N)
    yp0[:N] = -0.04
    yp0[N:2*N] = 0.04

    diags = [
        np.ones(N),
        np.ones(2*N),
        np.ones(3*N),
        np.ones(2*N),
        np.ones(N),
    ]
    offsets = [-2*N, -N, 0, N, 2*N]
    correct = sparse.diags(diags, offsets, shape=(3*N, 3*N)).toarray()

    approx = sun.jacband.j_pattern(ida_wide, t0, y0, yp0)
    np.testing.assert_allclose(correct, approx)


def test_bandwidth():

    # wide banded matrix
    diags = [
        np.ones(N),
        np.hstack([np.zeros(N), np.ones(N)]),
        np.ones(N),
    ]
    offsets = [-N, 0, N]
    diagonal = sparse.diags(diags, offsets, shape=(2*N, 2*N)).toarray()

    bands = sun.jacband.bandwidth(diagonal)
    assert bands[0] == N
    assert bands[1] == N

    # narrow block-banded matrix
    sparsity = np.zeros((3*N, 3*N))
    for i in range(N):
        sparsity[3*i:3*(i+1), 3*i:3*(i+1)] = np.ones((3, 3))

    bands = sun.jacband.bandwidth(sparsity)
    assert bands[0] == 2
    assert bands[1] == 2
