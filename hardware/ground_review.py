# SPDX-License-Identifier: MIT
"""Bound the reviewed GPIO crossover and verify the refilled ground plane.

L2 remains the USB reference. The single PA17 escape is confined below the
MCU, away from the USB and power stage; arbitrary L2 signal routing is rejected.
These are geometric checks, not an EMC qualification.
"""
import math
from .sexp import children, one
from .usb_review import contains, path_length


def crossovers(doc):
    tracks=[n for n in children(doc,'segment')
            if one(n,'layer')[1]=='In1.Cu' and one(n,'net')[-1]!='GND']
    if not tracks:return []
    for track in tracks:
        if one(track,'net')[-1]!='PA17':
            raise ValueError('Unreviewed signal on the ground layer')
        if abs(float(one(track,'width')[1])-.15)>1e-6:
            raise ValueError('Ground-layer crossover must remain 0.15 mm wide')
        for key in ('start','end'):
            x,y=map(float,one(track,key)[1:3])
            if not (1.5<=x<=8.9 and 36.7<=y<=37.2):
                raise ValueError('Ground-layer crossover leaves its reviewed corridor')
    length=sum(math.dist(tuple(map(float,one(t,'start')[1:3])),
                         tuple(map(float,one(t,'end')[1:3]))) for t in tracks)
    if length>7.4:raise ValueError('Ground-layer crossover exceeds its length budget')
    distance=path_length(tracks,(8.7329,37.0378),(1.61,36.93))
    if abs(distance-length)>1e-5:
        raise ValueError('Ground-layer crossover must be a single unbranched path')
    return [{'net':'PA17','length_mm':round(length,4),'width_mm':.15,
             'corridor_mm':[1.5,36.7,8.9,37.2]}]


def audit(doc):
    signals=crossovers(doc)
    polygons=[[tuple(map(float,p[1:3])) for p in children(one(poly,'pts'),'xy')]
              for zone in children(doc,'zone')
              if not children(zone,'keepout') and one(zone,'net')[-1]=='GND'
              for poly in children(zone,'filled_polygon')
              if one(poly,'layer')[1]=='In1.Cu']
    vias=[tuple(map(float,one(v,'at')[1:3])) for v in children(doc,'via')
          if one(v,'net')[-1]=='GND']
    if not polygons or not vias:
        raise ValueError('Ground continuity review requires a filled plane and ground vias')
    if not any(all(contains(via,polygon) for via in vias) for polygon in polygons):
        raise ValueError('Ground vias do not all reach one connected L2 fill polygon')
    return {'signal_crossovers':signals,'ground_via_count':len(vias),
            'all_ground_vias_on_one_fill_polygon':True,
            'passes':True,'limitations':'Geometry only; USB reference is checked separately; EMC requires hardware'}
