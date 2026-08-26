- :mod:`compas_sandbox` uses the `IPOPT <https://coin-or.github.io/Ipopt/>`_ solver with
  the MUMPS linear solver. Ill-conditioned assemblies can end in a non-optimal
  termination condition, which is reported as a :class:`ValueError` by the solver
  functions.

- The solver ships inside the package as the compiled ``compas_sandbox._core``
  extension, so a working install always has one. On a platform without a prebuilt
  wheel, pip falls back to the sdist, which has to compile it: run
  ``packaging/build_ipopt.sh`` first and then ``pip install .`` — see
  ``native/README.md``.
