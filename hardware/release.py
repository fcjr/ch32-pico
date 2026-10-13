# SPDX-License-Identifier: MIT
"""Reject stale revision artifacts before manufacturing or presentation exports."""
import json
from .design import BOARD_REVISION
from .library import ROOT
from .sexp import parse,children


def require_current_layout():
    path=ROOT/'hardware/review/ch32-pico.kicad_pcb'
    if not path.exists():raise ValueError('No reviewed layout exists for the current revision')
    doc=parse(path.read_text())
    if f'REV {BOARD_REVISION}' not in {n[1] for n in children(doc,'gr_text')}:
        raise ValueError(f'Saved layout is not Rev {BOARD_REVISION}. Finish routing and review before export; older revision files cannot manufacture the current board.')
    from .verify_placement import verify_board
    verify_board(path)
