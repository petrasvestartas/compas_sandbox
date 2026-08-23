#! python3
# venv: compas-sandbox
# r: compas_sandbox
"""Diagnose the bundled IPOPT solver in this Python environment.

Run this in the Rhino ScriptEditor (or any Python) when a solve fails with
"No IPOPT executable found". The output tells you which case you are in:

- version is not the latest        -> stale install: pip install --upgrade --force-reinstall compas_sandbox
- bin dir MISSING or empty         -> sdist install or antivirus quarantine:
                                      pip install --force-reinstall --only-binary :all: compas_sandbox
                                      (if pip finds no matching distribution, the Python is not a
                                      supported 64-bit platform; if the exe disappears after install,
                                      check the antivirus quarantine and allowlist it)
- ipopt.exe listed but says None   -> the exe is blocked from executing (SmartScreen / antivirus policy)
"""

import os

import compas_sandbox
from compas_sandbox._ipopt import bundled, ipopt_version

print("version:", compas_sandbox.__version__)
print("package at:", os.path.dirname(compas_sandbox.__file__))
bindir = os.path.join(os.path.dirname(compas_sandbox.__file__), "_ipopt", "bin")
print("bin dir:", os.listdir(bindir) if os.path.isdir(bindir) else "MISSING")
print("bundled:", bundled())
print("ipopt says:", ipopt_version())

# the in-process solver (no executable at all) — preferred when installed
try:
    import compas_sandbox_native

    print("native binding: OK, IPOPT", compas_sandbox_native.IPOPT_VERSION)
except ImportError as e:
    print("native binding: not installed ({})".format(e))
