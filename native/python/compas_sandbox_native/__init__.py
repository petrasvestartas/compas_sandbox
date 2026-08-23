"""In-process IPOPT solver for compas_sandbox.

The heavy lifting happens in the compiled ``_core`` module, which links IPOPT and the
MUMPS linear solver statically. See ``compas_sandbox.nlp`` for the high-level API.
"""

from ._core import IPOPT_VERSION
from ._core import solve_nlp

__all__ = ["solve_nlp", "IPOPT_VERSION"]
