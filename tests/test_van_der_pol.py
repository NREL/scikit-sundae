import os

import numpy as np
import pandas as pd
from sksundae import cvode


def rhsfn_nonstiff(t, y, yp):
    yp[0] = y[1]
    yp[1] = (1 - y[0]**2)*y[1] - y[0]


def rhsfn_stiff(t, y, yp):
    yp[0] = y[1]
    yp[1] = 1000*(1 - y[0]**2)*y[1] - y[0]


def test_successful_stiff_solve():

    tspan = np.linspace(0, 3000, 1000)
    y0 = np.array([2, 0])

    solver = cvode.CVODE(rhsfn_stiff, rtol=1e-6, atol=1e-8, max_step=0.5)
    soln = solver.solve(tspan, y0)

    assert soln.success
    assert soln.t[-1] == tspan[-1]


def test_nonstiff_agaisnt_C_solution():
    # Only the nonstiff solution is checked against the solution generated from
    # a SUNDIALS C program because the stiff problem transitions from large to
    # small values at slightly different times, making errors seems larger than
    # they are. NOTE: If GitHub actions has issues with checking this solution
    # based on the 'onestep_solve', change over to using a linspace time span.

    here = os.path.dirname(__file__)
    data = pd.read_csv(here + '/C_programs/van_der_pol/output.csv')

    tspan = np.array([0, 20])
    y0 = np.array([2, 0])

    solver = cvode.CVODE(rhsfn_nonstiff, rtol=1e-6, atol=1e-8)
    soln = solver.solve(tspan, y0)

    assert np.allclose(soln.t, data.t)
    assert np.allclose(soln.y, data[['y0', 'y1']])
