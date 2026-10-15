# SPDX-License-Identifier: MIT
"""Prepare a provisional four-window stencil for the 2.7 mm U3 exposed pad."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hardware.sexp import parse,dump,children,one
from hardware.library import ROOT


def main():
    path=ROOT/'hardware/lib/ch32-pico.pretty/VQFN-24_L4.0-W4.0-P0.50-TL-EP2.7.kicad_mod'
    doc=parse(path.read_text())
    ep=next(p for p in children(doc,'pad') if p[1]=='25')
    one(ep,'layers')[:]=parse('(layers "F.Cu" "F.Mask")')
    doc[:]=[p for p in doc if not (isinstance(p,list) and p[0]=='pad' and p[1]=='')]
    # Geometry originally follows TI drawing 4219016/A for a same-size EP.
    # This is not a Maxin process recommendation. Four 1.188 mm squares at
    # +/-0.694 mm give 78% coverage. Factory review of a 0.125 mm stencil
    # and solder/joint qualification on the actual MX26631 package are required.
    for x in (-.694,.694):
        for y in (-.694,.694):
            doc.append(parse(f'(pad "" smd roundrect (at {x} {y}) (size 1.188 1.188) (layers "F.Paste") (roundrect_rratio 0.0420875))'))
    path.write_text(dump(doc)+'\n')


if __name__=='__main__':main()
