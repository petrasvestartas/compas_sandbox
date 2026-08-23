# Packaging

`compas_sandbox` solves its models with [IPOPT](https://coin-or.github.io/Ipopt/)
compiled into a Python extension module — the `compas_sandbox_native` package in
[`native/`](../native). `build_ipopt.sh` builds IPOPT (with the MUMPS linear solver)
from source with coinbrew as **static libraries**, staged into `build/ipopt/stage`;
the extension links against that stage tree. `.github/workflows/native.yml` runs the
build per platform and packs the extension wheels for CPython 3.9–3.13 with
cibuildwheel.

| script | what it does |
| --- | --- |
| `build_ipopt.sh` | builds IPOPT + MUMPS from source and stages libraries and headers into `build/ipopt/stage` |

## What goes into the binary

- **IPOPT 3.14.19**, Eclipse Public License 2.0
- **MUMPS** as the linear solver. This is IPOPT's default and the one `compas_sandbox`
  relies on, since none of the formulations set `linear_solver`.
- **AMPL ASL**, without which the `ipopt` executable is not built at all.
- **BLAS/LAPACK**: a static OpenBLAS on Linux and Windows, Accelerate on macOS - named
  by its SDK stub path, because `-framework Accelerate` does not survive libtool.
- **No HSL.** The HSL linear solvers (`ma27`, `ma57`, ...) are not redistributable.

Everything that can be is linked statically, so the shipped binary has no dynamic
dependencies beyond the platform's own system libraries. That is what
`check_binary.sh` enforces, and it is why no `auditwheel`/`delocate` step is needed.

## Building locally

```bash
packaging/build_ipopt.sh                          # ~15 minutes
packaging/build_wheel.sh manylinux_2_28_x86_64    # or your platform tag
packaging/test_wheel.sh
```

On Linux, build inside the manylinux container so the result runs on older
distributions than your own:

```bash
docker run --rm -v "$PWD":/io -w /io quay.io/pypa/manylinux_2_28_x86_64 bash -c '
  dnf install -y --enablerepo=powertools glibc-static libstdc++-static openblas-static
  packaging/build_ipopt.sh'
```

On Windows the build runs in an MSYS2 UCRT64 shell; on macOS it needs `gfortran`
(`brew install gcc`).

## Releasing

`.github/workflows/release.yml` builds and tests all five wheels plus an sdist on every
push, and publishes them to PyPI with trusted publishing when a `v*` tag is pushed.

`invoke release <patch|minor|major>` is the way to cut one: it runs the tests, bumps the
version, tags it and pushes. It uploads nothing itself - the tag is what triggers the
publish, and the wheels are built on the runners, never locally. The ipopt binaries are
not in git (see `.gitignore`), so nothing platform-specific travels through the push.

Before uploading, the publish job runs `check_release.py`, which refuses to publish
unless every platform wheel is present and each one actually contains an ipopt
executable. Run it on a set of downloaded artifacts any time:

```bash
python packaging/check_release.py dist
```

| script | what it does |
| --- | --- |
| `check_release.py` | refuses a release that is missing a platform, or a solver |
