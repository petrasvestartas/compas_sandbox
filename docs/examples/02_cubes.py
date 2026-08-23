"""Simple example to calculate three stacked cubes"""

import os

import compas

import compas_sandbox
from compas_sandbox.algorithms import assembly_interfaces_numpy
from compas_sandbox.datastructures import CRA_Assembly
from compas_sandbox.equilibrium import cra_solve
from compas_sandbox.viewers import cra_view

FILE_I = os.path.join(compas_sandbox.SAMPLE, "cubes.json")

assembly = compas.json_load(FILE_I)
assembly: CRA_Assembly = assembly.copy(cls=CRA_Assembly)
assembly.set_boundary_conditions([0])

assembly_interfaces_numpy(assembly, nmax=10, amin=1e-2, tmax=1e-2)

cra_solve(assembly, verbose=True, timer=True)

cra_view(
    assembly,
    resultant=False,
    nodal=True,
    grid=True,
    displacements=True,
    dispscale=0,
    scale=0.5,
)
