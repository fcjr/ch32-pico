# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Placement-only gate: all DRC violations fail; unrouted count is reported.

A passing placement gate does not imply electrical connectivity or readiness
for manufacture. The routed release gate must require zero unrouted items.
"""
import json
import math
from .library import ROOT,load_library
from .circuit import COMPONENTS
from .placement import PLACEMENT
from .design import MECHANICAL
from .sexp import parse,children,one
from .mechanical_checks import usb_fit


def verify_board(path):
    doc=parse(path.read_text())
    wanted={c.ref:c for c in COMPONENTS if not c.ref.startswith('#')}
    observed={}
    for fp in children(doc,'footprint'):
        ref=next(p[2] for p in children(fp,'property') if p[1]=='Reference')
        if ref in observed: raise ValueError(f'Duplicate PCB reference {ref}')
        c=wanted[ref]
        pads={}
        for pad in children(fp,'pad'):
            if not pad[1]: continue
            nets=children(pad,'net')
            net=nets[0][-1] if nets else None
            # Thermal lands can share a pad number, but not disagree on net.
            if pad[1] in pads and pads[pad[1]]!=net: raise ValueError(f'{ref}: inconsistent repeated pad')
            pads[pad[1]]=net
        if pads!=c.nets: raise ValueError(f'{ref}: PCB pad nets differ from circuit source')
        position=list(map(float,one(fp,'at')[1:]))
        x,y,*angle=position
        px,py,*pa=PLACEMENT[ref]
        if not (math.isclose(x,px,abs_tol=1e-6) and math.isclose(y,py,abs_tol=1e-6)) or ((angle[0] if angle else 0)-(pa[0] if pa else 0))%360:
            raise ValueError(f'{ref}: PCB placement differs from source')
        observed[ref]=fp
    if set(observed)!=set(wanted): raise ValueError('PCB component coverage differs from source')
    header=observed['J1']
    edge_pads=[p for p in children(header,'pad') if any(
        prop[1]=='pad_prop_castellated' for prop in children(p,'property'))]
    if len(edge_pads)!=40 or {p[1] for p in edge_pads}!={str(i) for i in range(1,41)}:
        raise ValueError('Pico needs exactly 40 numbered castellations')
    header_pads=[p for p in children(header,'pad') if p[1] and p not in edge_pads]
    if len(header_pads)!=40:raise ValueError('Pico needs exactly 40 header holes')
    for pad in children(header,'pad'):
        if pad[1]:
            number=int(pad[1])
            expected=MECHANICAL.position(number)
            if any(p[1]=='pad_prop_castellated' for p in children(pad,'property')):
                expected=(0 if number<=20 else MECHANICAL.width,expected[1])
            if tuple(map(float,one(pad,'at')[1:3]))!=expected:
                raise ValueError('Pico header position changed')
            drill=float(one(pad,'drill')[1])
            if not math.isclose(drill,0.6 if pad in edge_pads else MECHANICAL.header_drill):
                raise ValueError('Pico header/castellation drill changed')
    holes=[tuple(map(float,one(p,'at')[1:3])) for p in children(header,'pad') if p[2]=='np_thru_hole']
    if sorted(holes)!=sorted(MECHANICAL.mounting_holes): raise ValueError('Pico mounting pattern changed')
    if any(float(one(p,'drill')[1])!=MECHANICAL.mounting_drill
           for p in children(header,'pad') if p[2]=='np_thru_hole'):
        raise ValueError('Pico mounting-hole diameter changed')
    outline=[s for s in children(doc,'gr_line') if one(s,'layer')[1]=='Edge.Cuts']
    corners=[(0.,0.),(21.,0.),(21.,51.),(0.,51.)]
    expected_edges={frozenset((a,b)) for a,b in zip(corners,corners[1:]+corners[:1])}
    actual_edges={frozenset((tuple(map(float,one(s,'start')[1:3])),
                             tuple(map(float,one(s,'end')[1:3])))) for s in outline}
    if len(outline)!=4 or actual_edges!=expected_edges:
        raise ValueError('Pico outline changed')
    if float(one(one(doc,'general'),'thickness')[1])!=1: raise ValueError('Board thickness must be 1 mm')
    usb_fit(doc)
    return len(observed)


def main():
    from .markings import audit
    count=verify_board(ROOT/'build/ch32-pico-placed.kicad_pcb')
    markings=audit(parse((ROOT/'build/ch32-pico-placed.kicad_pcb').read_text()))
    report=json.loads((ROOT/'build/placement-drc.json').read_text())
    if report['violations']: raise SystemExit(f"Placement failed: {len(report['violations'])} DRC violations")
    summary={'components':count,'source_pad_net_parity':True,'placement_violations':0,
             'unrouted_connections':len(report['unconnected_items']),'fabrication_ready':False,
             'silkscreen':markings}
    (ROOT/'build/placement-verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))


if __name__=='__main__': main()
