# Packaging

`compas_sandbox` solves its models with [IPOPT](https://coin-or.github.io/Ipopt/)
compiled into a Python extension module — `compas_sandbox._core`, whose CMake project
lives in [`native/`](../native) and is driven by the root `pyproject.toml` through
scikit-build-core. `build_ipopt.sh` builds IPOPT (with the MUMPS linear solver) from
source with coinbrew as **static libraries**, staged into `build/ipopt/stage`; the
extension links against that stage tree. `.github/workflows/pipeline.yml` runs the
build per platform and packs the `compas_sandbox` wheels for CPython 3.9–3.13 with
cibuildwheel.

| script | what it does |
| --- | --- |
| `build_ipopt.sh` | builds IPOPT + MUMPS from source and stages libraries and headers into `build/ipopt/stage` |

## What goes into the stage tree

- **IPOPT 3.14.19**, Eclipse Public License 2.0, as `libipopt.a`
- **MUMPS** as the linear solver (`libcoinmumps.a`). This is IPOPT's default and the
  one `compas_sandbox` relies on, since none of the formulations set `linear_solver`.
- **BLAS/LAPACK**: a static OpenBLAS on Linux and Windows, Accelerate on macOS — named
  by its SDK stub path, because `-framework Accelerate` does not survive libtool.
- **No HSL.** The HSL linear solvers (`ma27`, `ma57`, ...) are not redistributable.

IPOPT and MUMPS are linked statically into the extension module. The remaining
runtimes (the Fortran runtime, OpenBLAS) are linked dynamically and grafted into the
wheels by the platform repair tools (`auditwheel` / `delocate` / `delvewheel`) —
the standard approach of the scientific Python wheels.

## Building locally

```bash
packaging/build_ipopt.sh    # ~15 minutes, stages into build/ipopt/stage
pip install ./native        # builds the extension against the stage tree
python native/tests/smoke.py
```

On Linux, build inside the manylinux container so the result runs on older
distributions than your own (this is what CI does through cibuildwheel):

```bash
docker run --rm -v "$PWD":/io -w /io quay.io/pypa/manylinux_2_28_x86_64 bash -c '
  dnf install -y --enablerepo=powertools glibc-static libstdc++-static openblas-static openblas-devel
  CFLAGS="-O2 -fPIC" CXXFLAGS="-O2 -fPIC" FFLAGS="-O2 -fPIC" FCFLAGS="-O2 -fPIC" packaging/build_ipopt.sh'
```

On Windows the build runs in an MSYS2 UCRT64 shell; on macOS it needs `gfortran`
(`brew install gcc`).

## Releasing

`.github/workflows/release.yml` builds and tests the pure Python `compas_sandbox`
package; `.github/workflows/native.yml` builds and smoke-tests the solver wheels.
Both publish to PyPI with trusted publishing when a `v*` tag is pushed.

`invoke release <patch|minor|major>` is the way to cut one: it runs the tests, bumps
the version, tags it and pushes. It uploads nothing itself — the tag is what triggers
the publish, and the wheels are built on the runners, never locally.
