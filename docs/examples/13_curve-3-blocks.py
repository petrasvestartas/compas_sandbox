"""Example to calculate three block with curved interfaces"""

import os

import compas

import compas_sandbox
from compas_sandbox.datastructures import CRA_Assembly
from compas_sandbox.equilibrium import cra_solve
from compas_sandbox.viewers import cra_view

density = 1

FILE_I = os.path.join(compas_sandbox.SAMPLE, "curve-3-blocks.json")

assembly = compas.json_load(FILE_I)
assembly: CRA_Assembly = assembly.copy(cls=CRA_Assembly)
assembly.set_boundary_conditions([0])

cra_solve(assembly, verbose=True, timer=True, density=density)
cra_view(
    assembly,
    resultant=False,
    nodal=True,
    grid=True,
    displacements=True,
    dispscale=0,
    scale=1,
    density=density,
)
