# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
import unittest
from hardware.sexp import parse,children
from hardware.usb_review import contains,path_length


class USBGeometryChecks(unittest.TestCase):
    def test_bridged_ground_cutout_is_not_copper(self):
        # Outer square with a bridge to an inner square, as in KiCad fills.
        polygon=[(0,0),(4,0),(4,4),(0,4),(0,0),
                 (1,1),(1,3),(3,3),(3,1),(1,1),(0,0)]
        self.assertTrue(contains((.5,2),polygon))
        self.assertFalse(contains((2,2),polygon))
        self.assertFalse(contains((5,2),polygon))

    def test_route_length_splits_t_junction(self):
        doc=parse('''(kicad_pcb
          (segment (start 0 0) (end 4 0))
          (segment (start 2 0) (end 2 3)))''')
        self.assertEqual(path_length(children(doc,'segment'),(0,0),(2,3)),5)

    def test_disconnected_centerline_fails(self):
        doc=parse('(kicad_pcb (segment (start 0 0) (end 1 0)))')
        with self.assertRaises(ValueError):path_length(children(doc,'segment'),(0,0),(2,0))
