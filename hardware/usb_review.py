# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Measure routed USB centerlines and sample their filled L2 reference copper.

This is a geometry audit, not a field solver or USB compliance result. Pad,
package and resistor electrical lengths are not modelled.
"""
import heapq
import json
import math
from pathlib import Path
from .library import ROOT
from .sexp import parse, children, one
from .route_geometry import xy

USB_NETS={'USB_DP','USB_DM'}


def contains(point,polygon):
    """Even/odd containment, including KiCad's bridged polygon cutouts."""
    x,y=point;inside=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>y)!=(b[1]>y):
            cross_x=a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1])
            if x<cross_x:inside=not inside
    return inside


def pad_centers(doc):
    result={}
    for fp in children(doc,'footprint'):
        ref=next(p[2] for p in children(fp,'property') if p[1]=='Reference')
        at=one(fp,'at');fx,fy=map(float,at[1:3])
        angle=math.radians(float(at[3]) if len(at)>3 else 0)
        for pad in children(fp,'pad'):
            x,y=xy(pad,'at')
            result[ref,str(pad[1])]=(round(fx+x*math.cos(angle)+y*math.sin(angle),6),
                                     round(fy-x*math.sin(angle)+y*math.cos(angle),6))
    return result


def path_length(segments,start,end):
    """Centerline graph with junctions inserted at collinear endpoints."""
    points={start,end}|{xy(s,k) for s in segments for k in ('start','end')}
    graph={p:[] for p in points}
    for s in segments:
        a,b=xy(s,'start'),xy(s,'end');length=math.dist(a,b)
        if not length:continue
        ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length
        along=[]
        for p in points:
            t=(p[0]-a[0])*ux+(p[1]-a[1])*uy
            if -1e-6<=t<=length+1e-6 and abs((p[0]-a[0])*uy-(p[1]-a[1])*ux)<1e-6:
                along.append((t,p))
        along.sort()
        for (_,p),(_,q) in zip(along,along[1:]):
            distance=math.dist(p,q);graph[p].append((q,distance));graph[q].append((p,distance))
    queue=[(0,start)];best={start:0}
    while queue:
        distance,p=heapq.heappop(queue)
        if distance>best[p]:continue
        if p==end:return distance
        for q,weight in graph[p]:
            candidate=distance+weight
            if candidate<best.get(q,math.inf):best[q]=candidate;heapq.heappush(queue,(candidate,q))
    raise ValueError(f'No continuous USB centerline from {start} to {end}')


def probe_contacts(doc,tracks,pads):
    # Probe contacts must stay entirely inside a straight USB trace. This also
    # rejects a later pad enlargement that silently adds a capacitive branch.
    from .diagnostics import DIAGNOSTICS
    probes=[]
    for d in DIAGNOSTICS:
        if d.part!='USB_PROBE':continue
        fp=next(f for f in children(doc,'footprint') if any(
            p[1:3]==['Reference',d.ref] for p in children(f,'property')))
        pad=one(fp,'pad');cx,cy=pads[d.ref,'1']
        width,height=map(float,one(pad,'size')[1:3])
        if (one(fp,'layer')[1]!='F.Cu' or one(pad,'net')[-1]!=d.net
            or set(one(pad,'layers')[1:])!={'F.Cu','F.Mask'}
            or len(one(fp,'at'))>3 and float(one(fp,'at')[3])%360):
            raise ValueError('USB probe must be an unrotated, paste-free front contact')
        fitting=[t for t in tracks if one(t,'net')[-1]==d.net
                 and abs(xy(t,'start')[1]-cy)<1e-6 and abs(xy(t,'end')[1]-cy)<1e-6
                 and min(xy(t,'start')[0],xy(t,'end')[0])<=cx-width/2
                 and max(xy(t,'start')[0],xy(t,'end')[0])>=cx+width/2
                 and height<=float(one(t,'width')[1])+1e-6]
        if not fitting:raise ValueError(f'USB probe adds copper outside existing trace: {d.ref}')
        probes.append({'ref':d.ref,'net':d.net,'size_mm':[width,height],
                       'inline_without_branch_or_via':True})
    return probes


def report(board):
    doc=parse(Path(board).read_text());pads=pad_centers(doc)
    tracks=[s for s in children(doc,'segment') if one(s,'net')[-1] in USB_NETS]
    wrong_layers=[one(s,'layer')[1] for s in tracks if one(s,'layer')[1]!='F.Cu']
    vias=[xy(v,'at') for v in children(doc,'via') if one(v,'net')[-1] in USB_NETS]
    if wrong_layers or vias:raise ValueError('USB must remain on F.Cu without vias')
    probes=probe_contacts(doc,tracks,pads)
    polygons=[]
    for zone in children(doc,'zone'):
        if children(zone,'keepout') or one(zone,'net')[-1]!='GND':continue
        for poly in children(zone,'filled_polygon'):
            if one(poly,'layer')[1]=='In1.Cu':
                polygons.append([tuple(map(float,p[1:3])) for p in children(one(poly,'pts'),'xy')])
    if not polygons:raise ValueError('No filled In1.Cu ground reference')
    missing=[];samples=0
    for s in tracks:
        a,b=xy(s,'start'),xy(s,'end');length=math.dist(a,b)
        if not length:continue
        radius=float(one(s,'width')[1])/2;nx,ny=-(b[1]-a[1])/length,(b[0]-a[0])/length
        steps=math.ceil(length/.05)
        for i in range(steps+1):
            for offset in (-radius,0,radius):
                p=(a[0]+(b[0]-a[0])*i/steps+nx*offset,a[1]+(b[1]-a[1])*i/steps+ny*offset)
                samples+=1
                if not any(contains(p,polygon) for polygon in polygons):
                    missing.append({'net':one(s,'net')[-1],'point_mm':[round(v,6) for v in p]})
    paths={}
    for suffix,mcu,contacts in [('DP','33',('A6','B6')),('DM','32',('A7','B7'))]:
        segments=[s for s in tracks if one(s,'net')[-1]=='USB_'+suffix]
        paths[suffix]={'connector_to_mcu_mm':{pin:round(path_length(segments,pads['J2',pin],pads['U1',mcu]),4)
                       for pin in contacts}}
    paths['BOOT']={'resistor':'R12', 'series_resistance_ohm':4700,
                   'note':'Only the short D+ to R12 branch is part of the USB signal net; button wire is isolated by R12.'}
    return {'status':'geometry audit; impedance and USB performance not certified',
        'probe_contacts':probes,'all_usb_tracks_on_F_Cu':not wrong_layers,'usb_vias':len(vias),'paths':paths,
        'ground_reference_sampling':{'layer':'In1.Cu','net':'GND','longitudinal_step_max_mm':.05,
            'transverse_samples':'trace center and both edges','sample_count':samples,
            'uncovered_sample_count':len(missing),'uncovered_samples':missing},
        'limitations':['Sampling does not prove continuous copper coverage between samples or adequate lateral return width.',
            'Centerline lengths exclude package, pad spreading and resistor electrical length.',
            'Connector, ESD, BOOT branch and MCU fanouts are not uniform differential transmission lines.',
            'The JLC calculator describes a uniform pair only; assembled-board USB validation remains required.']}


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('board',nargs='?',default=str(ROOT/'hardware/review/ch32-pico.kicad_pcb'))
    args=parser.parse_args();result=report(args.board)
    out=ROOT/'build/usb-review.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if result['ground_reference_sampling']['uncovered_sample_count']:raise SystemExit('USB ground-reference sampling failed')


if __name__=='__main__':main()
