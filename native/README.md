# compas_sandbox._core

IPOPT (with the MUMPS linear solver) compiled into a Python extension module with
[nanobind](https://github.com/wjakob/nanobind), so `compas_sandbox` can solve CRA
problems in-process: no bundled executable, no subprocess, no `.nl` files.

This directory holds only the CMake project and the binding source. It is not a
separate distribution: the root `pyproject.toml` points scikit-build-core at it
(`cmake.source-dir = "native"`) and the module is installed into the `compas_sandbox`
package, so the solver and the Python code always ship as one versioned wheel.

## Building

The extension links the static IPOPT tree produced by `packaging/build_ipopt.sh`:

```bash
packaging/build_ipopt.sh                  # stages into build/ipopt/stage
pip install .                             # from the repo root; picks the stage tree up
```

Point `IPOPT_PREFIX` at a different stage tree to override. Extra link flags (e.g. a
static Fortran runtime) go in `IPOPT_EXTRA_LINK`.

## Usage

The `nlp` backend discovers the extension automatically:

```python
from compas_sandbox.equilibrium import cra_solve_native
cra_solve_native(assembly)   # same inputs and results as cra_solve
```
