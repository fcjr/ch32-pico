# SPDX-License-Identifier: MIT
"""Rev E local GND stitching, ordinary tented through vias without paste.

Two vias join the connector-region back pour to L2. The ESD array retains
its existing short local ground via. No board-wide fence or switch-node copper.
"""
from .sexp import parse
from .schematic import uid

VIAS=((5.5,7.8),(14.5,7.55))


def apply(doc):
    for i,(x,y) in enumerate(VIAS):
        doc.append(parse(f'''(via (at {x} {y}) (size .45) (drill .2)
            (layers "F.Cu" "B.Cu") (net "GND") (locked yes)
            (tenting front back) (uuid "{uid(f'reve/stitch/{i}')}"))'''))
