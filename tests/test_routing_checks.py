# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
import unittest
from hardware.routing_checks import unpreserved_segments
from hardware.sexp import parse


class CriticalCopper(unittest.TestCase):
    def seed(self):
        return parse('''(kicad_pcb (segment (start 0 0) (end 2 0)
                     (width .6) (layer "B.Cu") (net "VSYS") (locked yes)))''')

    def test_layer_swap_is_rejected(self):
        changed=parse('''(kicad_pcb (segment (start 0 0) (end 2 0)
                      (width .6) (layer "In1.Cu") (net "VSYS")))''')
        self.assertEqual(len(unpreserved_segments(self.seed(),changed)),1)

    def test_collinear_splitting_is_allowed(self):
        split=parse('''(kicad_pcb
           (segment (start 0 0) (end 1 0) (width .6) (layer "B.Cu") (net "VSYS"))
           (segment (start 1 0) (end 2 0) (width .6) (layer "B.Cu") (net "VSYS")))''')
        self.assertEqual(unpreserved_segments(self.seed(),split),[])

    def test_narrowed_path_is_rejected(self):
        changed=parse('''(kicad_pcb (segment (start 0 0) (end 2 0)
                      (width .25) (layer "B.Cu") (net "VSYS")))''')
        self.assertEqual(len(unpreserved_segments(self.seed(),changed)),1)


class CriticalVias(unittest.TestCase):
    def test_power_via_changes_are_rejected(self):
        from hardware.routing_checks import unpreserved_vias
        original='(kicad_pcb (via (at 5 10.7) (size .6) (drill .3) (layers "F.Cu" "B.Cu") (net "VSYS") (locked yes)))'
        seed=parse(original)
        for changed in (original.replace('(size .6)','(size .45)'),
                        original.replace('(drill .3)','(drill .2)'),
                        original.replace('(at 5 10.7)','(at 5.1 10.7)')):
            with self.subTest(changed=changed):
                self.assertEqual(len(unpreserved_vias(seed,parse(changed))),1)
        self.assertEqual(unpreserved_vias(seed,parse(original)),[])

class OutlineCopper(unittest.TestCase):
    def test_wholly_outside_copper_rejected(self):
        from hardware.routing_checks import outside_outline_copper
        doc=parse('(kicad_pcb (segment (start -1 4) (end -1 8) (width .15) (layer "F.Cu") (net "GND")))')
        self.assertEqual(len(outside_outline_copper(doc)),1)

    def test_track_width_and_via_annulus_must_fit(self):
        from hardware.routing_checks import outside_outline_copper
        doc=parse('(kicad_pcb (segment (start .05 4) (end .05 8) (width .15) (net "GND")) (via (at 20.9 4) (size .45) (net "GND")))')
        self.assertEqual(len(outside_outline_copper(doc)),2)

    def test_inside_copper_accepted(self):
        from hardware.routing_checks import outside_outline_copper
        doc=parse('(kicad_pcb (segment (start .5 4) (end .5 8) (width .15) (net "GND")))')
        self.assertEqual(outside_outline_copper(doc),[])


class StackupContract(unittest.TestCase):
    def test_missing_or_changed_stack_is_rejected(self):
        from hardware.routing_checks import stackup_matches
        board='(kicad_pcb (layers (0 "F.Cu" signal) (2 "B.Cu" signal)) (setup (stackup (layer "F.Cu" (thickness 0.035)))))'
        source=parse(board)
        self.assertTrue(stackup_matches(source,source))
        self.assertFalse(stackup_matches(source,parse(board.replace('0.035','0.018'))))
        self.assertFalse(stackup_matches(source,parse(board.replace('(stackup (layer "F.Cu" (thickness 0.035)))',''))))
        self.assertFalse(stackup_matches(source,parse(board.replace('(2 "B.Cu" signal)','(4 "In1.Cu" signal) (2 "B.Cu" signal)'))))
