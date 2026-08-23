"""CRA solver on the in-process IPOPT binding — no pyomo, no subprocess.

Solves exactly the problem :func:`~compas_sandbox.equilibrium.cra_solve` solves, with
the same tolerances, and writes the same results to the assembly (``interface.forces``
per contact interface and a ``displacement`` attribute per free node). The two solvers
are interchangeable; the test suite asserts that their results match.
"""

import time

from compas_assembly.datastructures import Assembly

from ..nlp import solve_nlp
from .cra_nlp import cra_problem

__all__ = ["cra_solve_native"]


def cra_solve_native(
    assembly: Assembly,
    mu: float = 0.84,
    density: float = 1.0,
    d_bnd: float = 1e-3,
    eps: float = 1e-4,
    verbose: bool = False,
    timer: bool = False,
) -> Assembly:
    """CRA solver using the in-process IPOPT binding.

    Same parameters, same results as :func:`~compas_sandbox.equilibrium.cra_solve`;
    requires the ``compas_sandbox_native`` package instead of the bundled executable.
    """
    if timer:
        start_time = time.time()

    problem, layout = cra_problem(assembly, mu=mu, density=density, d_bnd=d_bnd, eps=eps)

    if timer:
        print("--- set up time: %s seconds ---" % (time.time() - start_time))
        start_time = time.time()

    result = solve_nlp(problem, backend="native", verbose=verbose)

    if timer:
        print("--- solving time: %s seconds ---" % (time.time() - start_time))

    if not result.success:
        raise ValueError("solve failed: {} ({})".format(result.status, result.status_message))
    print("result: ", result.status)

    _result_to_assembly(result.x, layout, assembly, verbose=verbose)
    return assembly


def _result_to_assembly(x, layout, assembly, verbose=False):
    """Write the solution vector to the assembly, mirroring pyomo_result_assembly."""
    f = x[layout["f"]]
    q = x[layout["q"]]

    offset = 0
    for edge in assembly.graph.edges():
        for interface in assembly.graph.edge_attribute(edge, "interfaces"):
            interface.forces = []
            for i in range(len(interface.points)):
                interface.forces.append(
                    {
                        "c_np": float(f[offset + 3 * i + 0]),
                        "c_nn": 0,
                        "c_u": float(f[offset + 3 * i + 1]),
                        "c_v": float(f[offset + 3 * i + 2]),
                    }
                )
            offset += 3 * len(interface.points)

    if verbose:
        print("q:", list(q))
    offset = 0
    for node in assembly.graph.nodes():
        if assembly.graph.node_attribute(node, "is_support"):
            continue
        assembly.graph.node_attribute(node, "displacement", [float(v) for v in q[offset : offset + 6]])
        offset += 6
