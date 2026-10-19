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
route('USB_DP',.1537,(9.75,7.09),(9.75,8.55),(10.6,9.4),(12.4,9.4),(13.05,9.4125),(13.05,11.6875),(13.05,12.6),(17.95,12.6),(17.95,21.95),(17.6,22.3),(9.9,22.3),(9.25,22.95),pad('U1','33'))
route('USB_DM',.1537,(11.25,7.95),(12,7.95),(12,8.4),(14.95,8.4),(14.95,9.4125),(14.95,11.6875),(18.3036,11.5),(18.3036,22.3036),(17.9072,22.7),(10.2,22.7),(9.75,23.05),pad('U1','32'))
route('USB_DP',.1537,(11.7,9.4),pad('R12','1'))
route('GND',.25,pad('D2','2'),(13.6,10.55));VIAS.append(('GND',13.6,10.55))
route('3V3_OUT',.2,pad('D2','5'),(14.4,10.55));VIAS.append(('3V3_OUT',14.4,10.55))
# MCU local decoupling follows the package position.
route('3V3_OUT',.25,pad('U1','48'),pad('C6','1'))
route('GND',.25,pad('C6','2'),(4.18,30.25),(5.2,30.25),pad('U1','47'))
route('GND',.25,pad('C7','2'),(4.18,28.3),(4.7,28.3))
VIAS.extend([('GND',5.2,30.25),('GND',4.7,28.3)])
# SY8301 loops. BS/LX feed the bootstrap capacitor above the package; LX
# runs up and over to the inductor; IN reaches the input capacitor below the
# package on the right, with GND returning through adjacent plane vias.
route('BUCK_BST',.25,pad('U4','1'),(6.38,13.6),pad('C4','1'))
route('BUCK_SW',.25,pad('U4','6'),(7.22,13.6),pad('C4','2'))
route('BUCK_SW',.6,pad('U4','6'),(8.6,13.75),(9.6,13.75),(10.25,14.9),pad('L1','1'))
route('VIN_SYS',.5,pad('U4','5'),(8.9,15.3),(8.9,17.9),pad('C1','1'))
route('GND',.5,pad('U4','2'),(4.65,15.3));VIAS.append(('GND',4.65,15.3))
route('GND',.5,pad('C1','2'),(5.21,19.95));VIAS.append(('GND',5.21,19.95))
route('GND',.5,pad('C1','2'),(6.3,17.6),(6.8,17.3));VIAS.append(('GND',6.8,17.3))
# Diode-OR inputs reach the input capacitor on the supply layer.
route('VIN_SYS',.35,pad('D1','1'),(3.5,15.7));VIAS.append(('VIN_SYS',3.5,15.7))
route('VIN_SYS',.4,(3.5,15.7),(3.5,16.0),(7.5,20.0),(8.39,19.95),layer='In2.Cu');VIAS.append(('VIN_SYS',8.39,19.95))
route('VIN_SYS',.5,pad('C1','1'),(8.39,19.95))
route('VIN_SYS',.5,(8.39,19.95),(9.0,20.5),pad('D4','1'))
route('VIN_SYS',.3,(8.39,19.95),(9.3,19.4),pad('R15','1'))
# Feedback divider sits away from LX; its top senses the output capacitors
# over a dedicated bottom-layer trace rather than the shared pour.
route('BUCK_FB',.15,pad('U4','3'),(4.6,16.25),(4.25,16.6),(4.25,17.23),pad('R14','1'))
route('BUCK_FB',.15,pad('R14','1'),pad('R13','2'))
route('GND',.2,pad('R14','2'),(2.85,16.1));VIAS.append(('GND',2.85,16.1))
route('3V3_OUT',.2,pad('R13','1'),(3.6,19.6));VIAS.append(('3V3_OUT',3.6,19.6))
route('3V3_OUT',.8,pad('L1','2'),(15.1,15.75),pad('C2','1'))
route('3V3_OUT',.8,(15.1,15.75),pad('C3','1'))
for ref,y in [('C2',13.2),('C3',16.1)]:
 x,py=pad(ref,'2');route('GND',.4,(x,py),(16.75,y));VIAS.append(('GND',16.75,y))
route('3V3_OUT',.25,pad('L1','2'),(15.6,15.8));VIAS.append(('3V3_OUT',15.6,15.8))
route('3V3_OUT',.2,(15.6,15.8),(15.6,14.6),(5.5,14.6),(5.5,17.2),(4.0,18.7),(3.6,19.6),layer='B.Cu')
# VBUS sense divider beside the connector, with a local ground return.
route('VBUS_SENSE',.15,pad('R1','2'),pad('R2','1'))
route('VBUS_SENSE',.15,pad('R2','1'),(16.85,7.1),pad('C9','1'))
route('GND',.3,pad('R2','2'),(16.3,9.0),(16.0,9.6));VIAS.append(('GND',16.0,9.6))
route('GND',.3,pad('C9','2'),(16.7,8.43),pad('R2','2'))
# A locked 3.3 V trunk on the supply layer joins the regulator output to the
# MCU decoupling corner and header pin 36, so the rail never depends on
# router-width taps between fragments of the shared pour.
route('3V3_OUT',.6,(15.6,15.8),(15.6,17.6),(17.0,19.0),(17.5,19.5),(17.5,33.2),(5.02,33.2),(5.02,32.1),layer='In2.Cu')
route('3V3_OUT',.6,(17.5,19.5),(17.5,12.0),(18.3,11.53),(19.39,11.53),layer='In2.Cu')
VIAS.append(('3V3_OUT',5.02,32.1))
route('3V3_OUT',.3,pad('C6','1'),(5.02,32.1))

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
        (polygon (pts (xy 3.0 19.0) (xy 4.2 19.0) (xy 4.2 20.2) (xy 3.0 20.2))))'''))
    from .stitching import apply as stitch
    stitch(doc)
    out.write_text(dump(doc)+'\n')
    copy_rules(source,out)
    print(f'Wrote critical copper to {out}; thermal qualification pending')


if __name__=='__main__':main()
