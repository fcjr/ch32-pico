# SPDX-License-Identifier: MIT
"""Locked USB, supply and VBUS copper; independent DRC checks every output."""
import math
from .library import ROOT
from .sexp import parse, dump
from .schematic import uid
from .fabrication import copy_rules
from .protection_routes import ROUTES, VIAS, route, pad

# Nets whose routed copper cleanup must never prune.
PROTECTED_NETS = {'USB_DP','USB_DM','BUCK_SW','BUCK_BST','VBUS','3V3_OUT','GND'}

# USB connector duplicates, ESD pass-through, and paired front-layer trunk.
route('USB_DP',.1537,(9.75,7.09),(9.75,6.05),(10.75,6.05),(10.75,7.09))
route('USB_DM',.1537,(10.25,7.09),(10.25,7.95),(11.25,7.95),(11.25,7.09))
route('USB_DP',.1537,(9.75,7.09),(9.75,8.55),(10.6,9.4),(12.4,9.4),(13.05,9.4125),(13.05,11.6875),(13.05,12.6),(17.7,12.6),(17.7,21.95),(17.35,22.3),(9.9,22.3),(9.25,22.95),pad('U1','33'))
route('USB_DM',.1537,(11.25,7.95),(12,7.95),(12,8.4),(14.95,8.4),(14.95,9.4125),(14.95,11.6875),(18.0536,11.5),(18.0536,22.3036),(17.6572,22.7),(10.2,22.7),(9.75,23.05),pad('U1','32'))
route('USB_DP',.1537,(11.7,9.4),pad('R12','1'))
route('GND',.25,pad('D2','2'),(13.6,10.55));VIAS.append(('GND',13.6,10.55))
route('3V3_OUT',.2,pad('D2','5'),(14.4,10.55));VIAS.append(('3V3_OUT',14.4,10.55))
# MCU local decoupling follows the package position.
route('3V3_OUT',.25,pad('U1','48'),pad('C6','1'))
route('GND',.25,pad('C6','2'),(4.18,30.25),(5.2,30.25),pad('U1','47'))
route('GND',.25,pad('C7','2'),(4.18,28.3),(4.7,28.3))
VIAS.extend([('GND',5.2,30.25),('GND',4.7,28.3)])
# Fixed regulator input loop, bootstrap and switching node are all local F.Cu.
route('VIN_SYS',.6,pad('U4','3'),(5.21,16.64),pad('C1','1'))
route('GND',.6,pad('U4','4'),(8.39,16.64),pad('C1','2'))
route('GND',.4,pad('C1','2'),(8.9,17.14),(8.9,16.0));VIAS.extend([('GND',8.9,16.0),('GND',8.9,16.5)])
route('BUCK_SW',.6,pad('U4','5'),(10.0,15.3),pad('L1','1'))
route('BUCK_SW',.25,(9,15.3),(9,13.9),(8.2,13.1),pad('C4','2'))
route('BUCK_BST',.25,pad('U4','6'),(7.38,13.73),pad('C4','1'))
route('3V3_OUT',.8,pad('L1','2'),(15.2,15.75),pad('C2','1'))
route('3V3_OUT',.8,(15.2,15.75),pad('C3','1'))
for ref,y in [('C2',13.2),('C3',16.1)]:
 x,py=pad(ref,'2');route('GND',.4,(x,py),(x,y));VIAS.append(('GND',x,y))
route('3V3_OUT',.2,pad('U4','1'),(5.6,13.5));VIAS.append(('3V3_OUT',5.6,13.5))
route('3V3_OUT',.25,pad('L1','2'),(15.6,15.8));VIAS.append(('3V3_OUT',15.6,15.8))
route('3V3_OUT',.2,(5.6,13.5),(5.6,14.6),(15.6,14.6),(15.6,15.8),layer='B.Cu')
route('VIN_SYS',.35,pad('D1','1'),(4.2,15.1),(4.4,15.4),(4.4,16.4),pad('C1','1'))
route('VIN_SYS',.35,pad('D4','1'),(6.0,20.0),(5.21,19.2),pad('C1','1'))

def main():
    source=ROOT/'build/ch32-pico-placed.kicad_pcb'
    out=ROOT/'build/ch32-pico-seed.kicad_pcb'
    doc=parse(source.read_text())
    for i,(layer,net,width,points) in enumerate(ROUTES):
        for j,(a,b) in enumerate(zip(points,points[1:])):
            # GPIO/control pin escapes may be pruned if the router reaches
            # the pad another way. USB and power trunk geometry stay locked.
            optional=net in {'CC1','BOOT_PULLUP'}
            lock='' if optional else '(locked yes)'
            doc.append(parse(f'''(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]})
                (width {width}) (layer "{layer}") (net "{net}") {lock}
                (uuid "{uid(f'critical/route/{i}/{j}')}"))'''))
            if net not in {'USB_DP','USB_DM'}:continue
            length=math.dist(a,b);ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length
            r=.28
            polygon=[(a[0]-ux*r-uy*r,a[1]-uy*r+ux*r),
                     (b[0]+ux*r-uy*r,b[1]+uy*r+ux*r),
                     (b[0]+ux*r+uy*r,b[1]+uy*r-ux*r),
                     (a[0]-ux*r+uy*r,a[1]-uy*r-ux*r)]
            pts=' '.join(f'(xy {x:.6f} {y:.6f})' for x,y in polygon)
            doc.append(parse(f'''(zone (net "") (layer "In1.Cu")
                (uuid "{uid(f'critical/usb-return/{i}/{j}')}") (hatch edge 0.5)
                (connect_pads (clearance 0)) (min_thickness 0.1)
                (keepout (tracks allowed) (vias not_allowed) (pads allowed)
                    (copperpour allowed) (footprints allowed))
                (fill (thermal_gap 0.3) (thermal_bridge_width 0.3))
                (polygon (pts {pts})))'''))
    for i,(net,x,y) in enumerate(VIAS):
        lock='' if net in {'CC1','BOOT_PULLUP'} else '(locked yes)'
        doc.append(parse(f'''(via (at {x} {y}) (size .45) (drill .2)
          (layers "F.Cu" "B.Cu") (net "{net}") {lock}
          (uuid "{uid(f'critical/via/{i}')}"))'''))
    # Prevent the shared 3V3 plane from bypassing the dedicated FB sense trace.
    doc.append(parse(f'''(zone (net "") (layer "In2.Cu")
        (uuid "{uid('critical/feedback-plane-isolation')}") (hatch edge 0.5)
        (connect_pads (clearance 0)) (min_thickness 0.1)
        (keepout (tracks allowed) (vias allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))
        (fill (thermal_gap 0.3) (thermal_bridge_width 0.3))
        (polygon (pts (xy 5.0 12.9) (xy 6.2 12.9) (xy 6.2 14.1) (xy 5.0 14.1))))'''))
    from .stitching import apply as stitch
    stitch(doc)
    out.write_text(dump(doc)+'\n')
    copy_rules(source,out)
    print(f'Wrote critical copper to {out}; thermal qualification pending')


if __name__=='__main__':main()
