# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Deterministic silkscreen artwork, independent of copper and routing."""
from .schematic import uid
from .design import BOARD_REVISION
from .sexp import children, one, parse, dump


def artwork():
    nodes = []
    for label, x, y, size, side in [('ch32-pico', 10.5, 27.3, .9, 'B'),
                              (f'REV {BOARD_REVISION}', 10.5, 28.9, .8, 'B'),
                              ('LEFT SHIFT', 10.5, 46.5, .8, 'B'),
                              ('LOGICAL', 10.5, 47.8, .8, 'B'),
                              ('VBUS 5-20V',10.5,13.0,.8,'B')]:
        mirror='(justify mirror)' if side=='B' else ''
        nodes.append(parse(f'''(gr_text "{label}" (at {x} {y}) (layer "{side}.SilkS")
            (uuid "{uid('brand/text/' + label)}")
            (effects (font (size {size} {size}) (thickness 0.15)) {mirror}))'''))
    # Separate the brand from the center test points. Mirrored geometry reads
    # as left chevrons beside LOGICAL when viewed from the back.
    for index, x in enumerate((13.4, 14.0)):
        for half, (a, b) in enumerate((((x, 47.5), (x+.3, 47.8)),
                                       ((x+.3, 47.8), (x, 48.1)))):
            nodes.append(parse(f'''(gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]})
                (stroke (width 0.18) (type solid)) (layer "B.SilkS")
                (uuid "{uid(f'brand/chevron/{index}/{half}')}"))'''))
    return nodes


def apply(doc):
    """Replace only the managed artwork; repeated builds are idempotent."""
    marks = artwork()
    ids = {one(n, 'uuid')[1] for n in marks}
    # Replace any existing logo strokes when updating a saved board.
    ids |= {uid(f'brand/chevron/{index}/{half}') for index in range(2) for half in range(2)}
    labels = {'ch32-pico', 'LEFT SHIFT', 'LOGICAL', 'VBUS 5-20V'}
    doc[:] = [n for n in doc if not (isinstance(n, list) and n and (
        (n[0] == 'gr_text' and (n[1] in labels or n[1].startswith('REV '))) or
        (n[0] == 'gr_line' and children(n, 'uuid') and one(n, 'uuid')[1] in ids)))]
    doc.extend(marks)


def update(path):
    doc = parse(path.read_text())
    apply(doc)
    path.write_text(dump(doc) + '\n')
