# SPDX-License-Identifier: MIT
"""GND stitching: ordinary tented through vias, outside paste.

One via joins the connector-region back pour to L2; 11 more tie the back
pour to the ground plane on a clearance-filtered grid, including through the
3.3 V inner pour where it is wide. There is no board-wide fence.
"""
from .sexp import parse
from .schematic import uid

VIAS=((14.5,7.55),(6.0,50.0),(8.0,26.0),(8.5,46.5),(9.0,22.0),(10.5,4.5),(10.5,43.0),(10.5,50.0),(12.5,46.5),(14.5,50.0),(16.5,21.5),(16.5,45.5))
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
