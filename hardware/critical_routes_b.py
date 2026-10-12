# SPDX-License-Identifier: MIT
"""Rev B locked USB, local buck loops and provisional high-current copper.

Coordinates are reviewed against the generated placement with independent DRC.
Passing DRC does not establish a 5 A thermal/contact rating.
"""
import math
from .library import ROOT
from .sexp import parse, dump
from .schematic import uid
from .fabrication import copy_rules

# Layer, net, width, vertices. No via-in-pad assembly is required.
ROUTES = [
 ('F.Cu','USB_DP',.1537,[(9.75,8.54),(9.75,7.5),(10.75,7.5),(10.75,8.54)]),
 ('F.Cu','USB_DM',.1537,[(10.25,8.54),(10.25,9.4),(11.25,9.4),(11.25,8.54)]),
 ('F.Cu','USB_DP',.1537,[(9.75,8.54),(9.75,9.65),(9.55,9.85),(9.55,10.3625),(9.55,12.6375),(9.55,13.1),(9.35,13.3),(9.35,17.7),(9.25,17.8),(9.25,18.3375)]),
 ('F.Cu','USB_DM',.1537,[(11.25,9.4),(11.45,9.6),(11.45,10.3625),(11.45,12.6375),(11.45,13.1),(9.6537,14.8963),(9.6537,17.7),(9.75,17.7963),(9.75,18.3375)]),
 ('F.Cu','USB_DP',.1537,[(9.35,13.5),(8.42,13.5)]),
 ('F.Cu','3V3_OUT',.25,[(10.5,10.3625),(10.5,11.4)]),
 ('F.Cu','GND',.25,[(10.5,12.6375),(10.5,13.3),(10.1,13.7)]),
 ('F.Cu','3V3_OUT',.25,[(6.3375,25.25),(5.02,25.45)]),
 ('F.Cu','GND',.25,[(4.18,25.45),(3.55,25.45)]),
 ('F.Cu','GND',.25,[(4.18,23.7),(3.55,23.7)]),
 ('F.Cu','GND',.2,[(6.3375,24.75),(5.2,24.75)]),
 ('F.Cu','3V3_OUT',.25,[(17.23,13.1),(17.95,13.1)]),
 ('F.Cu','3V3_OUT',.6,[(14.75,40),(14.75,43),(14.3,43),(14.9,43)]),
 ('F.Cu','GND',.4,[(9.39,42.1),(8.85,42.1)]),
 ('F.Cu','PD_ENABLE',.15,[(16.0,5.3),(15.9,5.3),(15.5,5.2)]),
 ('F.Cu','PD_DVDT',.15,[(17.8,6.7),(18.1,6.7),(18.2,6.75),(18.2,7.7)]),
 ('F.Cu','PD_DVDT',.15,[(17.42,9.35),(18,9.35)]),
 ('B.Cu','PD_DVDT',.15,[(18.2,7.7),(18.2,9.2),(18,9.35)]),
 ('F.Cu','PD_ILM',.15,[(17.8,5.775),(18.35,5.775),(18.35,5.05),(18.45,4.95)]),
 ('F.Cu','STATUS_LED',.15,[(14.6625,20.25),(15.95,20.25)]),
 ('F.Cu','PA1',.15,[(12.75,26.6625),(12.75,28)]),
 ('F.Cu','VBUS',.25,[(4.4,14.23),(3.6,14.23)]),
 ('F.Cu','VIN_SYS',.5,[(4.3,42.9),(5.61,42.9),(6.21,43.5)]),
 ('F.Cu','VSYS',.25,[(4.3,39.5),(3.5,39.5)]),
 # Dedicated low-current control-supply paths, separate from the 5 A output.
 ('F.Cu','VBUS',.25,[(8.1,6),(3.1,6),(3.1,8.3),(4.3,8.3)]),
 ('In2.Cu','VSYS',.25,[(19.39,3.91),(18.1,2.62),(18.1,1.6),(17.1,.6),(3,.6),(3,39.5),(3.5,39.5)]),
 ('F.Cu','PD_OVLO',.15,[(4.4,5.37),(3.6,5.15)]),
 ('F.Cu','PD_OVLO',.15,[(3.87,7),(3.65,6.55)]),
 ('In2.Cu','PD_OVLO',.15,[(3.6,5.15),(3.65,5.2),(3.65,6.55)]),
 # Fixed 3.3 V buck. Switch node remains local, with no plane or long trace.
 ('F.Cu','BUCK_SW',.5,[(9.2,40),(10.85,40)]),
 ('F.Cu','BUCK_SW',.25,[(10.85,40),(10.85,38.4),(9.95,37.5),(9.32,37.5)]),
 ('F.Cu','BUCK_BST',.25,[(9.2,39.05),(8.48,38.33),(8.48,37.5)]),
 ('F.Cu','VIN_SYS',.5,[(6.8,40.95),(6.21,41.54),(6.21,43.5)]),
 ('F.Cu','GND',.5,[(9.2,40.95),(9.39,41.14),(9.39,43.5)]),
 ('F.Cu','3V3_OUT',.8,[(14.75,40),(15.8,40),(16.8,39)]),
 ('F.Cu','3V3_OUT',.8,[(15.8,40),(16.3,40.5),(16.8,40.5)]),
 ('F.Cu','GND',.5,[(16.8,37),(18,37)]),
 ('F.Cu','GND',.5,[(16.8,42.5),(18,42.5)]),
 ('F.Cu','3V3_OUT',.25,[(6.8,39.05),(6,39.05)]),
 # Both receptacle VBUS terminals participate in the input path.
 ('F.Cu','VBUS',.32,[(8.1,8.54),(8.1,7.95),(8.55,7.3)]),
 ('F.Cu','VBUS',.8,[(8.55,7.3),(8.55,6)]),
 ('F.Cu','VBUS',.32,[(12.9,8.54),(12.9,7.95),(12.45,7.3)]),
 ('F.Cu','VBUS',.8,[(12.45,7.3),(12.45,6)]),
 ('F.Cu','VBUS',1.0,[(8.1,6),(13.2,6)]),
 ('F.Cu','VBUS',.3,[(16.65,4.8),(16.65,4.42),(16.5,4.42),(15.8,4.42),(15.8,3.8)]),
 ('F.Cu','VBUS',.3,[(16.65,7.2),(16.65,7.85),(16.3,7.85),(16.3,8.45)]),
 ('B.Cu','VBUS',1.0,[(13.2,6),(14,6.15),(16,6.15),(16.3,6.45),(16.3,8.45)]),
 ('B.Cu','VBUS',.3,[(15.8,3.8),(15.8,4.42),(16.35,4.97),(16.35,5.6),(16,6.15)]),
 # Output exits both ends of the eFuse terminal, then runs on both outer
 # layers through the narrow corridor beside the upper Pico mounting hole.
 ('F.Cu','PD_OUT',.3,[(17.15,4.8),(17.15,4.2),(17.3,3.9),(17.85,4.1)]),
 ('F.Cu','PD_OUT',.3,[(17.15,7.2),(17.15,7.7),(17.35,8.1),(17.45,8.7)]),
 ('B.Cu','PD_OUT',.8,[(17.85,4.1),(17.4,4.9),(17.4,8.1),(17.35,8.1),(17.45,8.7)]),
 ('B.Cu','PD_OUT',.4,[(17.3,3.9),(17.85,4.1)]),
 *[(layer,'PD_OUT',.8,[(17.85,4.1),(17.85,2.2),(18.63,1.37),(19.39,1.37)]) for layer in ('F.Cu','B.Cu')],
]
VIAS = [
 ('PD_OVLO',3.6,5.15),('PD_OVLO',3.65,6.55),
 ('VSYS',3.5,39.5),
 ('PD_DVDT',18.2,7.7),('PD_DVDT',18,9.35),('PD_ILM',18.45,4.95),
 ('PD_ENABLE',15.5,5.2),('STATUS_LED',15.95,20.25),('PA1',12.75,28),('VBUS',3.6,14.23),
 ('3V3_OUT',10.5,11.4),('GND',10.1,13.7),('GND',3.55,25.45),
 ('GND',3.55,23.7),('GND',5.2,24.75),('3V3_OUT',6,39.05),
 ('GND',9.39,42.1),('GND',8.85,42.1),
 ('GND',18,37),('GND',18,42.5),
 ('3V3_OUT',14.3,43),('3V3_OUT',14.9,43),('3V3_OUT',17.95,13.1),
 *[('VBUS',x,y) for x,y in [(12.9,6),(13.5,6),(12.9,6.6),(13.5,6.6),
                            (15.8,3.8),(15.8,4.42),(16.3,7.85),(16.3,8.45)]],
 *[('PD_OUT',x,y) for x,y in [(17.3,3.9),(17.85,4.1),(17.35,8.1),(17.45,8.7)]],
]


