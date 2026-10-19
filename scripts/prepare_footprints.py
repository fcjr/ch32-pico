# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""One-time vendoring of selected KiCad 10 footprints and local pin aliases.

Normal builds use the checked-in results, not the workstation's library.
Run deliberately after reviewing any upstream library update.
"""
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hardware.sexp import parse,children,one,dump,Atom

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
DEST=ROOT/'hardware/lib/ch32-pico.pretty'
PARTS={'SOT-23-6':'Package_TO_SOT_SMD', 'TSSOP-20_4.4x6.5mm_P0.65mm':'Package_SO', 'LQFP-48_7x7mm_P0.5mm':'Package_QFP'}
ALIASES={'C7519':'SOT-23-6', 'C29779902':'LQFP-48_7x7mm_P0.5mm', 'C5187096':'TSSOP-20_4.4x6.5mm_P0.65mm'}


def main():
    for name,folder in PARTS.items():
        node=parse((SOURCE/(folder+'.pretty')/(name+'.kicad_mod')).read_text())
        node[:]=[v for v in node if not isinstance(v,list) or v[0]!='model']
        (DEST/(name+'.kicad_mod')).write_text(dump(node)+'\n')
    sym_path=ROOT/'hardware/lib/ch32-pico.kicad_sym'
    symbols=parse(sym_path.read_text())
    for s in children(symbols,'symbol'):
        props={p[1]:p for p in children(s,'property')}
        code=props['LCSC Part'][2]
        if code in ALIASES: props['Footprint'][2]='ch32-pico:'+ALIASES[code]
    sym_path.write_text(dump(symbols)+'\n')
    # Imported models were not downloaded. Remove all dangling 3D references.
    for path in DEST.glob('*.kicad_mod'):
        node=parse(path.read_text())
        node[:]=[v for v in node if not (isinstance(v,list) and v[0]=='model')]
        # Imported legends intrude on fine-pitch pads. Retain the drawings on
        # fabrication layers and add board-specific legends in the generator.
        def fabrication_layers(item):
            if not isinstance(item,list): return
            if item and item[0]=='layer' and item[1]=='F.SilkS': item[1]='F.Fab'
            for child in item: fabrication_layers(child)
        fabrication_layers(node)
        rebuild_courtyard(node,path.stem)
        path.write_text(dump(node)+'\n')


GRAPHICS=('fp_line','fp_circle','fp_arc','fp_rect','fp_poly')


def rebuild_courtyard(node,name):
    # EasyEDA exports draw the package body on F.CrtYd, so KiCad's courtyard
    # check never sees the pads. Keep that outline as the body on F.Fab and
    # draw a courtyard around pads and body with IPC nominal excess.
    def points(item):
        out=[]
        if isinstance(item,list):
            if item and item[0] in ('start','end','xy','center'): out.append((float(item[1]),float(item[2])))
            for child in item: out+=points(child)
        return out
    def layer(item): return one(item,'layer')[1] if children(item,'layer') else None
    xs=[];ys=[]
    for pad in children(node,'pad'):
        at=one(pad,'at');x,y=float(at[1]),float(at[2]);w,h=map(float,one(pad,'size')[1:3])
        if abs(math.sin(math.radians(float(at[3]) if len(at)>3 else 0)))>.5: w,h=h,w
        xs+=[x-w/2,x+w/2];ys+=[y-h/2,y+h/2]
    graphics=[item for item in node if isinstance(item,list) and item[0] in GRAPHICS and layer(item)=='F.CrtYd']
    body=[p for item in graphics for p in points(item)]
    if not xs or not body or any(item[0]!='fp_line' for item in graphics): return
    box=(min(p[0] for p in body),min(p[1] for p in body),max(p[0] for p in body),max(p[1] for p in body))
    if box[0]<=min(xs) and box[1]<=min(ys) and box[2]>=max(xs) and box[3]>=max(ys): return
    for item in graphics:
        for i,child in enumerate(item):
            if isinstance(child,list) and child[0]=='layer': item[i]=[Atom('layer'),Atom('F.Fab')]
            if isinstance(child,list) and child[0]=='width': item[i]=[Atom('width'),Atom('0.1')]
    margin=0.15 if '0402' in name else 0.25
    x0,y0=min(min(xs),box[0])-margin,min(min(ys),box[1])-margin
    x1,y1=max(max(xs),box[2])+margin,max(max(ys),box[3])+margin
    corners=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    for a,b in zip(corners,corners[1:]+corners[:1]):
        node.append([Atom('fp_line'),[Atom('start'),Atom(f'{round(a[0],3):g}'),Atom(f'{round(a[1],3):g}')],
                     [Atom('end'),Atom(f'{round(b[0],3):g}'),Atom(f'{round(b[1],3):g}')],
                     [Atom('layer'),Atom('F.CrtYd')],[Atom('width'),Atom('0.05')]])


if __name__=='__main__': main()
