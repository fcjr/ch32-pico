# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Generate the placed PCB using KiCad's Python, then exit normally.

No routing subprocesses or timeouts are started here. Outputs are candidates,
never fabrication releases. Schematic and PCB share the same circuit source.
"""
import json
import shutil
import wx
import pcbnew as k
from .circuit import COMPONENTS
from .library import ROOT, LIBDIR, load_library, validate_library
from .placement import PLACEMENT
from .design import MECHANICAL
from .schematic import uid
from .sexp import parse, children, one, dump


def point(x,y): return k.VECTOR2I(round(x*1_000_000),round(y*1_000_000))


def generate():
    library=load_library()
    validate_library(COMPONENTS,library)
    physical=[c for c in COMPONENTS if not c.ref.startswith('#')]
    if set(PLACEMENT)!={c.ref for c in physical}: raise ValueError('Placement coverage mismatch')
    app=wx.App(False)
    board=k.BOARD()
    board.SetCopperLayerCount(4)
    settings=board.GetDesignSettings()
    settings.SetBoardThickness(k.FromMM(MECHANICAL.thickness))
    settings.m_MinClearance=k.FromMM(0.15)
    settings.m_TrackMinWidth=k.FromMM(0.15)
    settings.m_ViasMinSize=k.FromMM(0.45)
    settings.m_MinThroughDrill=k.FromMM(0.2)
    nets={}
    for name in sorted({net for c in physical for net in c.nets.values() if net is not None}):
        net=k.NETINFO_ITEM(board,name)
        board.Add(net); nets[name]=net
    for c in physical:
        part=library[c.part]
        fp=k.FootprintLoad(str(LIBDIR/'ch32-pico.pretty'),part.footprint)
        if fp is None: raise ValueError(f'Cannot load {part.footprint}')
        fp.SetReference(c.ref)
        fp.SetValue(c.value or part.mpn)
        fp.SetFPID(k.LIB_ID('ch32-pico',part.footprint))
        x,y,*rotation=PLACEMENT[c.ref]
        fp.SetPosition(point(x,y))
        fp.SetOrientationDegrees(rotation[0] if rotation else 0)
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        for item in fp.GraphicalItems():
            # Imported %R user text can cover pins even when Reference is hidden.
            if item.GetLayer()==k.F_SilkS: item.SetLayer(k.F_Fab)
            if isinstance(item,k.PCB_TEXT): item.SetVisible(False)
        if not c.fitted:
            fp.SetAttributes(fp.GetAttributes() | k.FP_EXCLUDE_FROM_BOM | k.FP_EXCLUDE_FROM_POS_FILES)
        board.Add(fp)
        for pad in fp.Pads():
            number=pad.GetNumber()
            if number and c.nets[number] is not None: pad.SetNet(nets[c.nets[number]])
    corners=[(0,0),(21,0),(21,51),(0,51)]
    for i,(a,b) in enumerate(zip(corners,corners[1:]+corners[:1])):
        edge=k.PCB_SHAPE(board); edge.SetShape(k.SHAPE_T_SEGMENT)
        edge.SetStart(point(*a)); edge.SetEnd(point(*b)); edge.SetLayer(k.Edge_Cuts)
        edge.SetWidth(k.FromMM(0.05)); board.Add(edge)
    out=ROOT/'build/ch32-pico-placed.kicad_pcb'
    board.SetFileName(str(out))
    k.SaveBoard(str(out),board)
    # KiCad exposes read-only UUID handles. Normalize the saved document,
    # instead of mutating native ownership pointers.
    doc=parse(out.read_text())
    one(doc,'setup').append(parse('''(stackup
      (layer "F.Cu" (type "copper") (thickness 0.035))
      (layer "dielectric 1" (type "prepreg") (thickness 0.0994) (material "3313 RC57%") (epsilon_r 4.1) (loss_tangent 0.02))
      (layer "In1.Cu" (type "copper") (thickness 0.0152))
      (layer "dielectric 2" (type "core") (thickness 0.7) (material "NP-155F") (epsilon_r 4.53) (loss_tangent 0.02))
      (layer "In2.Cu" (type "copper") (thickness 0.0152))
      (layer "dielectric 3" (type "prepreg") (thickness 0.0994) (material "3313 RC57%") (epsilon_r 4.1) (loss_tangent 0.02))
      (layer "B.Cu" (type "copper") (thickness 0.035))
      (copper_finish "ENIG") (dielectric_constraints yes))'''))
    def signature(node):
        if not isinstance(node,list): return node
        return [signature(v) for v in node if not (isinstance(v,list) and v[0]=='uuid')]
    def order(node):
        for child in node:
            if isinstance(child,list): order(child)
        if node[0] not in ('kicad_pcb','footprint'): return
        for kind in ('footprint','pad','fp_line','fp_circle','fp_arc','fp_text','gr_text','gr_line'):
            indices=[i for i,v in enumerate(node) if isinstance(v,list) and v[0]==kind]
            values=sorted((node[i] for i in indices),key=lambda v:json.dumps(signature(v)))
            for i,v in zip(indices,values): node[i]=v
    order(doc)
    def stable(node,path):
        for i,child in enumerate(node):
            if not isinstance(child,list): continue
            if child[0]=='uuid': child[1]=uid(path)
            else: stable(child,path+'/'+str(child[0])+'/'+str(i))
    for i,node in enumerate(doc):
        if not isinstance(node,list): continue
        if node[0]=='footprint':
            ref=next(p[2] for p in children(node,'property') if p[1]=='Reference')
            stable(node,'component/'+ref)
        else: stable(node,'board/'+str(i))
    from .branding import apply as apply_branding
    apply_branding(doc)
    from .markings import apply as apply_markings
    apply_markings(doc)
    out.write_text(dump(doc)+'\n')
    project={'board':{'design_settings':{'rules':{
        'min_clearance':0.15,'min_track_width':0.15,'min_via_diameter':0.45,
        'min_via_drill':0.2,'min_through_hole_diameter':0.2,'min_via_annular_width':0.075,'min_hole_clearance':0.2,
        'min_hole_to_hole':0.25,'min_copper_edge_clearance':0.3}}},
        'net_settings':{'classes':[{'name':'Default','clearance':0.15,'track_width':0.15,
            'via_diameter':0.45,'via_drill':0.2,'diff_pair_width':0.15,'diff_pair_gap':0.15}],
            'netclass_assignments':{},'netclass_patterns':[]},
        'kicad_routing_tools':{'same_net_pad_clearance':0.1}}
    out.with_suffix('.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
    shutil.copyfile(ROOT/'hardware/fabrication.kicad_dru',out.with_suffix('.kicad_dru'))
    print(f'Wrote placed candidate: {out}')


if __name__=='__main__': generate()
