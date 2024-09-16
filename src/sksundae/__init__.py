"""
Scikit-SUNDAE provides Python bindings to `SUNDIALS`_ integrators. The implicit
differential algebraic (IDA) solver and C-based variable-coefficient ordinary
differential equations (CVODE) solver are both included.

The name SUNDAE combines (SUN)DIALS and DAE, which stands for differential
algebraic equations. Solvers specific to DAE problems are not frequently
available in Python. An ordinary differential equation (ODE) solver is also
included for completeness. ODEs can be categorized as a subset of DAEs (i.e.,
DAEs with no algebraic constraints).

.. _SUNDIALS: https://sundials.readthedocs.io

Accessing the documentation
---------------------------
Documentation is accessible via Python's ``help()`` function which prints
docstrings from a package, module, function, class, etc. You can also access
the documentation by visiting the website, hosted through GitHub pages. The
website includes search functionality and more detailed examples.

Acknowledgements
----------------
Scikit-SUNDAE was inspired by `scikits.odes`_, which is another (more complete)
SUNDIALS-bindings library for Python. However, it should be noted that this
package shares no original source code with scikits.odes. Instead, this package
was written from scratch with three main intentions:

1. Have a more consistent API with the `scipy.integrate`_ package.
2. Be built primarily against SUNDIALS binaries from `conda-forge`_.
3. Setup the package for binary distribution.

The second two points are included for a few reasons. First of all, SUNDIALS
installations allow for a wide range of configurable settings. This can make
developing Python bindings challenging because they need to compile against a
variety of different builds. To make testing and maintenance of this package
easier, it is recommended to compile with SUNDIALS distributions form a single
and consistent source, e.g., conda-forge. As an added benefit, building against
conda-forge's SUNDIALS releases means that binary distributions on both PyPI
and conda are the same for a given version of scikit-SUNDAE. The last point is
highlighted because binary installations are a more consistent distribution
method, require less setup (i.e., no pre-installed SUNDIALS and/or C compilers)
- especially when existing as another package's dependency, and make packages
more approachable to new users.

Note that binary distributions also have some drawbacks, particularly when it
comes to SUNDIALS bindings. Distributing binaries means the package includes
pre-built SUNDIALS libraries, which it links against. If a custom-configured
SUNDIALS is required, you'll want to build from a source distribution instead.
Building from source against a custom SUNDIALS configuration is possible with
scikit-SUNDAE, but it is not intended to be the primary distribution method. In
fact, the only real reason to build scikit-SUNDAE against a custom SUNDIALS is
when the default 'double' and 'int32' precisions are not appropriate for your
project.

In contrast, `scikits.odes`_ exclusively uses source distributions. This is
because their package supports optional solvers (e.g., BLAS/LAPACK), which are
not included in all SUNDIALS builds. Rather than assuming a "best" SUNDIALS
configuration to build against and distribute, they leave it to the user to
compile and build against whichever SUNDIALS configuration makes the most sense
for their project.

In short, if you're looking for a more comprehensive set of bindings or want
the flexibility to compile against different SUNDIALS builds, scikits.odes may
be a better choice. However, if you're okay with using SUNDIALS distributions
available through conda-forge and don't need optional and/or iterative solvers,
scikit-SUNDAE is a suitable option.

Since scikit-SUNDAE installations may include pre-built SUNDIALS libraries, the
`SUNDIALS license`_ is linked here and is also included in all installations.
Distribution of SUNDIALS also requires that their copyright be shared. To be
in compliance, the copyright is: Copyright (c) 2002-2024, Lawrence Livermore
National Security and Southern Methodist University. All rights reserved.

.. _scikits.odes: https://scikits-odes.readthedocs.io
.. _conda-forge: https://anaconda.org/conda-forge/sundials
.. _scipy.integrate: https://docs.scipy.org/doc/scipy/reference/integrate.html
.. _SUNDIALS license: https://github.com/LLNL/sundials/blob/main/LICENSE

"""

from . import ida
from . import common
from . import cvode

__all__ = ['ida', 'common', 'cvode']

__version__ = '1.0.0'
