<picture>
  <source media='(prefers-color-scheme: dark)' srcset='./images/dark_tag.png'
  style='width: 75%; min-width: 250px; max-width: 500px;'>
  <img alt='Logo' src='./images/light_tag.png'
  style='width: 75%; min-width: 250px; max-width: 500px;'>
  </br></br>
</picture> 

[![CI][ci-b]][ci-l] &nbsp;
![tests][test-b] &nbsp;
![coverage][cov-b] &nbsp;
[![pep8][pep-b]][pep-l]

[ci-b]: https://github.com/NREL/BATMODS/actions/workflows/ci.yaml/badge.svg
[ci-l]: https://github.com/NREL/BATMODS/actions/workflows/ci.yaml

[test-b]: ./images/tests.svg
[cov-b]: ./images/coverage.svg

[pep-b]: https://img.shields.io/badge/code%20style-pep8-orange.svg
[pep-l]: https://www.python.org/dev/peps/pep-0008

## Summary
Scikit-SUNDAE provides Python bindings to [SUNDIALS](https://sundials.readthedocs.io/en/latest/) integrators. The implicit differential algebraic (IDA) solver and C-based variable-coefficient ordinary differential equations (CVODE) solver are both included.

The name SUNDAE combines (SUN)DIALS and DAE, which stands for differential algebraic equations. Solvers specific to DAE problems are not frequently available in Python. An ordinary differential equation (ODE) solver is also included for completeness. ODEs can be categorized as a subset of DAEs (i.e., DAEs with no algebraic constraints).

## Installation
Scikit-SUNDAE is installable via either `pip` or `conda`. To install from [PyPI]() use the following command.

```cmd
pip install scikit-sundae
```

If you prefer using the `conda` package manager, you can install scikit-SUNDAE from the `conda-forge` channel using the command below.

```cmd
conda install -c conda-forge scikit-sundae
```

Both sources contain binary installations. If you're combination of operating system and CPU architecture is not supported, please submit an [issue]() to let us know. If you'd prefer to build from source, please see the [documentation]().

## Get Started
You are now ready to start solving. Run one of the following examples to check your installation. Afterward, checkout the [documentation]() for a full list of options (including event functions), more detailed examples, and more.

```python
# Use the CVODE integrator to solve the Van der Pol equation

from sksundae.cvode import CVODE
import matplotlib.pyplot as plt

def rhsfn(t, y, yp):
    yp[0] = y[1]
    yp[1] = 1000*(1 - y[0]**2)*y[1] - y[0]

solver = CVODE(rhsfn)
soln = solver.solve([0, 3000], [2, 0])

plt.plot(soln.t, soln.y[:, 0])
plt.show()
```

The `CVODE` solver demonstrated above is only capable of solving pure ODEs. The constant parameters and time span used above matches the same example given by [MATLAB](https://www.mathworks.com/help/matlab/ref/ode15s.html) for easy comparison. If you are trying to solve a DAE, you will want to use the `IDA` solver instead. A minimal DAE example is given below for the Robertson problem. As with the CVODE example, the parameters below are chosen to match an online [MATLAB](https://www.mathworks.com/help/matlab/ref/ode15s.html) example for easy comparison.

```python
# Use the IDA integrator to solve the Robertson problem

from sksundae.ida import IDA
import matplotlib.pyplot as plt

def resfn(t, y, yp, res):
    res[0] = yp[0] + 0.04*y[0] - 1e4*y[1]*y[2]
    res[1] = yp[1] - 0.04*y[0] + 1e4*y[1]*y[2] + 3e7*y[1]**2
    res[2] = y[0] + y[1] + y[2] - 1

solver = IDA(resfn, algebraic_idx=[2], calc_initcond='yp0')
soln = solver.solve([4e-6, 4e6], [1, 0, 0], [0, 0, 0])

plt.plot(soln.t, soln.y)
plt.legend(['y0', 'y1', 'y2'])
plt.show()
```

**Notes:**
* If you are new to Python, check out [Spyder IDE](https://www.spyder-ide.org/). Spyder is a powerful interactive development environment (IDE) that can make programming in Python more approachable to new users.
* Check out the [solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) function from scipy or the [scipy-dae](https://pypi.org/project/scipy-dae/) package for more examples that you can translate over and try out in scikit-SUNDAE.

## Contributing
If you'd like to contribute to this package, please look through the existing [issues](). If the bug you've caught or the feature you'd like to add isn't already being worked on, please submit a new issue before getting started. You should also read through the [developer guidelines]().

## Acknowledgements
Scikit-SUNDAE was inspired by [scikits.odes](https://scikits-odes.readthedocs.io/en/latest/) which is another package offering Python bindings for SUNDIALS; however, all source code for scikit-SUNDAE is original. If you are looking to use the iterative solvers and/or you are trying to compile from source against a custom-configured SUNDIALS, you will likely want to consider scikits.odes over scikit-SUNDAE.

Since scikit-SUNDAE wraps the SUNDIALS solvers, the binary installations include pre-compiled dynamic libraries. These are self-contained in the scikit-SUNDAE package and will not affect any existing SUNDIALS installations you may already have on your machine. To be in compliance with SUNDIALS distribution requirements, all scikit-SUNDAE distributions include a copy of the SUNDIALS license. In addition, users and developers should be aware of the SUNDIALS [copyright](https://github.com/LLNL/sundials/blob/main/LICENSE).

This work was authored by the National Renewable Energy Laboratory (NREL), operated by Alliance for Sustainable Energy, LLC, for the U.S. Department of Energy (DOE) under Contract No. DE-AC36-08GO28308. This work was supported by funding from DOE's Vehicle Technologies Office (VTO) and Advanced Scientific Computing Research (ASCR) program. The research was performed using computational resources sponsored by the Department of Energy's Office of Energy Efficiency and Renewable Energy and located at the National Renewable Energy Laboratory. The views expressed in the repository do not necessarily represent the views of the DOE or the U.S. Government.