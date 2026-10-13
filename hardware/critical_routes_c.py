# SPDX-License-Identifier: MIT
"""Revs C/D locked USB, local buck loops and provisional high-current copper.

Coordinates are reviewed against the generated placement with independent DRC.
Passing DRC does not establish a 5 A thermal/contact rating.
"""
import math
from .library import ROOT
from .sexp import parse, dump
from .schematic import uid
from .fabrication import copy_rules

# Layer, net, width, vertices. No via-in-pad assembly is required.
ROUTES = [('F.Cu', 'USB_DP', 0.1537, [(9.75, 7.09), (9.75, 6.05), (10.75, 6.05), (10.75, 7.09)]),
 ('F.Cu', 'USB_DM', 0.1537, [(10.25, 7.09), (10.25, 7.95), (11.25, 7.95), (11.25, 7.09)]),
 ('F.Cu',
  'USB_DP',
  0.1537,
  [(9.75, 7.09),
   (9.75, 8.55),
   (10.6, 9.4),
   (12.4, 9.4),
   (13.05, 9.1625),
   (13.05, 11.4375),
   (13.05, 12.55),
   (17.7, 12.55),
   (17.7, 20.5),
   (15.9, 22.3),
   (9.9, 22.3),
   (9.25, 22.95),
   (9.25, 23.8375)]),
 ('F.Cu',
  'USB_DM',
  0.1537,
  [(11.25, 7.95),
   (12.3, 7.95),
   (14.95, 8.4),
   (14.95, 9.1625),
   (14.95, 11.4375),
   (18.0037, 11.5),
   (18.0037, 20.75),
   (16.0537, 22.7),
   (10.2, 22.7),
   (9.75, 23.05),
   (9.75, 23.8375)]),
 ('F.Cu', 'USB_DP', 0.1537, [(11.7, 9.4), (11.7, 9.57)]),
 ('F.Cu', '3V3_OUT', 0.25, [(6.3375, 30.75), (5.02, 30.95)]),
 ('F.Cu', 'GND', 0.25, [(4.18, 30.95), (3.55, 30.95)]),
 ('F.Cu', 'GND', 0.25, [(4.18, 29.2), (3.55, 29.2)]),
 ('F.Cu', 'GND', 0.2, [(6.3375, 30.25), (5.2, 30.25)]),
 ('F.Cu', 'GND', 0.25, [(14, 11.4375), (13.6, 10.3)]),
 ('F.Cu', '3V3_OUT', 0.2, [(14, 9.1625), (14.4, 10.3)]),
 ('F.Cu', 'VIN_SYS', 0.6, [(5.8, 15.65), (5.41, 16.04), (5.41, 17.05)]),
 ('F.Cu', 'GND', 0.6, [(8.2, 15.65), (8.59, 16.04), (8.59, 17.05)]),
 ('F.Cu', 'GND', 0.4, [(8.59, 17.05), (8.59, 18.3), (7.95, 18.3)]),
 ('F.Cu', 'BUCK_SW', 0.6, [(8.2, 14.7), (10.2, 14.7), (10.45, 14.95)]),
 ('F.Cu', 'BUCK_SW', 0.25, [(10.2, 14.7), (9.15, 13.65), (9.15, 12.5), (8.42, 12.5)]),
 ('F.Cu', 'BUCK_BST', 0.25, [(8.2, 13.75), (7.58, 13.13), (7.58, 12.5)]),
 ('F.Cu', '3V3_OUT', 0.8, [(14.35, 14.95), (15.2, 14.95), (15.55, 15.3), (16.7, 15.7), (16.4, 17.3)]),
 ('F.Cu', 'GND', 0.5, [(16.7, 13.7), (15.65, 13.7), (15.65, 13.2)]),
 ('F.Cu', 'GND', 0.5, [(16.4, 19.3), (16.4, 20.5), (15.8, 20.5)]),
 ('F.Cu', '3V3_OUT', 0.2, [(5.8, 13.75), (5.05, 13.75)]),
 ('F.Cu', '3V3_OUT', 0.2, [(14.35, 14.95), (14.35, 18.0)]),
 ('B.Cu', '3V3_OUT', 0.2, [(5.05, 13.75), (5.05, 15.5), (7.05, 17.5), (13.85, 17.5), (14.35, 18.0)]),
 ('F.Cu', 'VIN_SYS', 0.5, [(4.3, 10.7), (4.3, 15.94), (5.41, 17.05)]),
 ('F.Cu', 'VIN_SYS', 0.5, [(16.9, 10.6), (17.8, 10.6)]),
 ('F.Cu', 'VIN_SYS', 0.5, [(4.3, 10.7), (3.4, 10.7)]),
 ('In2.Cu', 'VIN_SYS', 0.5, [(17.8, 10.6), (17.8, 9), (17, 8.8), (5.8, 8.8), (3.4, 10.6), (3.4, 10.7)]),
 ('F.Cu', 'VSYS', 0.4, [(16.9, 7.2), (16.15, 7.2)]),
 ('In2.Cu', 'VSYS', 0.25, [(19.39, 3.91), (18.85, 3.91), (18.85, 5.2), (16.85, 7.2), (16.15, 7.2)]),
 ('F.Cu', 'VBUS', 0.32, [(8.1, 7.09), (8.1, 6.5), (8.55, 5.85)]),
 ('F.Cu', 'VBUS', 0.8, [(8.55, 5.85), (8.55, 4.7)]),
 ('F.Cu', 'VBUS', 0.32, [(12.9, 7.09), (12.9, 6.5), (12.45, 5.85)]),
 ('F.Cu', 'VBUS', 0.8, [(12.45, 5.85), (12.45, 4.7)]),
 ('F.Cu', 'VBUS', 1.0, [(8.1, 4.7), (13.5, 4.7)]),
 ('B.Cu', 'VBUS', 0.6, [(12.3, 3.9), (13, 3.9), (13, 4.5), (12.3, 4.5)]),
 ('F.Cu', 'VBUS', 0.8, [(12.3, 4.7), (12.3, 3.9), (13, 3.9), (13, 4.7)]),
 ('F.Cu', 'VBUS', 0.3, [(16.8, 1.3), (16.8, 0.8), (15.6, 0.8), (15, 0.8)]),
 ('F.Cu', 'VBUS', 0.3, [(16.8, 3.7), (16.8, 3.85), (16.5, 4.15), (15.6, 4.2), (15.6, 4.8)]),
 ('B.Cu', 'VBUS', 0.8, [(13, 4.5), (16.25, 4.5)]),
 ('B.Cu', 'VBUS', 0.4, [(15, 0.8), (15.6, 0.8), (16.65, 0.8), (16.65, 4.2), (15.6, 4.2), (15.6, 4.8)]),
 ('F.Cu', 'VBUS', 0.4, [(8.1, 4.7), (5.7, 4.7), (5.2, 4.93), (4.3, 4.93)]),
 ('F.Cu', 'VBUS', 0.3, [(5.2, 4.93), (5.3, 4.93)]),
 ('F.Cu', 'VBUS', 0.3, [(4.3, 7.3), (5.3, 7.3)]),
 ('B.Cu', 'VBUS', 0.3, [(5.3, 4.93), (5.3, 7.3)]),
 ('F.Cu', 'VBUS', 0.3, [(15.6, 4.8), (16, 5.28)]),
 ('F.Cu', 'PD_OUT', 0.3, [(17.3, 1.3), (17.3, 0.75), (18.25, 0.75)]),
 ('F.Cu', 'PD_OUT', 0.3, [(17.3, 3.7), (17.25, 4.2), (17.75, 4.2), (17.75, 4.8), (17.15, 4.8), (17.25, 4.2)]),
 ('B.Cu', 'PD_OUT', 0.3, [(17.15, 4.8), (17.75, 4.8), (17.75, 4.2), (17.25, 4.2), (17.15, 4.8)]),
 ('B.Cu', 'PD_OUT', 0.8, [(17.5, 4.2), (17.5, 1.8), (17.93, 1.37), (19.39, 1.37)]),
 ('In2.Cu', 'PD_OUT', 0.3, [(17.15, 4.8), (17.75, 4.8), (17.75, 4.2), (17.25, 4.2), (17.15, 4.8)]),
 ('In2.Cu', 'PD_OUT', 0.8, [(17.5, 4.2), (17.5, 1.8), (17.93, 1.37), (19.39, 1.37)]),
 ('B.Cu', 'PD_OUT', 0.5, [(18.25, 0.75), (18.77, 0.75), (19.39, 1.37)]),
 ('F.Cu', 'PD_OUT', 0.3, [(17.15, 4.8), (17.2, 5.28)]),
 ('F.Cu', 'PD_ENABLE', 0.15, [(16.15, 1.8), (16.05, 1.4)]),
 ('F.Cu', 'PD_OVLO', 0.15, [(16.15, 2.275), (15.55, 2.275), (15.55, 3.5), (15.25, 3.7)]),
 ('F.Cu', 'PD_DVDT', 0.15, [(17.95, 3.2), (18.2, 3.4), (18.35, 3.55), (18.35, 6.5), (18.25, 7.28)]),
 ('F.Cu', 'GND', 0.15, [(18.25, 8.12), (18.65, 8.0)]),
 ('F.Cu', 'PD_OVLO', 0.15, [(4.3, 4.07), (3.5, 4.07)]),
 ('F.Cu', 'PD_OVLO', 0.15, [(3.87, 6.1), (3.1, 6.1)]),
 ('B.Cu', 'PD_OVLO', 0.15, [(3.5, 4.07), (3.1, 4.47), (3.1, 6.1)]),
 ('In2.Cu', 'PD_OVLO', 0.15, [(15.25, 3.7), (15.25, 3.4375), (3.5, 3.4375), (3.5, 4.07)]),
 ('F.Cu', 'PD_FAULT_N', 0.15, [(16.15, 3.2), (16, 3.6)]),
 ('F.Cu', 'PD_ILM', 0.15, [(17.95, 2.275), (18.5, 2.275), (18.55, 2.25)]),
 ('F.Cu', 'GND', 0.15, [(17.95, 2.725), (18.3, 2.725), (18.65, 2.95)]),
 ('B.Cu',
  'PD_ILM',
  0.15,
  [(18.55, 2.25),
   (18.16, 2.25),
   (18.16, 3.2),
   (18.25, 3.9),
   (18.3, 4.9),
   (18, 5.4),
   (15.6, 5.4),
   (15.405, 5.22),
   (15.2, 5.18),
   (10, 5.18),
   (9, 4.14),
   (5, 4.14),
   (3.1, 3)]),
 ('F.Cu', 'PD_ILM', 0.15, [(3.87, 1.8), (3.2, 1.8), (3.1, 3), (3.87, 3)]),
 ('F.Cu', 'PD_ILM', 0.15, [(3.8, 35.93), (4.7, 35.93)]),
 ('In2.Cu', 'PD_ENABLE', 0.15, [(16.05, 1.4), (16.05, 2.95), (16.5, 3.4), (16.5, 5.9), (15.6, 6.8), (15.6, 7.75), (15.8, 7.95)]),
 ('In2.Cu',
  'PD_FAULT_N',
  0.15,
  [(16, 3.6), (16.1, 4), (16.1, 5.4), (15.6, 5.4), (15.405, 5.22), (15.2, 5.18), (9.73, 5.18), (9.33, 5.58)]),
 ('F.Cu', 'PD_OUT', 0.25, [(17.2, 5.28), (17.8, 5.28), (17.8, 6.3), (17.7, 6.7), (17.7, 7.8), (17.55, 8.28)])]
