# SPDX-License-Identifier: MIT
"""Manufacturing must reject a saved board from an older revision."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from hardware.release import require_current_layout


class ReleaseRevision(TestCase):
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
