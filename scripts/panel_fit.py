# SPDX-License-Identifier: MIT
"""Check the final KiKit outline for substrate under each USB overhang."""
import json
from pathlib import Path
import sys
import wx

app = wx.App(False)
import pcbnew
from kikit.substrate import Substrate
from shapely.geometry import box


def main():
    board = pcbnew.LoadBoard(str(Path(sys.argv[1]).resolve()))
    if board is None:
        raise ValueError('Cannot load panel for connector-fit audit')
    outline = Substrate([d for d in board.GetDrawings()
                         if d.GetLayer() == pcbnew.Edge_Cuts]).substrates
    results = []
    mm = 1_000_000
    for fp in board.GetFootprints():
        if not fp.GetReference().endswith('_J2'):
            continue
        if fp.GetOrientationDegrees() % 360 != 180:
            raise ValueError('Unexpected USB orientation on panel')
        p = fp.GetPosition()
        # Connector mouth is 0.30 mm beyond the finished board. Exclude the
        # shared boundary itself; include the entire mouth width and overhang.
        overhang = box(p.x - 4.47*mm, p.y - 3.675*mm,
                       p.x + 4.47*mm, p.y - 3.375*mm - 1)
        overlap = outline.intersection(overhang).area / mm**2
        if overlap > 1e-6:
            raise ValueError(f'Panel substrate obstructs {fp.GetReference()}: {overlap} mm²')
        results.append({'connector': fp.GetReference(), 'substrate_overlap_mm2': round(overlap, 6)})
    if len(results) != 4:
        raise ValueError('Expected four panel USB connectors')
    Path(sys.argv[2]).write_text(json.dumps({'passes': True, 'connectors': results}, indent=2)+'\n')


if __name__ == '__main__':
    main()
