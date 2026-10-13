# SPDX-License-Identifier: MIT
"""Rev C geometry gates for the local buck loop and feedback connection.

These reject layout regressions, not thermal, EMC or stability failures.
"""
import math
from pathlib import Path
from .sexp import parse, children, one
from .usb_review import pad_centers, path_length, contains


def audit(doc):
    pads=pad_centers(doc)
    tracks=children(doc,'segment')
    loops={}
    for net,cap,terminal in (('VIN_SYS','1','3'),('GND','2','4')):
        copper=[s for s in tracks if one(s,'net')[-1]==net and one(s,'layer')[1]=='F.Cu']
        length=path_length(copper,pads['C1',cap],pads['U4',terminal])
        if length>2:raise ValueError(f'Buck input-capacitor {net} connection exceeds 2 mm')
        loops[net]=round(length,4)
    if any(one(v,'net')[-1] in ('BUCK_SW','BUCK_BST') for v in children(doc,'via')):
        raise ValueError('Buck switch/bootstrap loop must not acquire vias')
    sw=[s for s in tracks if one(s,'net')[-1]=='BUCK_SW']
    length=sum(math.dist(tuple(map(float,one(s,'start')[1:3])),
                        tuple(map(float,one(s,'end')[1:3]))) for s in sw)
    if length>8 or any(one(s,'layer')[1]!='F.Cu' for s in sw):
        raise ValueError('Buck switch copper exceeds its local top-layer budget')
    timing=path_length([s for s in tracks if one(s,'net')[-1]=='PD_DVDT'
                        and one(s,'layer')[1]=='F.Cu'],pads['U3','7'],pads['C8','1'])
    if timing>5:raise ValueError('Load-switch timing capacitor is not locally connected')
    sense=(5.05,13.75)
    if not any(one(v,'net')[-1]=='3V3_OUT' and tuple(map(float,one(v,'at')[1:3]))==sense
               for v in children(doc,'via')):raise ValueError('Missing dedicated feedback via')
    for z in children(doc,'zone'):
        if children(z,'keepout') or one(z,'net')[-1]!='3V3_OUT':continue
        for poly in children(z,'filled_polygon'):
            points=[tuple(map(float,p[1:3])) for p in children(one(poly,'pts'),'xy')]
            if one(poly,'layer')[1]=='In2.Cu' and contains(sense,points):
                raise ValueError('Shared 3V3 plane bypasses the dedicated feedback trace')
    totals={}
    for net in ('VSYS','VIN_SYS'):
        totals[net]=round(sum(math.dist(tuple(map(float,one(s,'start')[1:3])),
                                       tuple(map(float,one(s,'end')[1:3])))
                              for s in tracks if one(s,'net')[-1]==net),3)
    return {'input_capacitor_connections_mm':loops,'switch_copper_total_mm':round(length,3),
            'load_switch_timing_connection_mm':round(timing,3),
            'supply_trace_totals_mm':totals,'feedback_via_isolated_from_shared_plane':True,
            'passes':True,'limitations':'Geometry only; current, temperature, ripple and EMC require hardware testing'}


def report(path):return audit(parse(Path(path).read_text()))
