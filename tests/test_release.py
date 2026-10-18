# SPDX-License-Identifier: MIT
"""Manufacturing must reject a saved board from an older revision."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from hardware.release import require_current_layout
from hardware.sexp import parse,children,dump
from hardware.verify_placement import verify_board


class ReleaseRevision(TestCase):
    def test_saved_board_cannot_keep_old_part_or_value(self):
        original=Path('hardware/review/ch32-pico.kicad_pcb').read_text()
        for ref,field,value in (('C1','LCSC Part','C1525'),('R1','Value','1k')):
            with self.subTest(ref=ref), TemporaryDirectory() as directory:
                doc=parse(original)
                fp=next(fp for fp in children(doc,'footprint') if any(
                    p[1:3]==['Reference',ref] for p in children(fp,'property')))
                next(p for p in children(fp,'property') if p[1]==field)[2]=value
                path=Path(directory)/'stale.kicad_pcb';path.write_text(dump(doc)+'\n')
                with self.assertRaisesRegex(ValueError,ref+': PCB part/value'):
                    verify_board(path)

    def test_stale_board_is_rejected_before_export(self):
        with TemporaryDirectory() as directory:
            root=Path(directory)
            path=root/'hardware/review/ch32-pico.kicad_pcb'
            path.parent.mkdir(parents=True)
            path.write_text('(kicad_pcb (gr_text "REV A"))')
            with patch('hardware.release.ROOT',root), patch('hardware.release.BOARD_REVISION','B'):
                with self.assertRaisesRegex(ValueError,'Saved layout is not Rev B'):
                    require_current_layout()

    def test_matching_silk_does_not_bypass_netlist_check(self):
        with TemporaryDirectory() as directory:
            root=Path(directory)
            path=root/'hardware/review/ch32-pico.kicad_pcb'
            path.parent.mkdir(parents=True)
            path.write_text('(kicad_pcb (gr_text "REV B"))')
            with patch('hardware.release.ROOT',root), patch('hardware.release.BOARD_REVISION','B'):
                with self.assertRaises(ValueError):
                    require_current_layout()
