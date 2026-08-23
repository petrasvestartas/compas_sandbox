#! python3
# venv: compas-sandbox
# r: compas_sandbox
# r: compas_sandbox_native
"""CRA equilibrium of a parametric masonry arch, drawn in the Rhino document.

Solves with compas_sandbox_native: IPOPT compiled into a Python extension module, so
there is no ipopt executable involved at all (nothing for antivirus to quarantine).

Open Rhino 8 -> ScriptEditor (Python 3) -> open this file -> Run.

Draws:
- voussoir blocks (gray) and the two support blocks (orange)
- contact interfaces (blue polylines)
- resultant contact forces: green = compression, red = tension,
  with a text dot showing the normal-force magnitude
"""

import rhinoscriptsyntax as rs

from compas_sandbox.algorithms import assembly_interfaces_numpy
from compas_sandbox.equilibrium import cra_solve_native
from compas_sandbox.geometry import Arch

# ----------------------------------------------------------------------------
# parameters — tweak and re-run
# ----------------------------------------------------------------------------

HEIGHT = 5.0  # rise of the arch (must be <= SPAN / 2, semicircular at the limit)
SPAN = 10.0  # distance between supports
THICKNESS = 0.5  # radial thickness of the voussoirs
DEPTH = 0.5  # out-of-plane depth
NUM_BLOCKS = 20  # number of voussoirs (including the two supports)
MU = 0.7  # friction coefficient
FORCE_SCALE = 0.5  # length of the drawn force lines per unit of force

# ----------------------------------------------------------------------------
# build the arch assembly and solve it (Arch marks its end blocks as supports)
# ----------------------------------------------------------------------------

assembly = Arch(
    height=HEIGHT,
    span=SPAN,
    thickness=THICKNESS,
    depth=DEPTH,
    num_blocks=NUM_BLOCKS,
    extra_support=False,
).assembly()

assembly_interfaces_numpy(assembly, nmax=10, amin=1e-2, tmax=1e-2)
cra_solve_native(assembly, mu=MU, verbose=True, timer=True)

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


blocks_layer = ensure_layer("CRA-Arch::Blocks", (0, 0, 0))
supports_layer = ensure_layer("CRA-Arch::Supports", (247, 157, 132))
interfaces_layer = ensure_layer("CRA-Arch::Interfaces", (0, 70, 139))
compression_layer = ensure_layer("CRA-Arch::Compression", (0, 120, 0))
tension_layer = ensure_layer("CRA-Arch::Tension", (200, 0, 0))

rs.EnableRedraw(False)

for node in assembly.graph.nodes():
    block = assembly.graph.node_attribute(node, "block")
    is_support = assembly.graph.node_attribute(node, "is_support")
    draw_block(block, supports_layer if is_support else blocks_layer)

max_n = 0.0
for edge in assembly.graph.edges():
    for interface in assembly.graph.edge_attribute(edge, "interfaces") or []:
        corners = list(interface.points)
        guid = rs.AddPolyline(corners + [corners[0]])
        rs.ObjectLayer(guid, interfaces_layer)

        forces = interface.forces
        if forces is None:
            continue

        # resultant force per interface, same math as compas_sandbox.viewers
        frame = interface.frame
        w, u, v = frame.zaxis, frame.xaxis, frame.yaxis
        normals = [f["c_np"] - f["c_nn"] for f in forces]
        sum_n = sum(normals)
        sum_u = sum(f["c_u"] for f in forces)
        sum_v = sum(f["c_v"] for f in forces)
        if sum_n == 0:
            continue
        max_n = max(max_n, abs(sum_n))
        pos = [sum(c[i] * n for c, n in zip(corners, normals)) / sum_n for i in range(3)]
        f = (w * sum_n + u * sum_u + v * sum_v) * 0.5 * FORCE_SCALE
        guid = rs.AddLine([pos[i] + f[i] for i in range(3)], [pos[i] - f[i] for i in range(3)])
        rs.ObjectLayer(guid, compression_layer if sum_n >= 0 else tension_layer)
        dot = rs.AddTextDot("{:.2f}".format(abs(sum_n)), pos)
        rs.ObjectLayer(dot, compression_layer if sum_n >= 0 else tension_layer)

rs.EnableRedraw(True)
rs.ZoomExtents(all=True)
for layer in (blocks_layer, supports_layer, interfaces_layer, compression_layer, tension_layer):
    print("{}: {} objects".format(layer, len(rs.ObjectsByLayer(layer) or [])))
print("Arch solved: {} blocks, max resultant normal force {:.2f}".format(assembly.graph.number_of_nodes(), max_n))
