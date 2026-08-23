.. _Installation:

********************************************************************************
Installation
********************************************************************************

Stable
======

.. code-block:: bash

    pip install compas_sandbox

That is all that is needed, on Windows, macOS (Apple Silicon and Intel) and Linux.
The `IPOPT <https://coin-or.github.io/Ipopt/>`_ solver is compiled into the
``compas_sandbox_native`` dependency as a Python extension module, so solving happens
in-process: no conda environment, no homebrew and no solver executables are involved.

To also install the viewers:

.. code-block:: bash

    pip install compas_sandbox[viz]

Verify the solver is available with:

.. code-block:: bash

    python -c "import compas_sandbox_native as n; print(n.IPOPT_VERSION)"


Rhino 8
=======

Start a Python 3 script in the ScriptEditor with this header and run it — Rhino
installs everything on the first run:

.. code-block:: python

    #! python3
    # venv: compas-sandbox
    # r: compas_sandbox

Ready-to-run examples are in the repository under ``scripts/``.


Latest
======

The latest version can be installed from local source.

.. code-block:: bash

    git clone https://github.com/petrasvestartas/compas_sandbox.git
    cd compas_sandbox
    pip install -e ".[dev]"

The solver extension installs from PyPI as a dependency. To build it from source
instead (for development on the binding itself), build the static IPOPT tree first and
then install the extension package:

.. code-block:: bash

    packaging/build_ipopt.sh
    pip install ./native

See ``native/README.md`` and ``packaging/README.md`` for details.
