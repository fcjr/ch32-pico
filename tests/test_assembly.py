# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
import unittest
from hardware.assembly_checks import via_in_paste
from hardware.sexp import parse


class AssemblyChecks(unittest.TestCase):
    def board(self,x,y):
        return parse(f'''(kicad_pcb
          (footprint "test" (at 10 10 90) (property "Reference" "R1")
            (pad "1" smd rect (at -1 0 90) (size 1 0.5) (layers "F.Cu" "F.Paste")))
          (via (at {x} {y}) (drill 0.2)))''')

    def test_rotated_pad_drill_overlap_rejected(self):
        self.assertEqual(via_in_paste(self.board(10,11))[0]['pad'],'R1.1')

    def test_drill_edge_overlap_rejected(self):
        self.assertTrue(via_in_paste(self.board(10.3,11)))

    def test_escape_via_outside_paste_allowed(self):
        self.assertEqual(via_in_paste(self.board(10.5,11)),[])
