# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""USBLC6-2P6 land pattern from ST DS4260 Rev 7, Figure 21 (millimeters).

Pad numbering follows the datasheet top view. This orientation places pin 1
at bottom left and pin 6 at top left, matching the board's flow-through routing.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hardware.sexp import parse,dump

NAME='ST_USBLC6-2P6_SOT666'
DEST=Path(__file__).resolve().parents[1]/'hardware/lib/ch32-pico.pretty'


def main():
    lines=[f'(footprint "{NAME}" (version 20241229) (generator "ch32-pico") (layer "F.Cu")',
        '(descr "ST DS4260 Rev 7 Figure 21: 0.30 x 0.99 lands, 0.50 pitch, 0.62 inner gap")',
        '(attr smd)',
        '(fp_text reference "REF**" (at 0 -2) (layer "F.SilkS") (effects (font (size .7 .7) (thickness .12))))',
        f'(fp_text value "{NAME}" (at 0 2) (layer "F.Fab") (effects (font (size .7 .7) (thickness .12))))',
        '(fp_rect (start -.85 -.85) (end .85 .85) (stroke (width .1) (type solid)) (fill none) (layer "F.Fab"))',
        '(fp_circle (center -.55 .5) (end -.45 .5) (stroke (width .1) (type solid)) (fill none) (layer "F.Fab"))',
        '(fp_rect (start -1.05 -1.5) (end 1.05 1.5) (stroke (width .05) (type solid)) (fill none) (layer "F.CrtYd"))']
    for number,x,y in [(1,-.5,.805),(2,0,.805),(3,.5,.805),(4,.5,-.805),(5,0,-.805),(6,-.5,-.805)]:
        lines.append(f'(pad "{number}" smd rect (at {x} {y}) (size .3 .99) (layers "F.Cu" "F.Paste" "F.Mask"))')
    lines.append(')')
    (DEST/(NAME+'.kicad_mod')).write_text(dump(parse('\n'.join(lines)))+'\n')


if __name__=='__main__':main()
