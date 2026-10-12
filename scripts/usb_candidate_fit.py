# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Make an isolated connector-fit coupon; never alter the routed board.

Run with KiCad's Python. The coupon retains all Pico headers, castellations,
mounting holes and outline. Electrical routing and cable fit are not certified
by its DRC result. Exit normally; no routing process is started here.
"""
import hashlib
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hardware.design import MECHANICAL
from hardware.sexp import parse, children, one, dump, Atom


def prepare_footprint(out):
    source = ROOT / 'hardware/research/usb-c/USB_C_Receptacle_G-Switch_GT-USB-7010ASV.kicad_mod'
    if hashlib.sha256(source.read_bytes()).hexdigest() != 'f5b0d469bf30aead721a8f87fcc7662ce857ef13cf65be66ab09c6d7a686c5f2':
        raise ValueError('Re-review the connector footprint before changing the fit coupon')
    doc = parse(source.read_text())
    doc[:] = [v for v in doc if not (isinstance(v, list) and (
        v[0] == 'model' or
        (v[0] == 'pad' and v[1] in {'B1', 'B4', 'B9', 'B12'}) or
        (v[0] == 'fp_line' and one(v, 'layer')[1] == 'F.CrtYd')))]
    for pad in children(doc, 'pad'):
        if pad[2] == 'smd':
            # Shift the SMT row 25 um tailward, within
            # the drawing's +/-50 um recommended-land-pattern tolerance.
            at = one(pad, 'at')
            at[2] = Atom(str(float(at[2]) - .025))
        pad[1] = {'A1': 'A1B12', 'A4': 'A4B9', 'A9': 'B4A9',
                  'A12': 'B1A12'}.get(pad[1], pad[1])
    # Follow the shell and stake lands with a 0.10 mm allowance instead of
    # the stock oversized rectangular courtyard. This is not a screw keepout.
    contour = [(-4.57, 3.775), (4.57, 3.775), (4.57, 2.075),
               (4.92, 2.075), (4.92, -4.6), (-4.92, -4.6),
               (-4.92, 2.075), (-4.57, 2.075)]
    for a, b in zip(contour, contour[1:] + contour[:1]):
        doc.append(parse(f'(fp_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) '
                         '(stroke (width 0.05) (type solid)) (layer "F.CrtYd"))'))
    (out / source.name).write_text(dump(doc) + '\n')
    return out


def point(x, y):
    import pcbnew as k
    return k.VECTOR2I(round(x * 1_000_000), round(y * 1_000_000))


def main():
    import wx
    import pcbnew as k
    app = wx.App(False)
    out = ROOT / 'build/usb-fit'
    out.mkdir(parents=True, exist_ok=True)
    prepare_footprint(out)
    board = k.BOARD()
    board.GetDesignSettings().SetBoardThickness(k.FromMM(MECHANICAL.thickness))
    for folder, name, ref, position, rotation in (
        ('hardware/lib/ch32-pico.pretty', 'Pico_Header', 'J1', (0, 0), 0),
        ('build/usb-fit', 'USB_C_Receptacle_G-Switch_GT-USB-7010ASV',
         'J2', (10.5, 4.825), 180),
    ):
        fp = k.FootprintLoad(str(ROOT / folder), name)
        if fp is None:
            raise ValueError(f'Cannot load {name}')
        fp.SetReference(ref)
        fp.SetPosition(point(*position))
        fp.SetOrientationDegrees(rotation)
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        for item in fp.GraphicalItems():
            if item.GetLayer() == k.F_SilkS:
                item.SetLayer(k.F_Fab)
        board.Add(fp)
    corners = [(0, 0), (21, 0), (21, 51), (0, 51)]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        edge = k.PCB_SHAPE(board)
        edge.SetShape(k.SHAPE_T_SEGMENT)
        edge.SetStart(point(*a))
        edge.SetEnd(point(*b))
        edge.SetLayer(k.Edge_Cuts)
        edge.SetWidth(k.FromMM(.05))
        board.Add(edge)
    path = out / 'gswitch.kicad_pcb'
    k.SaveBoard(str(path), board)
    # Match the existing board's manufacturing floors, without DRC exclusions.
    shutil.copyfile(ROOT / 'hardware/review/ch32-pico.kicad_pro', path.with_suffix('.kicad_pro'))
    shutil.copyfile(ROOT / 'hardware/review/ch32-pico.kicad_dru', path.with_suffix('.kicad_dru'))
    print(path)


if __name__ == '__main__':
    main()
