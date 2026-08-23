- :mod:`compas_sandbox` uses the `IPOPT <https://coin-or.github.io/Ipopt/>`_ solver with the
  MUMPS linear solver. Ill-conditioned assemblies can end in a non-optimal termination
  condition, which is reported as a :class:`ValueError` by
  :func:`compas_sandbox.equilibrium.pyomo_helper.pyomo_result_check`.

- If ``compas_sandbox`` was installed from a source distribution rather than a wheel, no
  IPOPT executable is bundled and one has to be available on the ``PATH`` instead. Not
  having one raises ``RuntimeError: No IPOPT executable found``. Installing a binary
  wheel with ``pip install compas_sandbox`` is the simplest fix.
