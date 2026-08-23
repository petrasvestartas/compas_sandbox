"""Example to calculate cube short with curved interfaces"""

import os

import compas

import compas_sandbox
from compas_sandbox.datastructures import CRA_Assembly
from compas_sandbox.equilibrium import cra_solve
from compas_sandbox.viewers import cra_view

density = 0.1

FILE_I = os.path.join(compas_sandbox.SAMPLE, "cube-curve-short.json")

assembly = compas.json_load(FILE_I)
assembly: CRA_Assembly = assembly.copy(cls=CRA_Assembly)
assembly.set_boundary_conditions([0])

cra_solve(assembly, verbose=True, timer=True, density=density)
cra_view(
    assembly,
    resultant=True,
    nodal=False,
    grid=True,
    displacements=True,
    dispscale=0,
    scale=50,
    density=density,
)
