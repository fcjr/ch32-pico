# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
import unittest
from pathlib import Path
from hardware.mechanical_checks import usb_fit
from hardware.generate import board, footprint
from hardware.sexp import parse, children, one


class CableClearance(unittest.TestCase):
    def fixture(self):
        doc=parse(board(footprint()))
        usb=parse(Path('hardware/lib/ch32-pico.pretty/USB_C_Receptacle_G-Switch_GT-USB-7010AW.kicad_mod').read_text())
        for prop in children(usb,'property'):
            if prop[1]=='Reference':prop[2]='J2'
            if prop[1]=='Value':prop[2]='GT-USB-7010AW'
        usb.append(parse('(at 10.5 3.375 180)'))
        doc.append(usb)
        return doc,usb

    def test_reference_dimension_is_not_a_guaranteed_minimum(self):
        doc,_=self.fixture()
        result=usb_fit(doc)
        self.assertIsNone(result['minimum_mated_gap_mm'])
        self.assertIsNone(result['remaining_cable_margin_mm'])
        self.assertFalse(result['physical_fit_tested'])
        self.assertEqual(len(result['mounting_holes']),0)
        self.assertEqual(result['mouth_recess_mm'],-.3)

    def test_unreviewed_recess_fails(self):
        doc,usb=self.fixture()
        one(usb,'at')[2]='5.5'
        with self.assertRaisesRegex(ValueError,'Unreviewed USB recess'):
            usb_fit(doc)

    def test_wrong_part_is_rejected(self):
        doc,usb=self.fixture()
        next(p for p in children(usb,'property') if p[1]=='Value')[2]='OTHER_CONNECTOR'
        with self.assertRaisesRegex(ValueError,'reviewed G-Switch part'):
            usb_fit(doc)

    def test_reversed_connector_is_rejected(self):
        doc,usb=self.fixture()
        one(usb,'at')[3]='0'
        with self.assertRaisesRegex(ValueError,'front-facing connector'):
            usb_fit(doc)

    def test_shell_over_mounting_hole_is_rejected(self):
        doc,usb=self.fixture()
        header=next(f for f in children(doc,'footprint') if f is not usb)
        header.append(parse('(pad "" np_thru_hole circle (at 5.2 2) (size 2.1 2.1) (drill 2.1) (layers "*.Cu" "*.Mask"))'))
        one(usb,'at')[1]='10.0'
        with self.assertRaisesRegex(ValueError,'overlaps a Pico mounting hole'):
            usb_fit(doc)
