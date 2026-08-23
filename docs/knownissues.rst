- :mod:`compas_sandbox` uses the `IPOPT <https://coin-or.github.io/Ipopt/>`_ solver with
  the MUMPS linear solver. Ill-conditioned assemblies can end in a non-optimal
  termination condition, which is reported as a :class:`ValueError` by the solver
  functions.

- The solver is provided by the ``compas_sandbox_native`` package, a compiled extension
  installed automatically as a dependency. If importing it fails (for example on a
  platform without prebuilt wheels), build it from source: run
  ``packaging/build_ipopt.sh`` and then ``pip install ./native`` — see
  ``native/README.md``.
