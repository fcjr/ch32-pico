# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Generate a physical pin/polarity guide, without guessing JLC angle offsets."""
import csv
import hashlib
import html
import json
from .circuit import COMPONENTS
from .library import ROOT, load_library
from .order_review import checked_board
from .sexp import parse, children, one
from .usb_review import pad_centers

# Explicit orientation anchors; LED numbering differs from the discrete diode.
ANCHORS = {
    'J2': ('A6', 'D+ contact A6; socket mouth faces the short USB edge'),
    'D1': ('1', 'Cathode / band, VSYS (anode goes to USB VBUS)'),
    'D2': ('1', 'Pin 1, USB D+; pin 2 GND and pin 5 VBUS'),
    'Q1': ('1', 'Pin 1, gate; pin 2 source GND, pin 3 drain'),
    'U2': ('1', 'Pin 1 / dot, programmer PD4 (USB D+)'),
    'U1': ('1', 'Pin 1 / dot, target PD4'),
    'D3': ('2', 'Cathode, GND; pin 1 is the LED anode'),
    'SW1': ('1', 'Contact 1, target RESET; contact 2 GND'),
    'U4': ('1', 'Pin 1, VIN; pin 2 GND; pin 5 main 3.3 V'),
    'U5': ('1', 'Pin 1, VIN; pin 2 GND; pin 5 target 3.3 V'),
}


def report():
    board = checked_board(); doc = parse(board.read_text()); pads = pad_centers(doc)
    fitted = {c.ref: c for c in COMPONENTS if c.fitted}; lib = load_library()
    fps = {next(p[2] for p in children(fp, 'property') if p[1] == 'Reference'): fp
           for fp in children(doc, 'footprint')}
    panel_dir = ROOT / 'build/panel-preview'
    manifest = json.loads((panel_dir / 'manifest.json').read_text())
    if manifest['source_board_sha256'] != hashlib.sha256(board.read_bytes()).hexdigest():
        raise ValueError('Stale panel source')
    cpl_path = panel_dir / 'cpl.csv'
    if hashlib.sha256(cpl_path.read_bytes()).hexdigest() != manifest['file_sha256']['cpl.csv']:
        raise ValueError('Panel CPL changed after validation')
    with cpl_path.open() as f:
        cpl_rows = list(csv.DictReader(f))
    cpl = {r['Designator']: r for r in cpl_rows}
    if len(cpl) != len(cpl_rows):
        raise ValueError('Duplicate CPL references')
    expected = {copy['prefix'] + ref for copy in manifest['copies'] for ref in fitted}
    if cpl.keys() != expected:
        raise ValueError('CPL fitted reference coverage mismatch')
    rows = []
    for ref, c in fitted.items():
        fp = fps[ref]; at = one(fp, 'at'); x, y = map(float, at[1:3])
        angle = float(at[3]) if len(at) > 3 else 0
        terminals = []
        for pad in children(fp, 'pad'):
            if not pad[1]:
                continue
            net = one(pad, 'net')[-1] if children(pad, 'net') else None
            # KiCad labels NC pads with an unconnected net. Only connected
            # terminals can be compared literally to the circuit source.
            if c.nets[str(pad[1])] is not None and net != c.nets[str(pad[1])]:
                raise ValueError(f'Unexpected pad net at {ref}.{pad[1]}')
            terminals.append({'pin': str(pad[1]), 'net': c.nets[str(pad[1])],
                              'board_xy_mm': pads[ref, str(pad[1])]})
        copies = []
        for copy in manifest['copies']:
            panel_ref = copy['prefix'] + ref; dx, dy = copy['translation_mm']; row = cpl[panel_ref]
            if (abs(float(row['Mid X']) - x - dx) > 1e-5
                or abs(float(row['Mid Y']) + y + dy) > 1e-5
                or (float(row['Rotation']) - angle) % 360 != 0 or row['Layer'] != 'top'):
                raise ValueError(f'CPL mismatch at {panel_ref}')
            anchor = ANCHORS.get(ref)
            point = pads[ref, anchor[0]] if anchor else None
            copies.append({'ref': panel_ref, 'cpl_center_mm': [float(row['Mid X']), float(row['Mid Y'])],
                'anchor_cpl_xy_mm': [round(point[0] + dx, 6), round(-point[1] - dy, 6)] if point else None})
        rows.append({'ref': ref, 'lcsc': c.part, 'mpn': lib[c.part].mpn,
                     'board_center_mm': [x, y], 'kicad_angle_deg': angle,
                     'orientation_anchor': ANCHORS.get(ref), 'terminals': terminals, 'panel_copies': copies})
    return {'status': 'physical pin guide; JLC model orientations remain unverified',
            'source_board_sha256': hashlib.sha256(board.read_bytes()).hexdigest(),
            'panel_sha256': manifest['panel_sha256'], 'cpl_sha256': manifest['file_sha256']['cpl.csv'],
            'coordinate_convention': 'Board: X right, Y down from upper-left. CPL: X right, Y up from panel origin.',
            'fitted_parts_per_board': len(rows), 'panel_cpl_rows_checked': len(cpl),
            'jlc_model_rotations_verified': False, 'parts': rows}, doc


