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
    parser.add_argument('--only-locked',action='store_true',
                        help='Allow the router to replace unlocked signal copper; preserve locked power/USB geometry')
    args=parser.parse_args()
    app=wx.App(False)
    source=args.board.resolve()
    if args.action=='export':
        # The overlapping castellations and round header lands are already
        # connected copper. Give the router only the inboard header terminals,
        # so it cannot start a new trace on the board edge. The SES is imported
        # into the ORIGINAL board, whose castellations remain unchanged.
        from .sexp import parse,children,dump
        from .fabrication import copy_rules
        doc=parse(source.read_text())
        for fp in children(doc,'footprint'):
            fp[:]=[p for p in fp if not (isinstance(p,list) and p[0]=='pad' and
                any(v[1]=='pad_prop_castellated' for v in children(p,'property')))]
        source=args.exchange.resolve().with_suffix('.export.kicad_pcb')
        source.write_text(dump(doc)+'\n')
        copy_rules(args.board.resolve(),source)
    board=k.LoadBoard(str(source))
    # SES is a routing delta: fixed input copper may be omitted. Preserve the
    # exact same input tracks on import that were declared fixed on export.
    if not args.only_locked:
        for t in board.GetTracks():t.SetLocked(True)
    if args.action=='export':
        if not k.ExportSpecctraDSN(board,str(args.exchange)):raise SystemExit('DSN export failed')
    else:
        if not args.output:parser.error('--output is required for import')
        if not k.ImportSpecctraSES(board,str(args.exchange)):raise SystemExit('SES import failed')
        k.ZONE_FILLER(board).Fill(board.Zones())
        k.SaveBoard(str(args.output),board)


if __name__=='__main__':main()
