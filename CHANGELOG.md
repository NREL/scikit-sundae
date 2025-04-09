# scikit-SUNDAE Changelog

## [Unreleased](https://github.com/NREL/scikit-sundae/)

### New Features
- Add `reduce_bandwidth` function to help restructure sparse problems ([#15](https://github.com/NREL/scikit-sundae/pull/15))
- Implement interfaces for Jacobian-vector products ([#13](https://github.com/NREL/scikit-sundae/pull/13))
- Allow preconditioning for iterative solvers ([#12](https://github.com/NREL/scikit-sundae/pull/12))
- Enable OpenBLAS-linked LAPACK linear solvers ([#11](https://github.com/NREL/scikit-sundae/pull/11))
- Add iterative linear solvers to IDA and CVODE ([#10](https://github.com/NREL/scikit-sundae/pull/10))
- Allow `numpy` types in options checks for both `CVODE` and `IDA` ([#8](https://github.com/NREL/scikit-sundae/pull/8))
- Expose linear solver option that uses SuperLU_MT ([#6](https://github.com/NREL/scikit-sundae/pull/6))
- New `jacband` module for support finding sparsity/bandwidth ([#6](https://github.com/NREL/scikit-sundae/pull/6))
- Custom `sparseDQJac` routines available by supplying `sparsity` ([#6](https://github.com/NREL/scikit-sundae/pull/6))
- Changed signature inspections to support decorated `jit` functions ([#3](https://github.com/NREL/scikit-sundae/pull/3))

### Optimizations
- Move to newest SUNDIALS v7.3 for CI tests/builds ([#16](https://github.com/NREL/scikit-sundae/pull/16))
- Use `np.testing` where possible in tests for more informative fail statements ([#14](https://github.com/NREL/scikit-sundae/pull/14))
- Updates to be compliant with Cython deprecations of `IF/ELIF/ELSE` and `DEF` ([#5](https://github.com/NREL/scikit-sundae/pull/5))
- Replace loops between 1D numpy arrays and SUNDIALS NVectors with single-line memory views and pointer addressing ([#5](https://github.com/NREL/scikit-sundae/pull/5))
- Use `micromamba` instead of `miniconda` in CI ([#3](https://github.com/NREL/scikit-sundae/pull/3))

### Bug Fixes
- Add `sign_y` terms and default to `np.float64` for floating type in `j_pattern` ([#7](https://github.com/NREL/scikit-sundae/pull/7))

### Breaking Changes
None.

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
