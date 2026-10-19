# SPDX-License-Identifier: MIT
"""GND stitching: ordinary tented through vias, outside paste.

One via joins the connector-region back pour to L2; 14 more tie the back
pour to the ground plane on a clearance-filtered grid, including through the
3.3 V inner pour where it is wide. There is no board-wide fence.
"""
from .sexp import parse
from .schematic import uid

VIAS=((14.5,7.55),(3.0,1.5),(6.0,42.0),(6.5,50.0),(8.0,9.0),(8.5,13.0),(9.0,45.5),(10.5,4.5),(10.5,41.5),(12.0,50.0),(12.5,37.0),(14.5,40.5),(16.5,27.5),(16.5,46.0),(17.5,50.0))
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
