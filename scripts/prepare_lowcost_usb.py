# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Reproduce the selected USB land pattern from the pinned library input."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.usb_candidate_fit import prepare_footprint
from hardware.sexp import parse, children, one, dump


def main():
    directory = ROOT / 'hardware/lib/ch32-pico.pretty'
    prepare_footprint(directory)
    path = directory / 'USB_C_Receptacle_G-Switch_GT-USB-7010ASV.kicad_mod'
    doc = parse(path.read_text())
    for pad in children(doc, 'pad'):
        if pad[1] == 'SH':
            x, y = map(float, one(pad, 'at')[1:3])
            pad[1] = str(1 if x > 0 and y < 0 else 2 if x > 0 else 3 if y > 0 else 4)
    def fabrication_layers(node):
        if not isinstance(node, list):
            return
        if node and node[0] == 'layer' and node[1] == 'F.SilkS':
            node[1] = 'F.Fab'
        for child in node:
            fabrication_layers(child)
    fabrication_layers(doc)
    path.write_text(dump(doc) + '\n')


if __name__ == '__main__':
    main()
