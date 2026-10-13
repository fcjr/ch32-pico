# SPDX-License-Identifier: MIT
"""Geometric checks against JLC's published Standard PCBA rail guidance.

Sources and review date are recorded in docs/factory-review.md. Passing these
checks does not approve factory part models, stencil processing or allocation.
"""
from .sexp import children, one


def panel_tooling(doc):
    points = [tuple(map(float, one(n, key)[1:3]))
              for kind in ('gr_line', 'gr_arc') for n in children(doc, kind)
              if one(n, 'layer')[1] == 'Edge.Cuts'
              for key in ('start', 'mid', 'end') if children(n, key)]
    left, top = (min(p[i] for p in points) for i in (0, 1))
    right, bottom = (max(p[i] for p in points) for i in (0, 1))
    holes, fiducials = [], []
    for fp in children(doc, 'footprint'):
        ref = next(p[2] for p in children(fp, 'property') if p[1] == 'Reference')
        if not ref.startswith(('KiKit_TO_', 'KiKit_FID_')):
            continue
        pad = one(fp, 'pad')
        x, y = map(float, one(fp, 'at')[1:3])
        edge_distance = min(x-left, right-x, y-top, bottom-y)
        diameter = min(map(float, one(pad, 'size')[1:3]))
        layers = one(pad, 'layers')[1:]
        if ref.startswith('KiKit_TO_'):
            drill = float(one(pad, 'drill')[1])
            if pad[2] != 'np_thru_hole' or drill < 2-1e-6:
                raise ValueError(f'{ref}: Standard PCBA tooling needs 2 mm NPTH')
            holes.append({'ref': ref, 'drill_mm': drill})
        else:
            margin = float(one(pad, 'solder_mask_margin')[1]) if children(pad, 'solder_mask_margin') else 0
            opening = diameter + 2*margin
            if abs(diameter-1) > 1e-6 or opening < 2-1e-6:
                raise ValueError(f'{ref}: use 1 mm copper and at least 2 mm mask opening')
            if edge_distance - opening/2 < 3.35-1e-3:
                raise ValueError(f'{ref}: fiducial opening too close to conveyor edge')
            if any('Paste' in layer for layer in layers):
                raise ValueError(f'{ref}: fiducial must not receive paste')
            fiducials.append({'ref': ref, 'copper_mm': diameter,
                              'mask_opening_mm': opening,
                              'opening_to_outer_edge_mm': round(edge_distance-opening/2, 4)})
    if len(holes) != 3 or len([f for f in fiducials if '_T_' in f['ref']]) != 3:
        raise ValueError('Expected three tooling holes and three top fiducials')
    return {'passes': True, 'tooling': holes, 'fiducials': fiducials}
