# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Add deterministic plane outlines without editing any source copper.

KiCad's DRC command fills them afterward. No router cleanup or project-rule
writeback is needed merely to create two plane polygons.
"""
from .sexp import parse, children, dump
from .schematic import uid
from .fabrication import copy_rules
from .design import MECHANICAL
from .design import BOARD_REVISION


def add_planes(source, output):
    doc=parse(source.read_text())
    if any(not children(z,'keepout') for z in children(doc,'zone')):
        raise ValueError('Plane input already contains copper zones')
    planes=[('GND','In1.Cu',MECHANICAL.length-.3),('3V3_OUT','In2.Cu',MECHANICAL.length-.3)]
    if BOARD_REVISION=='B':
        # Additional outer-layer return for the connector/output region.
        # The uninterrupted L2 reference remains the primary USB return.
        planes.append(('GND','B.Cu',12.0))
    for net,layer,bottom in planes:
        doc.append(parse(f'''(zone (net "{net}") (layer "{layer}")
          (uuid "{uid('plane/'+net+'/'+layer)}") (hatch edge 0.5)
          (connect_pads yes (clearance 0.2)) (min_thickness 0.1)
          (fill yes (thermal_gap 0.2) (thermal_bridge_width 0.2) (island_removal_mode 0))
          (polygon (pts (xy 0.3 0.3) (xy {MECHANICAL.width-.3} 0.3)
            (xy {MECHANICAL.width-.3} {bottom})
            (xy 0.3 {bottom}))))'''))
    output.write_text(dump(doc)+'\n')
    copy_rules(source,output)
