#! python3
# venv: compas-sandbox
# r: compas_sandbox>=0.7.2
"""Check that the in-process IPOPT solver is available in this Python environment."""

import os

import compas_sandbox

print("compas_sandbox:", compas_sandbox.__version__)
print("package at:", os.path.dirname(compas_sandbox.__file__))

try:
    import compas_sandbox_native

    print("solver: OK, IPOPT", compas_sandbox_native.IPOPT_VERSION)
except ImportError as e:
    print("solver: NOT AVAILABLE ({})".format(e))
    print("fix: pip install compas_sandbox_native  (or reinstall compas_sandbox, which depends on it)")
