# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Explicit USB and local supply paths; independent DRC checks every output."""
import math
from .library import ROOT
from .schematic import uid
from .sexp import parse,children,dump
from .fabrication import copy_rules

# Net, width in mm, polyline. USB is low-speed, 1.5 Mbit/s.
# Spread the two under-ESD traces by 0.10 mm locally so a 0.45/0.20 mm
# VBUS via keeps clearance and the sampled L2 return under both trace edges.
ROUTES = [
 ('PA1',.15,[(7.6375,32.975),(9.5,32.975)]),
 ('PD0',.15,[(7.6375,34.925),(9.5,34.925)]),
 ('PC0',.15,[(7.6375,36.225),(9.5,36.225)]),
 ('3V3_OUT',.25,[(19.39,11.53),(18.63,11.53),(18.0,10.9)]),
 ('USB_DP',.1537,[(9.75,8.575),(9.75,7.6),(10.75,7.6),(10.75,8.575)]),
 ('USB_DM',.1537,[(10.25,8.575),(10.25,9.5),(11.25,9.5),(11.25,8.575)]),
 ('USB_DP',.1537,[(9.75,8.575),(9.75,9.85),(10.1,10.2),(10.1,10.345)]),
 ('USB_DM',.1537,[(11.25,9.5),(11.1,9.65),(11.1,10.345)]),
 ('USB_DP',.1537,[(10.1,10.345),(10.1,10.7),(10.0,10.8),(10.0,11.4),(10.1,11.5),(10.1,11.955),(10.1,12.3),(7.6375,14.7625),(7.6375,15.17)]),
 ('USB_DM',.1537,[(11.1,10.345),(11.1,10.7),(11.2,10.8),(11.2,11.4),(11.1,11.5),(11.1,11.955),(11.1,12.3),(13.3625,14.5625),(13.3625,15.17)]),
 ('PROBE_DP',.15,[(7.6375,16.03),(7.6375,17.075)]),
 ('PROBE_DM',.15,[(13.3625,16.03),(13.3625,17.075)]),
 ('GND',.15,[(10.6,11.955),(10.6,13.25)]),
 ('VBUS',.15,[(10.6,10.345),(10.6,11.06)]),
 ('3V3_OUT',.25,[(7.6375,22.275),(6.32,22.275)]),
 ('GND',.25,[(5.48,22.275),(4.7,22.275)]),
 ('TARGET_3V3',.25,[(7.6375,35.575),(6.32,35.575)]),
 ('TARGET_3V3',.25,[(6.32,34.3),(6.5,34.3),(6.5,35.575)]),
 ('GND',.25,[(5.48,35.575),(4.7,35.575)]),
 ('GND',.25,[(5.48,34.3),(4.7,34.3)]),
 ('3V3_OUT',.25,[(6.05,41.85),(4.92,41.85)]),
 ('VSYS',.25,[(6.05,44.15),(4.92,44.15)]),
 ('TARGET_3V3',.25,[(12.55,41.85),(11.42,41.85)]),
 ('VSYS',.25,[(12.55,44.15),(11.42,44.15)]),
]
VIAS = [('PD0',9.5,34.925),('PC0',9.5,36.225),('3V3_OUT',18.0,10.9),('GND',4.7,22.275),('GND',4.7,35.575),('GND',4.7,34.3),
        ('GND',10.6,13.25),('VBUS',10.6,11.06)]
from .design import BOARD_REVISION
PROTECTED_NETS = ({'USB_DP','USB_DM','BUCK_SW','BUCK_BST','VBUS','PD_OUT','3V3_OUT','GND'}
                  if BOARD_REVISION in ('B','C') else {name for name, _, _ in ROUTES})


def main():
    from .design import BOARD_REVISION
    if BOARD_REVISION == 'C':
        from .critical_routes_c import main as rev_c
        return rev_c()
    if BOARD_REVISION == 'B':
        from .critical_routes_b import main as rev_b
        return rev_b()
    if BOARD_REVISION != 'A':
        raise SystemExit('No critical routing seed for this revision')
    import wx
    import pcbnew as k
    from .pcb import point
    app=wx.App(False)
    source=ROOT/'build/ch32-pico-placed.kicad_pcb'
    out=ROOT/'build/ch32-pico-seed.kicad_pcb'
    board=k.LoadBoard(str(source))
    if board is None: raise ValueError(f'Cannot load {source}')
    nets=board.GetNetsByName()
    for name,width,points in ROUTES:
        for a,b in zip(points,points[1:]):
            t=k.PCB_TRACK(board);t.SetStart(point(*a));t.SetEnd(point(*b))
            t.SetWidth(round(width*1e6));t.SetLayer(k.F_Cu);t.SetNet(nets[name]);t.SetLocked(True);board.Add(t)
    for name,x,y in VIAS:
        v=k.PCB_VIA(board);v.SetPosition(point(x,y))
        v.SetWidth(450000);v.SetDrill(200000)
        v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu)
        v.SetNet(nets[name]);v.SetLocked(True);board.Add(v)
    k.SaveBoard(str(out),board)
    doc=parse(out.read_text())
    for kind in ('segment','via'):
        nodes=children(doc,kind)
        for node in nodes:
            node[:]=[v for v in node if not (isinstance(v,list) and v[0]=='uuid')]
        nodes.sort(key=dump)
        doc[:]=[v for v in doc if not (isinstance(v,list) and v[0]==kind)]
        for i,node in enumerate(nodes):
            node.append(['uuid',uid(f'critical/{kind}/{i}')]);doc.append(node)
    # A via's antipad must not cut into the L2 reference directly below USB.
    # Half-band 0.28 = max trace half-width 0.07685 + plane clearance 0.20,
    # rounded up. Keepout applies to via copper; its annulus adds more margin.
    for i,(name,width,points) in enumerate(ROUTES):
        if name not in {'USB_DP','USB_DM','PROBE_DP','PROBE_DM'}:continue
        for j,(a,b) in enumerate(zip(points,points[1:])):
            length=math.dist(a,b);ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length
            r=.28
            polygon=[(a[0]-ux*r-uy*r,a[1]-uy*r+ux*r),
                     (b[0]+ux*r-uy*r,b[1]+uy*r+ux*r),
                     (b[0]+ux*r+uy*r,b[1]+uy*r-ux*r),
                     (a[0]-ux*r+uy*r,a[1]-uy*r-ux*r)]
            pts=' '.join(f'(xy {x:.6f} {y:.6f})' for x,y in polygon)
            doc.append(parse(f'''(zone (net 0) (net_name "") (layer "In1.Cu")
                (uuid "{uid(f'usb-return-keepout/{i}/{j}')}") (hatch edge 0.5)
                (connect_pads (clearance 0)) (min_thickness 0.1)
                (keepout (tracks allowed) (vias not_allowed) (pads allowed)
                    (copperpour allowed) (footprints allowed))
                (fill (thermal_gap 0.3) (thermal_bridge_width 0.3))
                (polygon (pts {pts})))'''))
    out.write_text(dump(doc)+'\n')
    copy_rules(source,out)
    print(f'Wrote {len(ROUTES)} critical polylines to {out}')


if __name__=='__main__':main()
