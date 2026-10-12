# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Independent check that routing preserves the locked critical copper.

Electrical DRC can pass after a router moves a power path onto a ground plane.
Compare the layer, net, width and covered centerline against the seed board.
Collinear splitting/merging is allowed; a layer change is not.
"""
import math
from .sexp import children, one


def geometry(segment):
    a=tuple(map(float,one(segment,'start')[1:3]))
    b=tuple(map(float,one(segment,'end')[1:3]))
    return a,b,float(one(segment,'width')[1]),one(segment,'layer')[1],one(segment,'net')[-1]


def unpreserved_segments(seed,board):
    actual=[geometry(s) for s in children(board,'segment')]
    missing=[]
    for segment in children(seed,'segment'):
        if not children(segment,'locked'):continue
        a,b,width,layer,net=geometry(segment)
        length=math.dist(a,b)
        if length<1e-6:continue
        ux,uy=((b[i]-a[i])/length for i in range(2))
        intervals=[]
        for c,d,w,side,name in actual:
            if side!=layer or name!=net or w<width-1e-6:continue
            if any(abs((p[0]-a[0])*uy-(p[1]-a[1])*ux)>1e-5 for p in (c,d)):continue
            interval=sorted((p[0]-a[0])*ux+(p[1]-a[1])*uy for p in (c,d))
            intervals.append(interval)
        end=0.0
        for lo,hi in sorted(intervals):
            if lo>end+1e-5:break
            end=max(end,hi)
        if end<length-1e-5:
            missing.append({'net':net,'layer':layer,'width_mm':width,'start_mm':a,'end_mm':b})
    return missing


def unpreserved_vias(seed,board):
    """Keep the specified drill, annulus and layer span of locked power vias."""
    def geometry(via):
        return (one(via,'net')[-1],tuple(round(float(v),6) for v in one(via,'at')[1:3]),
            round(float(one(via,'size')[1]),6),round(float(one(via,'drill')[1]),6),
            tuple(one(via,'layers')[1:]))
    actual={geometry(via) for via in children(board,'via')}
    return [{'net':net,'at_mm':at,'diameter_mm':diameter,'drill_mm':drill,'layers':layers}
        for net,at,diameter,drill,layers in
        (geometry(via) for via in children(seed,'via') if children(via,'locked'))
        if (net,at,diameter,drill,layers) not in actual]