VIAS = [('GND', 3.55, 30.95),
 ('GND', 3.55, 29.2),
 ('GND', 5.2, 30.25),
 ('GND', 13.6, 10.3),
 ('3V3_OUT', 14.4, 10.3),
 ('GND', 8.59, 18.3),
 ('GND', 7.95, 18.3),
 ('GND', 15.65, 13.2),
 ('GND', 16.4, 20.5),
 ('GND', 15.8, 20.5),
 ('3V3_OUT', 5.05, 13.75),
 ('3V3_OUT', 14.35, 18.0),
 ('VIN_SYS', 3.4, 10.7),
 ('VIN_SYS', 17.8, 10.6),
 ('VSYS', 16.15, 7.2),
 ('VBUS', 12.3, 4.5),
 ('VBUS', 13, 4.5),
 ('VBUS', 12.3, 3.9),
 ('VBUS', 13, 3.9),
 ('VBUS', 15.6, 0.8),
 ('VBUS', 15, 0.8),
 ('VBUS', 15.6, 4.2),
 ('VBUS', 15.6, 4.8),
 ('VBUS', 5.3, 4.93),
 ('VBUS', 5.3, 7.3),
 ('PD_OUT', 18.25, 0.75),
 ('PD_OUT', 17.25, 4.2),
 ('PD_OUT', 17.75, 4.2),
 ('PD_OUT', 17.15, 4.8),
 ('PD_OUT', 17.75, 4.8),
 ('PD_ENABLE', 16.05, 1.4),
 ('PD_OVLO', 15.25, 3.7),
 ('GND', 18.65, 8.0),
 ('PD_OVLO', 3.5, 4.07),
 ('PD_OVLO', 3.1, 6.1),
 ('PD_FAULT_N', 16, 3.6),
 ('PD_ILM', 18.55, 2.25),
 ('GND', 18.65, 2.95),
 ('PD_ILM', 3.1, 3),
 ('PD_ILM', 4.7, 35.93),
 ('PD_ENABLE', 15.8, 7.95),
 ('PD_FAULT_N', 9.33, 5.58),
 ('PD_OUT', 17.55, 8.28)]

