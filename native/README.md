# compas_sandbox_native

IPOPT (with the MUMPS linear solver) compiled into a Python extension module with
[nanobind](https://github.com/wjakob/nanobind), so `compas_sandbox` can solve CRA
problems in-process: no bundled executable, no subprocess, no `.nl` files.

## Building

The extension links the static IPOPT tree produced by `packaging/build_ipopt.sh`:

```bash
packaging/build_ipopt.sh                  # stages into build/ipopt/stage
pip install ./native                      # picks the stage tree up automatically
```

Point `IPOPT_PREFIX` at a different stage tree to override. Extra link flags (e.g. a
static Fortran runtime) go in `IPOPT_EXTRA_LINK`.

## Usage

Installed alongside `compas_sandbox`, the `nlp` backend discovers it automatically:

```python
from compas_sandbox.equilibrium import cra_solve_native
cra_solve_native(assembly)   # same inputs and results as cra_solve
```
