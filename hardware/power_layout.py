# SPDX-License-Identifier: MIT
"""Revs C/D/E geometry gates for the local buck loop and feedback connection.

These reject layout regressions, not thermal, EMC or stability failures.
"""
import math
from pathlib import Path
from .sexp import parse, children, one
from .usb_review import pad_centers, path_length, contains


def ground_returns(doc):
    """Require two local through-vias reached by at least 0.4 mm top copper."""
    pads=pad_centers(doc)
    tracks=[s for s in children(doc,'segment') if one(s,'net')[-1]=='GND'
            and one(s,'layer')[1]=='F.Cu' and float(one(s,'width')[1])>=.4]
    vias={tuple(map(float,one(v,'at')[1:3])) for v in children(doc,'via')
          if one(v,'net')[-1]=='GND' and one(v,'layers')[1:]==['F.Cu','B.Cu']}
    result={}
    for ref,pin in (('C12','2'),('D5','7'),('D6','7')):
        paths=[]
        for via in sorted(vias):
            if math.dist(pads[ref,pin],via)>2.5:continue
            try:distance=path_length(tracks,pads[ref,pin],via)
            except ValueError:continue
            if distance<=2.5:paths.append({'via_mm':list(via),'path_mm':round(distance,4)})
        if len(paths)<2:raise ValueError(f'{ref} needs two local ground vias with wide top-layer returns')
        result[ref]=paths
    return result


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
                        and one(s,'layer')[1]=='F.Cu'],pads['U3','9'],pads['C8','1'])
    if timing>5:raise ValueError('Load-switch timing capacitor is not locally connected')
    local={}
    for net,pin,ref,budget in (('PD_ILM','10','R17',3),('PD_IMON','13','R25',4)):
        distance=path_length([s for s in tracks if one(s,'net')[-1]==net
                             and one(s,'layer')[1]=='F.Cu'],pads['U3',pin],pads[ref,'1'])
        if distance>budget:raise ValueError(f'{net} programming/monitor resistor is not locally connected')
        local[net]=round(distance,3)

    sense=(5.6,23.5)
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
    from .design import BOARD_REVISION
    returns=ground_returns(doc) if BOARD_REVISION=='E' else {}
    return {'input_capacitor_connections_mm':loops,'switch_copper_total_mm':round(length,3),
            'local_ground_returns':returns,
            'load_switch_timing_connection_mm':round(timing,3),'local_programming_paths_mm':local,
            'supply_trace_totals_mm':totals,'feedback_via_isolated_from_shared_plane':True,
            'passes':True,'limitations':'Geometry only; current, temperature, ripple and EMC require hardware testing'}


def report(path):return audit(parse(Path(path).read_text()))
