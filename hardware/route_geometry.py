# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Trim a reported dead trace end while preserving centreline junctions.

Used only after KiCad reports a dangling track; every edit is rechecked by
KiCad. This is not a clearance checker or a replacement for zone connectivity.
"""
import math
import hashlib
import json
from .sexp import children,one,Atom


def fingerprint(doc):
    """Hash trace/via geometry without UUIDs, ordering, or number formatting."""
    copper=[]
    for track in children(doc,'segment'):
        copper.append(('track',one(track,'net')[-1],one(track,'layer')[1],
            float(one(track,'width')[1]),tuple(sorted((xy(track,'start'),xy(track,'end'))))))
    for via in children(doc,'via'):
        copper.append(('via',one(via,'net')[-1],tuple(one(via,'layers')[1:]),
            float(one(via,'size')[1]),float(one(via,'drill')[1]),xy(via,'at')))
    return hashlib.sha256(json.dumps(sorted(copper),separators=(',',':')).encode()).hexdigest()


def xy(node,key):return tuple(map(float,one(node,key)[1:3]))
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def cross(a,b):return a[0]*b[1]-a[1]*b[0]


def trim_to_junctions(doc,node):
    start,end=xy(node,'start'),xy(node,'end');direction=sub(end,start)
    length2=sum(v*v for v in direction)
    if not length2:return False
    net=one(node,'net')[-1];layer=one(node,'layer')[1];parameters=[]
    def projected(point):return sum(a*b for a,b in zip(sub(point,start),direction))/length2
    def add(value):
        if -1e-7<=value<=1+1e-7:parameters.append(max(0,min(1,value)))
    for other in children(doc,'segment'):
        if other is node or one(other,'net')[-1]!=net or one(other,'layer')[1]!=layer:continue
        a,b=xy(other,'start'),xy(other,'end');delta=sub(b,a);offset=sub(a,start)
        denominator=cross(direction,delta)
        if abs(denominator)>1e-10:
            t=cross(offset,delta)/denominator;u=cross(offset,direction)/denominator
            if -1e-7<=u<=1+1e-7:add(t)
        elif abs(cross(offset,direction))<1e-8:
            lo,hi=sorted((projected(a),projected(b)))
            if hi>=0 and lo<=1:add(max(0,lo));add(min(1,hi))
    # Pad centres are adequate for the generated escape tracks. For offset
    # attachments use a circle wholly inside the pad, then let DRC verify.
    anchors=[]
    for fp in children(doc,'footprint'):
        at=one(fp,'at');fx,fy=map(float,at[1:3]);angle=math.radians(float(at[3]) if len(at)>3 else 0)
        for pad in children(fp,'pad'):
            if not children(pad,'net') or one(pad,'net')[-1]!=net:continue
            if layer not in one(pad,'layers') and '*.Cu' not in one(pad,'layers'):continue
            x,y=xy(pad,'at');center=(fx+x*math.cos(angle)+y*math.sin(angle),fy-x*math.sin(angle)+y*math.cos(angle))
            anchors.append((center,min(map(float,one(pad,'size')[1:3]))/2))
    for via in children(doc,'via'):
        if one(via,'net')[-1]==net:anchors.append((xy(via,'at'),float(one(via,'size')[1])/2))
    for center,radius in anchors:
        t=projected(center);near=(start[0]+t*direction[0],start[1]+t*direction[1])
        if math.dist(center,near)<=radius+1e-7:add(t)
    if not parameters or max(parameters)-min(parameters)<1e-7:return False
    for key,t in [('start',min(parameters)),('end',max(parameters))]:
        one(node,key)[1:3]=[Atom(f'{start[i]+t*direction[i]:.6f}') for i in (0,1)]
    return True
