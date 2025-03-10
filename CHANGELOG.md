# scikit-SUNDAE Changelog

## [Unreleased](https://github.com/NREL/scikit-sundae/)

### New Features
- Expose linear solver option that uses SuperLU_MT ([PR #6](https://github.com/NREL/scikit-sundae/pull/6))
- New `jacband` module for support finding sparsity/bandwidth ([PR #6](https://github.com/NREL/scikit-sundae/pull/6))
- Custom `sparseDQJac` routines available by supplying `sparsity` ([PR #6](https://github.com/NREL/scikit-sundae/pull/6))
- Changed signature inspections to support decorated `jit` functions ([PR #3](https://github.com/NREL/scikit-sundae/pull/3))

### Optimizations
- Use `micromamba` instead of `miniconda` in CI ([PR #3](https://github.com/NREL/scikit-sundae/pull/3))
- Updates to be compliant with Cython deprecations of `IF/ELIF/ELSE` and `DEF` ([PR #5](https://github.com/NREL/scikit-sundae/pull/5))
- Replace loops that write data between 1D numpy arrays and SUNDIALS NVectors in favor of single-line memory views with pointer addressing ([PR #5](https://github.com/NREL/scikit-sundae/pull/5))

### Bug Fixes

### Breaking Changes

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