def main():
    source=ROOT/'build/ch32-pico-placed.kicad_pcb'
    out=ROOT/'build/ch32-pico-seed.kicad_pcb'
    doc=parse(source.read_text())
    for i,(layer,net,width,points) in enumerate(ROUTES):
        for j,(a,b) in enumerate(zip(points,points[1:])):
            # GPIO/control pin escapes may be pruned if the router reaches
            # the pad another way. USB and power trunk geometry stay locked.
            lock='' if net in {'PD_ENABLE'} else '(locked yes)'
            doc.append(parse(f'''(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]})
                (width {width}) (layer "{layer}") (net "{net}") {lock}
                (uuid "{uid(f'revc/route/{i}/{j}')}"))'''))
            if net not in {'USB_DP','USB_DM'}:continue
            length=math.dist(a,b);ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length
            r=.28
            polygon=[(a[0]-ux*r-uy*r,a[1]-uy*r+ux*r),
                     (b[0]+ux*r-uy*r,b[1]+uy*r+ux*r),
                     (b[0]+ux*r+uy*r,b[1]+uy*r-ux*r),
                     (a[0]-ux*r+uy*r,a[1]-uy*r-ux*r)]
            pts=' '.join(f'(xy {x:.6f} {y:.6f})' for x,y in polygon)
            doc.append(parse(f'''(zone (net "") (layer "In1.Cu")
                (uuid "{uid(f'revc/usb-return/{i}/{j}')}") (hatch edge 0.5)
                (connect_pads (clearance 0)) (min_thickness 0.1)
                (keepout (tracks allowed) (vias not_allowed) (pads allowed)
                    (copperpour allowed) (footprints allowed))
                (fill (thermal_gap 0.3) (thermal_bridge_width 0.3))
                (polygon (pts {pts})))'''))
    for i,(net,x,y) in enumerate(VIAS):
        lock='(locked yes)'
        doc.append(parse(f'''(via (at {x} {y}) (size .45) (drill .2)
          (layers "F.Cu" "B.Cu") (net "{net}") {lock}
          (uuid "{uid(f'revc/via/{i}')}"))'''))
    # Prevent the shared 3V3 plane from bypassing the dedicated FB sense trace.
    doc.append(parse(f'''(zone (net "") (layer "In2.Cu")
        (uuid "{uid('revc/feedback-plane-isolation')}") (hatch edge 0.5)
        (connect_pads (clearance 0)) (min_thickness 0.1)
        (keepout (tracks allowed) (vias allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))
        (fill (thermal_gap 0.3) (thermal_bridge_width 0.3))
        (polygon (pts (xy 4.45 13.15) (xy 5.65 13.15) (xy 5.65 14.35) (xy 4.45 14.35))))'''))
    out.write_text(dump(doc)+'\n')
    copy_rules(source,out)
    from .design import BOARD_REVISION
    print(f'Wrote Rev {BOARD_REVISION} critical copper to {out}; thermal qualification pending')


if __name__=='__main__':main()
