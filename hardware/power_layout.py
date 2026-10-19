# SPDX-License-Identifier: MIT
"""Geometry gates for the buck loop, feedback, VBUS clamp, pin 40 trunk and ground returns.

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
    for ref,pin in (('D5','7'),):
        paths=[]
        for via in sorted(vias):
            if math.dist(pads[ref,pin],via)>2.5:continue
            try:distance=path_length(tracks,pads[ref,pin],via)
            except ValueError:continue
            if distance<=2.5:paths.append({'via_mm':list(via),'path_mm':round(distance,4)})
        if len(paths)<2:raise ValueError(f'{ref} needs two local ground vias with wide top-layer returns')
        result[ref]=paths
    return result


def vbus_connections(doc):
    """Bound the clamp loop and require the wide pin 40 trunk."""
    pads=pad_centers(doc)
    tracks=children(doc,'segment')
    copper=[s for s in tracks if one(s,'net')[-1]=='VBUS' and one(s,'layer')[1]=='F.Cu']
    try:clamp=path_length(copper,pads['J2','B4A9'],pads['D5','4'])
    except ValueError as error:raise ValueError('input_clamp needs a direct top-layer connection') from error
    if clamp>6:raise ValueError('input_clamp connection exceeds 6 mm')
    trunk=[s for s in tracks if one(s,'net')[-1]=='VBUS' and one(s,'layer')[1]=='B.Cu'
           and float(one(s,'width')[1])>=1.2]
    from .design import MECHANICAL
    try:header=path_length(trunk,(12.9,7.85),MECHANICAL.position(40))
    except ValueError as error:raise ValueError('Header pin 40 needs the 1.2 mm VBUS trunk') from error
    if header>16:raise ValueError('Header pin 40 VBUS trunk exceeds 16 mm')
    front=[s for s in tracks if one(s,'net')[-1]=='VBUS' and one(s,'layer')[1]=='F.Cu'
           and float(one(s,'width')[1])>=.4]
    try:feed=path_length(front,pads['J2','A4B9'],MECHANICAL.position(40))
    except ValueError as error:raise ValueError('Header pin 40 needs the front-layer VBUS feed') from error
    if feed>16:raise ValueError('Header pin 40 front VBUS feed exceeds 16 mm')
    return {'input_clamp_mm':round(clamp,4),'header_pin40_trunk_mm':round(header,4),
            'header_pin40_front_feed_mm':round(feed,4)}


def _reachable(segments,start,end):
    try:path_length(segments,start,end);return True
    except ValueError:return False


def audit(doc):
    pads=pad_centers(doc)
    tracks=children(doc,'segment')
    loops={}
    copper=[s for s in tracks if one(s,'net')[-1]=='VIN_SYS' and one(s,'layer')[1]=='F.Cu']
    length=path_length(copper,pads['C1','1'],pads['U4','5'])
    if length>5:raise ValueError('Buck input-capacitor VIN_SYS connection exceeds 5 mm')
    loops['VIN_SYS']=round(length,4)
    # IN and GND are on opposite sides of the SOT-23-6, so the return closes
    # through the ground plane: both capacitor and IC ground need a via close by.
    gnd=[s for s in tracks if one(s,'net')[-1]=='GND' and one(s,'layer')[1]=='F.Cu']
    vias={tuple(map(float,one(v,'at')[1:3])) for v in children(doc,'via') if one(v,'net')[-1]=='GND'}
    for ref,pin in (('C1','2'),('U4','2')):
        near=[v for v in vias if math.dist(pads[ref,pin],v)<=2.0]
        if not any(path_length(gnd,pads[ref,pin],v)<=2.0 for v in near if _reachable(gnd,pads[ref,pin],v)):
            raise ValueError(f'{ref}.{pin} needs a ground via within 2 mm of front copper')
        loops[f'{ref}.{pin}_ground_via_mm']=round(min(path_length(gnd,pads[ref,pin],v) for v in near if _reachable(gnd,pads[ref,pin],v)),4)
    if any(one(v,'net')[-1] in ('BUCK_SW','BUCK_BST') for v in children(doc,'via')):
        raise ValueError('Buck switch/bootstrap loop must not acquire vias')
    sw=[s for s in tracks if one(s,'net')[-1]=='BUCK_SW']
    length=sum(math.dist(tuple(map(float,one(s,'start')[1:3])),
                        tuple(map(float,one(s,'end')[1:3]))) for s in sw)
    if length>8 or any(one(s,'layer')[1]!='F.Cu' for s in sw):
        raise ValueError('Buck switch copper exceeds its local top-layer budget')
    sense=(3.6,20.0)
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
    returns=ground_returns(doc)
    vbus=vbus_connections(doc)
    polygons=[[tuple(map(float,p[1:3])) for p in children(one(poly,'pts'),'xy')]
              for z in children(doc,'zone') if not children(z,'keepout') and one(z,'net')[-1]=='GND'
              for poly in children(z,'filled_polygon') if one(poly,'layer')[1]=='In1.Cu']
    local_vias={tuple(p['via_mm']) for paths in returns.values() for p in paths}
    if polygons and any(not any(contains(via,poly) for poly in polygons) for via in local_vias):
        raise ValueError('A local return via is outside the filled ground plane')
    return {'input_capacitor_connections_mm':loops,'switch_copper_total_mm':round(length,3),
            'local_ground_returns':returns,
            'vbus_connections':vbus,
            'local_return_via_count':len(local_vias),'local_return_ground_plane_checked':bool(polygons),
            'supply_trace_totals_mm':totals,'feedback_via_isolated_from_shared_plane':True,
            'passes':True,'limitations':'Geometry only; current, temperature, ripple and EMC require hardware testing'}


def report(path):return audit(parse(Path(path).read_text()))
