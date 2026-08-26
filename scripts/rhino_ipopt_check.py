#! python3
# venv: compas-sandbox
# r: compas_sandbox>=0.7.3
"""Check that the in-process IPOPT solver is available in this Python environment."""

import os

import compas_sandbox

print("compas_sandbox:", compas_sandbox.__version__)
print("package at:", os.path.dirname(compas_sandbox.__file__))

try:
    from compas_sandbox import _core

    print("solver: OK, IPOPT", _core.IPOPT_VERSION)
except ImportError as e:
    print("solver: NOT AVAILABLE ({})".format(e))
    print("fix: reinstall compas_sandbox from a wheel; the solver ships inside the package")
