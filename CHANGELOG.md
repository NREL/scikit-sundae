# scikit-SUNDAE Changelog

## [Unreleased](https://github.com/NREL/scikit-sundae/)

### New Features

### Optimizations
- Use `micromamba` over `conda` in CI workflow ([#22](https://github.com/NREL/scikit-sundae/pull/22))
- Remove `IF` and `DEF` compile-time code for future-proofing Cython code ([#22](https://github.com/NREL/scikit-sundae/pull/22)) 

### Bug Fixes
- Change `Exception` propagations to support Cython v3.1 ([#21](https://github.com/NREL/scikit-sundae/pull/21))
- Improve type support by using `Integral` and `Real` ([#21](https://github.com/NREL/scikit-sundae/pull/21))

### Breaking Changes

## [v1.0.1](https://github.com/NREL/scikit-sundae/tree/v1.0.1)

### Bug Fixes
- Fix memory leak in `CVODE` and `IDA` ([#18](https://github.com/NREL/scikit-sundae/pull/18))

## [v1.0.0](https://github.com/NREL/scikit-sundae/tree/v1.0.0)
This is the first official release of scikit-SUNDAE. Main features/capabilities are listed below.

### Features
- Python errors can be propagated through Cython wrappers
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
