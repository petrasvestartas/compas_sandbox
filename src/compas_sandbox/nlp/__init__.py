"""Solver-agnostic sparse NLP layer.

:class:`~compas_sandbox.nlp.problem.NLPProblem` describes a sparse nonlinear program;
:func:`~compas_sandbox.nlp.solve_nlp` solves one with the best available backend
(currently the in-process IPOPT binding in the ``compas_sandbox._core`` extension).
"""

from .backends import available_backends
from .backends import solve_nlp
from .problem import NLPProblem
from .problem import NLPResult

__all__ = ["NLPProblem", "NLPResult", "solve_nlp", "available_backends"]
