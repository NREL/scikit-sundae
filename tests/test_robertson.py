import os

import pandas as pd
from sksundae import ida

import numpy as np
import numpy.testing as npt


def resfn(t, y, yp, res):
    res[0] = yp[0] + 0.04*y[0] - 1e4*y[1]*y[2]
    res[1] = yp[1] - 0.04*y[0] + 1e4*y[1]*y[2] + 3e7*y[1]**2
    res[2] = y[0] + y[1] + y[2] - 1


def test_against_C_solution():
    here = os.path.dirname(__file__)
    data = pd.read_csv(here + '/C_programs/robertson/output.csv')

    tspan = 4*np.logspace(-6, 6, 50)
    y0 = np.array([1, 0, 0])
    yp0 = np.array([-0.04, 0.04, 0])

    solver = ida.IDA(resfn, rtol=1e-4, atol=1e-8, algebraic_idx=[2])
    soln = solver.solve(tspan, y0, yp0)

    soln.y[:, 1] *= 1e4  # Scale y1 values prior to comparison
    data.y1 *= 1e4

    npt.assert_allclose(soln.t, data.t)
    npt.assert_allclose(soln.y, data[['y0', 'y1', 'y2']])
