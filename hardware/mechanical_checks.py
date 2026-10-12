# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Check the selected G-Switch connector against the Pico mounting geometry.

The drawing gives a reference mating gap, not a guaranteed minimum. These
checks establish nominal placement only; cable fit requires prototypes.
"""
import math
from .sexp import children, one

MPN = 'GT-USB-7010AW'
DRAWING_URL = 'https://www.lcsc.com/datasheet/C963411.pdf'
MATED_GAP_REFERENCE = 1.85
EDGE_ALLOWANCE = .20
PLACEMENT_ALLOWANCE = .10
MOUTH_ALLOWANCE = .15


def usb_fit(doc):
    footprints = {next(p[2] for p in children(fp, 'property') if p[1] == 'Reference'): fp
                  for fp in children(doc, 'footprint')}
    fp = footprints['J2']
    props = {p[1]: p[2] for p in children(fp, 'property')}
    expected = 'USB_C_Receptacle_G-Switch_GT-USB-7010AW'
    if props.get('Value') != MPN or not str(fp[1]).endswith(expected):
        raise ValueError('USB mechanical model requires the reviewed G-Switch part')
    at = one(fp, 'at')
    x, y = map(float, at[1:3])
    if len(at) < 4 or float(at[3]) % 360 != 180:
        raise ValueError('USB mechanical model expects a front-facing connector')
    expected_edges = {((-4.47,-3.675),(-4.47,3.675)),
                      ((-4.47,-3.675),(4.47,-3.675)),
                      ((-4.47,3.675),(4.47,3.675)),
                      ((4.47,3.675),(4.47,-3.675))}
    edges = {(tuple(map(float,one(r,'start')[1:3])),
              tuple(map(float,one(r,'end')[1:3]))) for r in children(fp,'fp_line')
             if one(r,'layer')[1]=='F.Fab'}
    if not expected_edges.issubset(edges):
        raise ValueError('USB shell outline differs from reviewed drawing')
    left, right, front, rear = x-4.47, x+4.47, y-3.675, y+3.675
    if not math.isclose(front,1.15,abs_tol=1e-6):
        raise ValueError('Unreviewed USB recess')
    holes = []
    for p in children(footprints['J1'], 'pad'):
        if p[2] != 'np_thru_hole':
            continue
        hx, hy = map(float, one(p, 'at')[1:3])
        radius = float(one(p, 'drill')[1])/2
        distance = math.hypot(max(left-hx, hx-right, 0), max(front-hy, hy-rear, 0))
        clearance = distance-radius
        if clearance < 0:
            raise ValueError('USB shell overlaps a Pico mounting hole')
        holes.append({'center_mm': [hx, hy], 'nominal_shell_clearance_mm': round(clearance, 4),
                      'head_diameter_at_shell_contact_mm': round(2*distance, 4)})
    return {'part': MPN, 'lcsc': 'C963411', 'drawing': DRAWING_URL,
            'mouth_recess_mm': round(front, 4), 'minimum_mated_gap_mm': None,
            'reference_mated_gap_mm': MATED_GAP_REFERENCE,
            'nominal_cable_margin_mm': MATED_GAP_REFERENCE-front,
            'remaining_cable_margin_mm': None,
            'allowances_mm': {'board_edge': EDGE_ALLOWANCE, 'assembly_position': PLACEMENT_ALLOWANCE,
                              'mouth_position': MOUTH_ALLOWANCE},
            'mounting_holes': holes, 'upper_screw_heads_compatible': False,
            'physical_fit_tested': False}
