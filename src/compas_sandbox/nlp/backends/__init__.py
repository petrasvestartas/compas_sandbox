"""NLP solver backends."""

__all__ = ["solve_nlp", "available_backends"]

_BACKENDS = ("native",)


def available_backends():
    """Names of the backends that can be used on this installation."""
    found = []
    try:
        from . import native  # noqa: F401

        if native.is_available():
            found.append("native")
    except ImportError:
        pass
    return found


def solve_nlp(problem, backend="auto", options=None, verbose=False):
    """Solve an :class:`~compas_sandbox.nlp.problem.NLPProblem`.

    Parameters
    ----------
    problem : :class:`~compas_sandbox.nlp.problem.NLPProblem`
        The problem to solve.
    backend : str, optional
        ``"auto"`` picks the first available backend; or a backend name.
    options : dict, optional
        Solver options, passed through to the backend (for the native IPOPT backend
        these are `IPOPT options <https://coin-or.github.io/Ipopt/OPTIONS.html>`_).
    verbose : bool, optional
        Print solver output.

    Returns
    -------
    :class:`~compas_sandbox.nlp.problem.NLPResult`
    """
    if backend == "auto":
        names = available_backends()
        if not names:
            raise RuntimeError(
                "no NLP backend available: the compas_sandbox._core extension is missing, "
                "which means this is a source install without a compiled solver -- "
                "reinstall compas_sandbox from a wheel"
            )
        backend = names[0]
    if backend == "native":
        from . import native

        return native.solve(problem, options=options, verbose=verbose)
    raise ValueError("unknown backend: {!r} (known: {})".format(backend, ", ".join(_BACKENDS)))
