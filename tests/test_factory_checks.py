# SPDX-License-Identifier: MIT
import unittest
from hardware.factory_checks import panel_tooling
from hardware.sexp import parse


class FactoryTooling(unittest.TestCase):
    def panel(self, opening=2, offset=4.5, drill=2):
        features = ['(gr_line (start 0 0) (end 93 71) (layer "Edge.Cuts"))']
        for i, (x,y) in enumerate(((7,offset),(86,offset),(7,71-offset))):
            features.append(f'''(footprint "fid" (at {x} {y})
              (property "Reference" "KiKit_FID_T_{i}")
              (pad "" smd circle (size 1 1) (layers "F.Cu" "F.Mask")
                (solder_mask_margin {(opening-1)/2})))''')
        for i, (x,y) in enumerate(((2.5,3.5),(90.5,3.5),(2.5,67.5))):
            features.append(f'''(footprint "hole" (at {x} {y})
              (property "Reference" "KiKit_TO_{i}")
              (pad "" np_thru_hole circle (size {drill} {drill})
                (drill {drill}) (layers "*.Cu" "*.Mask")))''')
        return parse('(kicad_pcb '+' '.join(features)+')')

    def test_standard_panel(self):
        self.assertTrue(panel_tooling(self.panel())['passes'])

    def test_old_mask_opening_rejected(self):
        with self.assertRaisesRegex(ValueError, 'mask opening'):
            panel_tooling(self.panel(opening=1))

    def test_old_edge_offset_rejected(self):
        with self.assertRaisesRegex(ValueError, 'conveyor edge'):
            panel_tooling(self.panel(offset=3.5))

    def test_economic_tooling_rejected(self):
        with self.assertRaisesRegex(ValueError, '2 mm NPTH'):
            panel_tooling(self.panel(drill=1.152))
