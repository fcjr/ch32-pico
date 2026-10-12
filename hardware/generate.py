# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Generate a mechanical KiCad template and proposed pinout, without pcbnew.

No target/programmer circuit or routing is emitted by this mechanical-only generator. Stable UUIDs and no timestamps keep generated files reproducible.
"""

import csv
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from .design import HEADER, MECHANICAL, POWER_REQUIREMENTS, TARGET_PINS, validate
from .parts import export_candidates


ROOT = Path(__file__).resolve().parents[1]


def uid(name: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"ch32-pico/mechanical/{name}"))


def footprint(castellations=False) -> str:
    m = MECHANICAL
    lines = [
        '(footprint "Pico_Header_Mechanical" (version 20241229) (generator "ch32_pico")',
        '  (layer "F.Cu")',
        '  (descr "Pico 40-pin header and mounting holes. Mechanical template only.")',
        '  (attr through_hole exclude_from_pos_files exclude_from_bom)',
        '  (property "Reference" "J1" (at 10.5 22) (layer "F.Fab")',
        '    (effects (font (size 1 1))))',
        '  (property "Value" "MECHANICAL ONLY" (at 10.5 25) (layer "F.Fab")',
        '    (effects (font (size 0.8 0.8))))',
    ]
    for p in HEADER:
        x, y = m.position(p.number)
        shape = "rect" if p.number == 1 else "circle"
        lines.append(
            f'  (pad "{p.number}" thru_hole {shape} (at {x} {y}) '
            f'(size {m.header_pad} {m.header_pad}) (drill {m.header_drill}) '
            f'(layers "*.Cu" "*.Mask") (uuid "{uid(f"pad-{p.number}")}"))'
        )
        if castellations:
            edge_x=0 if p.number<=20 else m.width
            lines.append(
                f'  (pad "{p.number}" thru_hole rect (at {edge_x} {y}) '
                f'(size 2 1.7) (drill 0.6) (property pad_prop_castellated) '
                f'(layers "*.Cu" "*.Mask") (uuid "{uid(f"castellation-{p.number}")}"))'
            )
    for i, (x, y) in enumerate(m.mounting_holes):
        lines.append(
            f'  (pad "" np_thru_hole circle (at {x} {y}) '
            f'(size {m.mounting_drill} {m.mounting_drill}) (drill {m.mounting_drill}) '
            f'(layers "*.Cu" "*.Mask") (uuid "{uid(f"hole-{i}")}"))'
        )
    lines.append(')')
    return "\n".join(lines) + "\n"


def board(fp: str) -> str:
    m = MECHANICAL
    head = f'''(kicad_pcb (version 20241229) (generator "ch32_pico")
  (general (thickness {m.thickness}))
  (paper "A4")
  (layers
    (0 "F.Cu" signal) (2 "B.Cu" signal)
    (9 "F.Adhes" user "F.Adhesive") (13 "F.Paste" user)
    (5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
    (1 "F.Mask" user) (3 "B.Mask" user)
    (25 "Edge.Cuts" user) (49 "F.Fab" user))
  (setup (pad_to_mask_clearance 0))
'''
    # KiCad 9+ layer IDs. This template has two copper layers, not the final stackup.
    outline = []
    corners = [(0, 0), (m.width, 0), (m.width, m.length), (0, m.length)]
    for i, (a, b) in enumerate(zip(corners, corners[1:] + corners[:1])):
        outline.append(
            f'  (gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) '
            f'(stroke (width 0.05) (type default)) (layer "Edge.Cuts") '
            f'(uuid "{uid(f"edge-{i}")}"))'
        )
    return head + fp + "\n".join(outline) + "\n)\n"


def generate() -> None:
    validate()
    out = ROOT / "build"
    out.mkdir(exist_ok=True)
    export_candidates(ROOT)
    fp = footprint()
    electrical_fp=footprint(castellations=True).replace('Pico_Header_Mechanical','Pico_Header').replace('MECHANICAL ONLY','Pico header').replace('Mechanical template only.','Castellated edge pads overlap the header lands.')
    (ROOT/'hardware/lib/ch32-pico.pretty/Pico_Header.kicad_mod').write_text(electrical_fp)
    (out / "ch32-pico-mechanical.kicad_pcb").write_text(board(fp))
    with (out / "proposed-pinout.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["physical_pin", "pico_function", "proposed_net", "target_package_pin", "x_mm", "y_mm", "notes"])
        for p in HEADER:
            w.writerow([p.number, p.pico, p.proposed, TARGET_PINS.get(p.proposed, ""), *MECHANICAL.position(p.number), p.function])
    manifest = {
        "status": "mechanical template; proposed pinout; no electrical circuit or routing",
        "width_mm": MECHANICAL.width,
        "length_mm": MECHANICAL.length,
        "thickness_mm": MECHANICAL.thickness,
        "header_positions": {str(p.number): MECHANICAL.position(p.number) for p in HEADER},
        "mounting_holes_mm": MECHANICAL.mounting_holes,
        "castellations": "40 generated in Pico_Header; mechanical-only template omits them",
        "programmer": "CH32V003 / open rv003usb; external SWIO factory flash",
        "power_requirements_unverified": POWER_REQUIREMENTS,
    }
    (out / "design-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    pinout = [
        "# Proposed Pico compatibility map", "",
        "Generated from hardware/design.py. Proposed connections, not a validated circuit.", "",
        "| Physical pin | Pico | CH32 net | CH32 package pin | Function / limitation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p in HEADER:
        pinout.append(f"| {p.number} | {p.pico} | {p.proposed} | {TARGET_PINS.get(p.proposed, '-')} | {p.function} |")
    (out / "proposed-pinout.md").write_text("\n".join(pinout) + "\n")
    print("Generated mechanical PCB, proposed pinout, candidate parts, and manifest in build/")


if __name__ == "__main__":
    generate()