def main():
    source=ROOT/'build/ch32-pico-placed.kicad_pcb'
    out=ROOT/'build/ch32-pico-seed.kicad_pcb'
    doc=parse(source.read_text())
    for i,(layer,net,width,points) in enumerate(ROUTES):
        for j,(a,b) in enumerate(zip(points,points[1:])):
            # GPIO/control pin escapes may be pruned if the router reaches
            # the pad another way. USB and power trunk geometry stay locked.
            lock='' if net in {'PA1','STATUS_LED','PD_ENABLE'} else '(locked yes)'
            doc.append(parse(f'''(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]})
                (width {width}) (layer "{layer}") (net "{net}") {lock}
                (uuid "{uid(f'revb/route/{i}/{j}')}"))'''))
            if net not in {'USB_DP','USB_DM'}:continue
            length=math.dist(a,b);ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length
            r=.28
            polygon=[(a[0]-ux*r-uy*r,a[1]-uy*r+ux*r),
                     (b[0]+ux*r-uy*r,b[1]+uy*r+ux*r),
                     (b[0]+ux*r+uy*r,b[1]+uy*r-ux*r),
                     (a[0]-ux*r+uy*r,a[1]-uy*r-ux*r)]
            pts=' '.join(f'(xy {x:.6f} {y:.6f})' for x,y in polygon)
            doc.append(parse(f'''(zone (net "") (layer "In1.Cu")
                (uuid "{uid(f'revb/usb-return/{i}/{j}')}") (hatch edge 0.5)
                (connect_pads (clearance 0)) (min_thickness 0.1)
                (keepout (tracks allowed) (vias not_allowed) (pads allowed)
                    (copperpour allowed) (footprints allowed))
                (fill (thermal_gap 0.3) (thermal_bridge_width 0.3))
                (polygon (pts {pts})))'''))
    optional={('PD_ENABLE',15.5,5.2),('STATUS_LED',15.95,20.25),('PA1',12.75,28),('VBUS',3.6,14.23)}
    for i,(net,x,y) in enumerate(VIAS):
        lock='' if (net,x,y) in optional else '(locked yes)'
        doc.append(parse(f'''(via (at {x} {y}) (size .45) (drill .2)
          (layers "F.Cu" "B.Cu") (net "{net}") {lock}
          (uuid "{uid(f'revb/via/{i}')}"))'''))
    out.write_text(dump(doc)+'\n')
    copy_rules(source,out)
    print(f'Wrote Rev B critical copper to {out}; thermal qualification pending')


if __name__=='__main__':main()
