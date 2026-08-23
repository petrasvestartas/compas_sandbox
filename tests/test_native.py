"""Tests for the in-process IPOPT binding and the pyomo-free CRA formulation.

Skipped entirely when the compas_sandbox_native extension is not installed.
The parity tests additionally need the bundled ipopt executable (the pyomo path).
"""

import numpy as np
import pytest
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Translation
from compas_assembly.datastructures import Block

from compas_sandbox._ipopt import executable
from compas_sandbox.datastructures import CRA_Assembly
from compas_sandbox.equilibrium.cra_nlp import cra_problem

pytest.importorskip("compas_sandbox_native")

needs_exe = pytest.mark.skipif(executable() is None, reason="no ipopt executable for the pyomo reference solve")


def box_assembly():
    support = Box(1, 1, 1)
    free1 = Box(1, 1, 1, frame=Frame.worldXY().transformed(Translation.from_vector([0, 0, 1])))
    assembly = CRA_Assembly()
    assembly.add_block(Block.from_shape(support), node=0)
    assembly.add_block(Block.from_shape(free1), node=1)
    assembly.set_boundary_conditions([0])
    interface = Mesh()
    for i, c in enumerate([[0.5, 0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5]]):
        interface.add_vertex(key=i, x=c[0], y=c[1], z=c[2])
    interface.add_face([0, 1, 2, 3])
    assembly.add_interfaces_from_meshes([interface], 0, 1)
    return assembly


def interface_forces(assembly):
    forces = []
    for edge in assembly.graph.edges():
        for interface in assembly.graph.edge_attribute(edge, "interfaces"):
            for f in interface.forces:
                forces.append((f["c_np"], f["c_u"], f["c_v"]))
    return forces


def test_derivatives_match_finite_differences():
    problem, _ = cra_problem(box_assembly(), density=1)
    rng = np.random.default_rng(7)
    for _ in range(3):
        x = rng.normal(scale=0.7, size=problem.n)
        lam = rng.normal(size=problem.m)
        assert problem.check_gradient(x) < 1e-6
        assert problem.check_jacobian(x) < 1e-6
        assert problem.check_hessian(x, sigma=0.9, lam=lam) < 1e-6


def test_native_box():
    """The one-cube-on-a-cube case has the analytic answer 0.25 per corner."""
    from compas_sandbox.equilibrium.cra_native import cra_solve_native

    assembly = box_assembly()
    cra_solve_native(assembly, density=1)
    for c_np, _, _ in interface_forces(assembly):
        assert c_np == pytest.approx(0.25, abs=1e-6)


@needs_exe
def test_native_matches_pyomo_box():
    from compas_sandbox.equilibrium import cra_solve
    from compas_sandbox.equilibrium.cra_native import cra_solve_native

    a1 = box_assembly()
    cra_solve_native(a1, density=1)
    a2 = box_assembly()
    cra_solve(a2, density=1)
    for f1, f2 in zip(interface_forces(a1), interface_forces(a2)):
        assert f1 == pytest.approx(f2, abs=1e-8)


@needs_exe
def test_native_matches_pyomo_arch():
    from compas_sandbox.algorithms import assembly_interfaces_numpy
    from compas_sandbox.equilibrium import cra_solve
    from compas_sandbox.equilibrium.cra_native import cra_solve_native
    from compas_sandbox.geometry import Arch

    def arch():
        a = Arch(height=5.0, span=10.0, thickness=0.5, depth=0.5, num_blocks=20).assembly()
        assembly_interfaces_numpy(a, nmax=10, amin=1e-2, tmax=1e-2)
        return a

    a1 = arch()
    cra_solve_native(a1, mu=0.7)
    a2 = arch()
    cra_solve(a2, mu=0.7)
    f1 = np.array(interface_forces(a1))
    f2 = np.array(interface_forces(a2))
    scale = np.max(np.abs(f2))
    assert np.max(np.abs(f1 - f2)) / scale < 1e-4
