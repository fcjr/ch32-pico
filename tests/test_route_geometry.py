# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
import unittest
from hardware.sexp import parse,children,one
from hardware.route_geometry import trim_to_junctions


class DeadEscapeChecks(unittest.TestCase):
    def board(self,branch_net='S',branch_layer='F.Cu'):
        return parse(f'''(kicad_pcb
          (footprint "test" (at 0 0) (property "Reference" "U1")
            (pad "1" smd rect (at 0 0) (size 0.2 0.8) (layers "F.Cu") (net "S")))
          (segment (start 0 0) (end 2 0) (width 0.15) (layer "F.Cu") (net "S"))
          (segment (start 1 0) (end 1 1) (width 0.15) (layer "{branch_layer}") (net "{branch_net}")))''')

    def test_keep_pad_to_branch_connection(self):
        doc=self.board();track=children(doc,'segment')[0]
        self.assertTrue(trim_to_junctions(doc,track))
        self.assertEqual(tuple(map(float,one(track,'end')[1:3])),(1,0))

    def test_foreign_copper_is_not_a_connection(self):
        for net,layer in [('OTHER','F.Cu'),('S','B.Cu')]:
            doc=self.board(net,layer)
            self.assertFalse(trim_to_junctions(doc,children(doc,'segment')[0]))
