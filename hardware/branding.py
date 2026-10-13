# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Deterministic silkscreen artwork, independent of copper and routing."""
from .schematic import uid
from .design import BOARD_REVISION
from .sexp import children, one, parse, dump


def artwork():
    nodes = []
    for label, x, y, size in [('ch32-pico', 10.5, 34.7, .9),
                              ('LEFT SHIFT', 10.5, 36.2, .8),
                              ('LOGICAL', 10.5, 37.4, .8),
                              (f'REV {BOARD_REVISION}', 10.5, 21.8, .8),
                              ('PDOUT 5-20V',10.5,45.2,.8)]:
        nodes.append(parse(f'''(gr_text "{label}" (at {x} {y}) (layer "F.SilkS")
            (uuid "{uid('brand/text/' + label)}")
            (effects (font (size {size} {size}) (thickness 0.15))))'''))
    # Double left-chevron mark from Left Shift Logical's original SVG.
    for index, x in enumerate((5.5, 6.3)):
        for half, (a, b) in enumerate((((x, 35.9), (x-.8, 36.7)),
                                       ((x-.8, 36.7), (x, 37.5)))):
            nodes.append(parse(f'''(gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]})
                (stroke (width 0.22) (type solid)) (layer "F.SilkS")
                (uuid "{uid(f'brand/chevron/{index}/{half}')}"))'''))
    return nodes


def apply(doc):
    """Replace only the managed artwork; repeated builds are idempotent."""
    marks = artwork()
    ids = {one(n, 'uuid')[1] for n in marks}
    labels = {'CH32 PICO', 'ch32-pico', 'LEFT SHIFT', 'LOGICAL', 'PDOUT 5-20V'}
    doc[:] = [n for n in doc if not (isinstance(n, list) and n and (
        (n[0] == 'gr_text' and (n[1] in labels or n[1].startswith('REV '))) or
        (n[0] == 'gr_line' and children(n, 'uuid') and one(n, 'uuid')[1] in ids)))]
    doc.extend(marks)


def update(path):
    doc = parse(path.read_text())
    apply(doc)
    path.write_text(dump(doc) + '\n')
