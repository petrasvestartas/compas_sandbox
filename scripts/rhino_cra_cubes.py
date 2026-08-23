#! python3
# venv: compas-sandbox
# r: compas_sandbox
# r: compas_sandbox_native
"""CRA equilibrium of three stacked cubes, drawn in the Rhino document.

Open Rhino 8 -> ScriptEditor (Python 3) -> paste/open this file -> Run.

Solves with compas_sandbox_native: IPOPT compiled into a Python extension module, so
there is no ipopt executable involved at all (nothing for antivirus to quarantine).

Draws:
- free blocks (black wireframe) and support blocks (orange)
- contact interfaces (blue polylines)
- resultant contact forces: green = compression, red = tension
"""

import os

import compas
import rhinoscriptsyntax as rs

import compas_sandbox
from compas_sandbox.algorithms import assembly_interfaces_numpy
from compas_sandbox.datastructures import CRA_Assembly
from compas_sandbox.equilibrium import cra_solve_native

FORCE_SCALE = 0.5

# ----------------------------------------------------------------------------
# load a sample assembly shipped with the package and solve it
# ----------------------------------------------------------------------------

assembly = compas.json_load(os.path.join(compas_sandbox.SAMPLE, "cubes.json"))
assembly = assembly.copy(cls=CRA_Assembly)
assembly.set_boundary_conditions([0])  # node 0 is the support

assembly_interfaces_numpy(assembly, nmax=10, amin=1e-2, tmax=1e-2)
cra_solve_native(assembly, verbose=True, timer=True)

# ----------------------------------------------------------------------------
# draw into the Rhino document
# ----------------------------------------------------------------------------


def ensure_layer(name, color):
    if not rs.IsLayer(name):
        rs.AddLayer(name, color)
    return name


def draw_block(block, layer):
    # bake as wireframe: one line per mesh edge, grouped so a block selects as one
    guids = []
    for edge in block.edges():
        a, b = block.edge_coordinates(edge)
        guids.append(rs.AddLine(a, b))
    rs.ObjectLayer(guids, layer)
    rs.AddObjectsToGroup(guids, rs.AddGroup())


blocks_layer = ensure_layer("CRA::Blocks", (0, 0, 0))
supports_layer = ensure_layer("CRA::Supports", (247, 157, 132))
interfaces_layer = ensure_layer("CRA::Interfaces", (0, 70, 139))
compression_layer = ensure_layer("CRA::Compression", (0, 120, 0))
tension_layer = ensure_layer("CRA::Tension", (200, 0, 0))

rs.EnableRedraw(False)

for node in assembly.graph.nodes():
    block = assembly.graph.node_attribute(node, "block")
    is_support = assembly.graph.node_attribute(node, "is_support")
    draw_block(block, supports_layer if is_support else blocks_layer)

for edge in assembly.graph.edges():
    for interface in assembly.graph.edge_attribute(edge, "interfaces") or []:
        corners = list(interface.points)
        guid = rs.AddPolyline(corners + [corners[0]])
        rs.ObjectLayer(guid, interfaces_layer)

        forces = interface.forces
        if forces is None:
            continue

        # resultant force per interface, exactly as compas_sandbox.viewers draws it
        frame = interface.frame
        w, u, v = frame.zaxis, frame.xaxis, frame.yaxis
        normals = [f["c_np"] - f["c_nn"] for f in forces]
        sum_n = sum(normals)
        sum_u = sum(f["c_u"] for f in forces)
        sum_v = sum(f["c_v"] for f in forces)
        if sum_n == 0:
            continue
        pos = [sum(c[i] * n for c, n in zip(corners, normals)) / sum_n for i in range(3)]
        f = (w * sum_n + u * sum_u + v * sum_v) * 0.5 * FORCE_SCALE
        p1 = [pos[i] + f[i] for i in range(3)]
        p2 = [pos[i] - f[i] for i in range(3)]
        guid = rs.AddLine(p1, p2)
        rs.ObjectLayer(guid, compression_layer if sum_n >= 0 else tension_layer)
        dot = rs.AddTextDot("{:.2f}".format(abs(sum_n)), pos)
        rs.ObjectLayer(dot, compression_layer if sum_n >= 0 else tension_layer)

rs.EnableRedraw(True)
rs.ZoomExtents(all=True)
for layer in (blocks_layer, supports_layer, interfaces_layer, compression_layer, tension_layer):
    print("{}: {} objects".format(layer, len(rs.ObjectsByLayer(layer) or [])))
