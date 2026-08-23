# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.5] 2026-08-23

### Added

### Changed

* Hardened the native binding after a three-stage independent audit: sparsity index range checks (out-of-range values from Python now raise instead of crashing), a solve that converges despite a transient callback exception keeps its solution, `hessian_approximation=limited-memory` is set automatically when no Hessian callback is given, and `Maximum_WallTime_Exceeded` is reported by name.
* The native backend no longer accepts iteration-capped points; only near-converged endings (`Restoration_Failed`, `Search_Direction_Becomes_Too_Small`) qualify for the feasible-point acceptance check, matching the executable path's failure behavior.
* The Rhino example scripts solve with `cra_solve_native` (in-process, no executable involved).
* macOS arm64 native wheels are built on macOS 14, so they install on macOS 14+.

### Removed

## [0.6.4] 2026-08-23

### Added

* Added `compas_sandbox.nlp`, a solver-agnostic sparse NLP layer, and `compas_sandbox.equilibrium.cra_problem`, the CRA optimisation problem formulated directly in numpy/scipy with exact analytic gradient, Jacobian and Lagrangian Hessian (no pyomo involved).
* Added `compas_sandbox_native` (in `native/`): IPOPT + MUMPS compiled into a Python extension module with nanobind, so CRA problems solve in-process — no bundled executable, no subprocess, no `.nl` files. Results match the pyomo + executable path on the test suite (bit-identical on the cube fixtures, < 1e-5 relative force difference on the arch).
* Added `cra_solve_native`, a drop-in alternative to `cra_solve` using the binding.

### Changed

### Removed

## [0.6.3] 2026-08-23

### Added

* Added the `COMPAS_SANDBOX_IPOPT` environment variable to override the solver location, for machines where antivirus or application-control policies block the bundled binary.
* The Windows `ipopt.exe` now carries a version resource (product, publisher, version, license), and the release workflow supports Authenticode signing via Azure Trusted Signing when the signing secrets are configured.

### Changed

### Removed

## [0.6.2] 2026-08-23

### Added

### Changed

* Lowered `requires-python` to `>= 3.9` so the package installs into Rhino 8's bundled CPython 3.9.

### Removed

## [0.6.1] 2026-08-23

### Added

### Changed

### Removed

## [0.6.0] 2026-08-23

### Added

* Added a bundled, statically linked IPOPT executable to the platform wheels, so `pip install compas_sandbox` no longer needs conda, homebrew or a manually downloaded solver. Wheels are built for Windows, macOS (Apple Silicon and Intel) and manylinux (x86_64 and aarch64) by `.github/workflows/release.yml`.
* Added `packaging/` with the scripts that build IPOPT 3.14.19 from source with coinbrew (MUMPS linear solver, no HSL), pack the platform wheels and test them in a clean environment.
* Added `compas_sandbox._ipopt` to locate the solver, and a `compas-sandbox-ipopt` console script to check which solver will be used.
* Added the `viz` optional dependencies (`pip install compas_sandbox[viz]`).
* Added `packaging/check_release.py`, run by the publish job before uploading: a release is rejected unless it carries a wheel for every supported platform and each wheel actually contains an ipopt executable.

### Changed

* Declared the runtime dependencies (`compas`, `compas_assembly`, `numpy`, `pyomo`, `scipy`, `shapely`) in `requirements.txt`, which was empty.
* `cra_solve`, `cra_penalty_solve` and `rbe_solve` now build their solver with `compas_sandbox.equilibrium._solver.ipopt_solver`, which points pyomo at the bundled executable. Solver options and tolerances are unchanged.
* Rewrote the installation instructions around pip; the manual Windows workaround for missing ipopt binaries is no longer needed.

* Replaced kernel-layer `MatrixConstraint` with standard `pyo.Constraint` rules in `static_equilibrium_constraints` for compatibility with recent Pyomo versions.
* Pinned Python to `< 3.14` for viewer compatibility.

### Removed


## [0.5.0] 2024-10-21

### Added

### Changed

* Changed compas_view2 to compas_viewer.
* Changed sample files to COMPAS 2 format.
* Fixed bug in temp viewer arrow solution.

### Removed

* Removed `matplotlib` from env files.
* Removed `pip` requirements.
* Removed incompatible interface info.


## [0.4.0] 2024-03-02

### Added

* Add delete block and blocks methods in CRA_Assembly class. 
* A script to export mesh to json in Rhino. 

### Changed

### Removed


## [0.3.0] 2022-11-06

### Added

### Changed

### Removed


## [0.2.2] 2022-09-29

### Added

* Add example folder directory to tutorial docs for easy access. 

### Changed

* Fix some typos and wrong url links. 
* Change ipopt installation guide using conda.

### Removed


## [0.2.1] 2022-09-02

### Added

### Changed

### Removed


## [0.2.0] 2022-09-02

### Added

### Changed

### Removed

