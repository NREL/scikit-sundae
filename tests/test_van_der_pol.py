import os

import numpy as np
import pandas as pd
from sksundae import cvode


def rhsfn(t, y, yp):
    yp[0] = y[1]
    yp[1] = 1000*(1 - y[0]**2)*y[1] - y[0]


def test_agaisnt_C_solution():
    # There are small differences (less than 1e-6) that can occur around stiff
    # transitions, likely due to differences between Python's vs C's handling
    # of floating point calculations. While solutions are visually identical,
    # value comparisons can sometimes fail np.allclose() tests. Therefore, the
    # rtol, atol, and max_dt required iterating over to find a combination that
    # passes np.allclose() for all y. Keep in mind that these may need to be
    # adjusted again for newer versions of SUNDIALS.

    here = os.path.dirname(__file__)
    data = pd.read_csv(here + '/C_programs/van_der_pol/output.csv')

    tspan = np.linspace(0, 3000, 1000)
    y0 = np.array([2, 0])

    solver = cvode.CVODE(rhsfn, rtol=1e-6, atol=1e-8, max_step=0.5)
    soln = solver.solve(tspan, y0)

    assert np.allclose(soln.t, data.t)
    assert np.allclose(soln.y, data[['y0', 'y1']])
