# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""DSN export / SES import, using KiCad's own native connectivity model."""
import argparse
from pathlib import Path
import wx
import pcbnew as k


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['export','import'])
    parser.add_argument('board',type=Path)
    parser.add_argument('exchange',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    app=wx.App(False)
    board=k.LoadBoard(str(args.board))
    # SES is a routing delta: fixed input copper may be omitted. Preserve the
    # exact same input tracks on import that were declared fixed on export.
    for t in board.GetTracks():t.SetLocked(True)
    if args.action=='export':
        if not k.ExportSpecctraDSN(board,str(args.exchange)):raise SystemExit('DSN export failed')
    else:
        if not args.output:parser.error('--output is required for import')
        if not k.ImportSpecctraSES(board,str(args.exchange)):raise SystemExit('SES import failed')
        k.ZONE_FILLER(board).Fill(board.Zones())
        k.SaveBoard(str(args.output),board)


if __name__=='__main__':main()
