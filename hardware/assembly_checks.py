# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Conservative drill-to-paste check independent of router manufacturing flags.

An ordinary assembly order must not silently acquire filled/capped via-in-pad.
Paste rectangles are checked by their bounding boxes, including rounded corners.
This can over-report a corner overlap; it cannot approve one by rounding it away.
"""
import math
from .sexp import children,one


def via_in_paste(doc):
    pads=[]
    for fp in children(doc,'footprint'):
        ref=next(p[2] for p in children(fp,'property') if p[1]=='Reference')
        at=one(fp,'at');fx,fy=map(float,at[1:3])
        angle=math.radians(float(at[3]) if len(at)>3 else 0)
        for pad in children(fp,'pad'):
            layers=one(pad,'layers')[1:]
            if not any(layer in layers for layer in ('F.Paste','B.Paste','*.Paste')):continue
            at=one(pad,'at');x,y=map(float,at[1:3])
            center=(fx+x*math.cos(angle)+y*math.sin(angle),
                    fy-x*math.sin(angle)+y*math.cos(angle))
            orientation=math.radians(float(at[3]) if len(at)>3 else 0)
            width,height=map(float,one(pad,'size')[1:3])
            # Positive paste expansion enlarges the exclusion. Negative paste
            # shrinkage never grants permission to drill into the solder land.
            margin=max([0.0]+[float(n[1]) for n in children(pad,'solder_paste_margin')])
            pads.append((f'{ref}.{pad[1]}',center,orientation,width/2+margin,height/2+margin))
    hits=[]
    for via in children(doc,'via'):
        x,y=map(float,one(via,'at')[1:3]);radius=float(one(via,'drill')[1])/2
        for ref,(px,py),angle,hw,hh in pads:
            dx=(x-px)*math.cos(angle)-(y-py)*math.sin(angle)
            dy=(x-px)*math.sin(angle)+(y-py)*math.cos(angle)
            distance=math.hypot(max(abs(dx)-hw,0),max(abs(dy)-hh,0))
            if distance<radius-1e-6:
                hits.append({'pad':ref,'via_mm':[x,y]})
    return hits
