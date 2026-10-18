# SPDX-License-Identifier: MIT
"""GND stitching: ordinary tented through vias, outside paste.

One via joins the connector-region back pour to L2; five more tie the back
pour to the ground plane where no through-hole ground pins or decoupling
returns exist. The D5 pair is defined
beside its routes in protection_routes. There is no board-wide fence.
"""
from .sexp import parse
from .schematic import uid

VIAS=((14.5,7.55),(2.0,25.5),(17.0,21.5),(17.0,41.5),(18.0,39.0),(18.0,47.5))
ROUTES=()


def apply(doc):
    for i,(x,y) in enumerate(VIAS):
        doc.append(parse(f'''(via (at {x} {y}) (size .45) (drill .2)
            (layers "F.Cu" "B.Cu") (net "GND") (locked yes)
            (tenting front back) (uuid "{uid(f'stitch/via/{i}')}"))'''))
    for i,(width,points) in enumerate(ROUTES):
        for j,(a,b) in enumerate(zip(points,points[1:])):
            doc.append(parse(f'''(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]})
                (width {width}) (layer "F.Cu") (net "GND") (locked yes)
                (uuid "{uid(f'stitch/route/{i}/{j}')}"))'''))
