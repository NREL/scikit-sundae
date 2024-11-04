# scikit-SUNDAE Changelog

## [Unreleased](https://github.com/NREL/scikit-sundae/)

### New Features

### Optimizations

### Bug Fixes

### Breaking Changes

## [v1.0.0](https://github.com/NREL/scikit-sundae/tree/v1.0.0)
This is the first official release of scikit-SUNDAE. Main features/capabilities are listed below.

### Features
- Implicit differential algebraic (IDA) solver for differential algebraic equations (DAEs)
- C-based variable-coeffecients ordinary differential equations (CVODE) solver
- Events functions with scipy-like API, including "terminal" and "direction" options
- Dense and banded linear solver options in both IDA and CVODE
- Option for user-supplied Jacobian function in both IDA and CVODE
- scipy-like `RichResult` output containers

### Notes
- Implemented `pytest` with tests that directly compare against solutions generated using C programs
- Source/binary distributions available on [PyPI](https://pypi.org/project/scikit-sundae)
- Documentation available on [Read the Docs](https://scikit-sundae.readthedocs.io/)
