# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed

### Removed


## [0.7.6] 2026-08-26

### Added

### Changed

* The Linux wheel jobs build IPOPT serially (`JOBS=1`). MUMPS' makefiles are missing dependencies, so a parallel build races and dies linking `libcoinmumps`, always just after `dtype3_root.F` and with coinbrew reporting no error at all. It cost three of six pipeline runs. Linux is where it showed up because it is the only platform that rebuilds IPOPT every run rather than restoring a cached stage tree. No change to the package itself.

### Removed


## [0.7.5] 2026-08-26

### Changed

* **`compas_sandbox` ships its own solver again: one package, one version.** IPOPT and the MUMPS linear solver are compiled into the in-package extension `compas_sandbox._core` instead of being pulled in from a separate `compas_sandbox_native` distribution, so `compas_sandbox` is now a platform wheel (CPython 3.9–3.13 on Windows, macOS arm64/x86_64, manylinux x86_64/aarch64) rather than a universal one. The split it replaces could silently desynchronise: a `compas_sandbox` release did not republish the native wheel, so a fix to the compiled solver could sit in the repository without ever reaching users. The CMake project stays in `native/`, now driven by the root `pyproject.toml` through scikit-build-core.
* The CRA solvers use IPOPT's adaptive barrier update (`mu_strategy="adaptive"`). CRA's complementarity constraints are degenerate and the monotone update crawls on them: the 20-block arch needed 1964 of IPOPT's 3000 permitted iterations, leaving almost no margin, and the macOS wheels ran out of iterations entirely and raised `solve failed: failed (Maximum_Iterations_Exceeded)`. The adaptive update reaches the same answer (interface resultants agree to 1e-10) in 668 iterations, and 307 rather than 2757 on a 40-block arch.
* `test_cra_arch` no longer skips itself when the arch stalls, and a companion test asserts the solve keeps its iteration headroom. The skip is what let the macOS failure reach users.
* CI builds and tests `compas_sandbox` wheels directly: the test job installs a built wheel rather than the source tree, so what is tested is what is shipped.

### Removed

* The separate `compas_sandbox_native` distribution. Its contents now ship inside `compas_sandbox`; the runtime dependency on it is gone, and `requirements.txt`, `requirements-dev.txt` and `requirements-viz.txt` are folded into `pyproject.toml`.

## [0.7.2] 2026-08-23

### Added

### Changed

* One ordered release pipeline in `release.yml`: native wheels build first (IPOPT compiled from source), the pure package is tested against the just-built native wheel, then publish native → publish sandbox → GitHub release → docs. `native.yml` is build-only push CI; `docs.yml` builds on main pushes only; the lint job runs without installing the package.

### Removed

## [0.7.1] 2026-08-23

### Added

### Changed

* `compas_sandbox_native` 0.1.1: the audit-hardened binding (sparsity index range checks, transient-callback-exception recovery, automatic quasi-Newton fallback, wall-time status) actually ships to PyPI — 0.1.0 predated those fixes and `skip-existing` had kept re-uploads out.
* Rhino scripts pin `compas_sandbox>=0.7.0` so cached ScriptEditor environments upgrade off the removed executable path.

### Removed

## [0.7.0] 2026-08-23

### Added

* Added `cra_penalty_problem` and `rbe_problem` NLP formulations with exact analytic derivatives, and the matching native solvers `cra_penalty_solve_native` and `rbe_solve_native`, validated against the pyomo implementations before those were removed (max force difference 1.9e-14 for RBE, 7.1e-9 for the penalty formulation).

### Changed

* `cra_solve`, `cra_penalty_solve` and `rbe_solve` are now the in-process native solvers. `compas_sandbox` is a pure Python package again — one universal wheel — with the compiled solver coming from the `compas_sandbox_native` dependency.
* The native wheel workflow builds the Linux wheels with cibuildwheel inside the manylinux containers, in the style of compas_cgal.

### Removed

* Removed the bundled IPOPT executable, the pyomo formulations and the pyomo dependency. There is no solver executable anywhere anymore: solving happens in-process through the nanobind extension, which also removes the Windows antivirus false-positive problem structurally.

## [0.6.6] 2026-08-23

### Added

### Changed

* `compas_sandbox_native` is now a dependency of `compas_sandbox` (on Python < 3.14), so `pip install compas_sandbox` — or a single `# r: compas_sandbox` line in Rhino — brings the in-process solver along automatically.

### Removed

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

