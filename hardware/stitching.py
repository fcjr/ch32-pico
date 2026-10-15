# SPDX-License-Identifier: MIT
"""Rev E local GND stitching, ordinary tented through vias without paste.

Two vias join the connector-region back pour to L2. Two more shorten C12's
ground return, and one supplements each surge clamp's existing ground via.
All sit outside paste; there is no board-wide fence or switch-node copper.
"""
from .sexp import parse
from .schematic import uid

VIAS=((5.5,7.8),(14.5,7.55),(14.85,14.025),(15.3,14.025),(15.7,3.4),(15.1,6.0))
ROUTES=(
    (.4,((16.4,13.91),(15.3,14.025),(14.85,14.025))),
    (.4,((15.7,2.8),(15.7,3.4))),
    (.4,((15.7,6.0),(15.1,6.0))),
)


def apply(doc):
    for i,(x,y) in enumerate(VIAS):
        doc.append(parse(f'''(via (at {x} {y}) (size .45) (drill .2)
            (layers "F.Cu" "B.Cu") (net "GND") (locked yes)
            (tenting front back) (uuid "{uid(f'reve/stitch/{i}')}"))'''))
    for i,(width,points) in enumerate(ROUTES):
        for j,(a,b) in enumerate(zip(points,points[1:])):
            doc.append(parse(f'''(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]})
                (width {width}) (layer "F.Cu") (net "GND") (locked yes)
                (uuid "{uid(f'reve/stitch-route/{i}/{j}')}"))'''))