def svg_guide(result, doc):
    e = html.escape
    parts = {r['ref']: r for r in result['parts']}
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="820" viewBox="0 0 1100 820">',
        '<rect width="1100" height="820" fill="white"/>',
        '<g font-family="sans-serif" fill="#17263c">',
        '<text x="35" y="36" font-size="24" font-weight="bold">ch32-pico — assembly orientation guide</text>',
        '<text x="35" y="63" font-size="14">Top view · USB at top · physical anchors, not approved JLC model angles</text>',
        '<text x="35" y="87" font-size="12">Orange marks show the specific pad named at right. Dimensions are board coordinates in mm.</text>',
        '<g transform="translate(40 115) scale(12)">',
        '<rect width="21" height="51" fill="#edf2f5" stroke="#26394f" stroke-width="0.12"/>']
    for fp in children(doc, 'footprint'):
        ref = next(p[2] for p in children(fp, 'property') if p[1] == 'Reference')
        at = one(fp, 'at'); x, y = map(float, at[1:3]); angle = float(at[3]) if len(at) > 3 else 0
        if ref not in parts and ref != 'J1':
            continue
        svg.append(f'<g transform="translate({x} {y}) rotate({-angle})">')
        for line in children(fp, 'fp_line'):
            if one(line, 'layer')[1] != 'F.Fab':
                continue
            a, b = one(line, 'start'), one(line, 'end')
            svg.append(f'<line x1="{a[1]}" y1="{a[2]}" x2="{b[1]}" y2="{b[2]}" stroke="#64748b" stroke-width="0.09"/>')
        for pad in children(fp, 'pad'):
            at = one(pad, 'at'); px, py = map(float, at[1:3]); w, h = map(float, one(pad, 'size')[1:3])
            # Saved pad angle is absolute; the enclosing group already rotates.
            pa = float(at[3]) if len(at) > 3 else 0
            svg.append(f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" '
                       f'transform="translate({px} {py}) rotate({angle-pa})" fill="#9aa9b4" stroke="white" stroke-width="0.025"/>')
            if children(pad, 'drill'):
                drill = one(pad, 'drill')
                if drill[1] == 'oval':
                    dw, dh = map(float, drill[2:4])
                else:
                    dw = dh = float(drill[1])
                svg.append(f'<rect x="{-dw/2}" y="{-dh/2}" width="{dw}" height="{dh}" '
                           f'rx="{min(dw,dh)/2}" transform="translate({px} {py}) rotate({angle-pa})" fill="white"/>')
        svg.append('</g>')
        if ref in ANCHORS:
            svg.append(f'<text x="{x}" y="{y-.25}" text-anchor="middle" font-size="0.7" fill="#14243a">{ref}</text>')
    for ref, (pin, _) in ANCHORS.items():
        p = next(t for t in parts[ref]['terminals'] if t['pin'] == pin)['board_xy_mm']
        svg.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="0.29" fill="#f27a21" stroke="#8f3d00" stroke-width="0.06"/>')
    svg.append('<path d="M10.5 1.1 V-1 M10 -0.5 L10.5 -1 L11 -0.5" fill="none" stroke="#f27a21" stroke-width="0.15"/>')
    svg.append('</g>')
    for i, (ref, (pin, note)) in enumerate(ANCHORS.items()):
        row = parts[ref]; terminal = next(t for t in row['terminals'] if t['pin'] == pin)
        x, y = terminal['board_xy_mm']; top = 124 + 56 * i
        svg.append(f'<text x="330" y="{top}" font-size="16" font-weight="bold">{ref} · {e(row["mpn"])}</text>')
        svg.append(f'<text x="330" y="{top+19}" font-size="13">{e(note)}</text>')
        svg.append(f'<text x="330" y="{top+36}" font-size="12" fill="#58677a">Pad {pin}: x={x:.4f}, y={y:.4f} · {e(terminal["net"] or "NC")} · KiCad {row["kicad_angle_deg"]:g}°</text>')
    svg += ['<text x="330" y="712" font-size="13">Resistors and ceramic capacitors have no polarity.</text>',
            '<text x="330" y="734" font-size="13">Use the JSON companion for all 132 panel placements and anchor coordinates.</text>',
            '<text x="35" y="783" font-size="12">Compare actual pad numbering and body marks in JLC preview; a red model dot alone is not proof of pin 1.</text>',
            '</g></svg>']
    return '\n'.join(svg) + '\n'


def main():
    result, doc = report(); out = ROOT / 'build/order-review'; out.mkdir(exist_ok=True)
    (out / 'assembly-orientation.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / 'assembly-orientation.svg').write_text(svg_guide(result, doc))
    print(f"Physical assembly guide: {result['fitted_parts_per_board']} parts; "
          f"{result['panel_cpl_rows_checked']} panel positions checked; JLC rotations pending")


if __name__ == '__main__':
    main()
