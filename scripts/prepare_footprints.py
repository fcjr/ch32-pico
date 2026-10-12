# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""One-time vendoring of selected KiCad 10 footprints and local pin aliases.

Normal builds use the checked-in results, not the workstation's library.
Run deliberately after reviewing any upstream library update.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hardware.sexp import parse,children,one,dump

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
DEST=ROOT/'hardware/lib/ch32-pico.pretty'
PARTS={'SOT-23-6':'Package_TO_SOT_SMD', 'TSSOP-20_4.4x6.5mm_P0.65mm':'Package_SO', 'LQFP-48_7x7mm_P0.5mm':'Package_QFP'}
ALIASES={'C7519':'SOT-23-6', 'C29779902':'LQFP-48_7x7mm_P0.5mm', 'C5187096':'TSSOP-20_4.4x6.5mm_P0.65mm'}


def main():
    for name,folder in PARTS.items():
        node=parse((SOURCE/(folder+'.pretty')/(name+'.kicad_mod')).read_text())
        node[:]=[v for v in node if not isinstance(v,list) or v[0]!='model']
        (DEST/(name+'.kicad_mod')).write_text(dump(node)+'\n')
    sym_path=ROOT/'hardware/lib/ch32-pico.kicad_sym'
    symbols=parse(sym_path.read_text())
    for s in children(symbols,'symbol'):
        props={p[1]:p for p in children(s,'property')}
        code=props['LCSC Part'][2]
        if code in ALIASES: props['Footprint'][2]='ch32-pico:'+ALIASES[code]
    sym_path.write_text(dump(symbols)+'\n')
    # Imported models were not downloaded. Remove all dangling 3D references.
    for path in DEST.glob('*.kicad_mod'):
        node=parse(path.read_text())
        node[:]=[v for v in node if not (isinstance(v,list) and v[0]=='model')]
        # Imported legends intrude on fine-pitch pads. Retain the drawings on
        # fabrication layers and add board-specific legends in the generator.
        def fabrication_layers(item):
            if not isinstance(item,list): return
            if item and item[0]=='layer' and item[1]=='F.SilkS': item[1]='F.Fab'
            for child in item: fabrication_layers(child)
        fabrication_layers(node)
        path.write_text(dump(node)+'\n')


if __name__=='__main__': main()
