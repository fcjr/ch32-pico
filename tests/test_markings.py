# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Fault injection for label errors that electrical DRC cannot identify."""
import unittest
from pathlib import Path
from hardware.markings import audit, apply
from hardware.sexp import parse, children, one


class MarkingAudit(unittest.TestCase):
    def setUp(self):
        self.doc=parse(Path('build/ch32-pico-placed.kicad_pcb').read_text())
        apply(self.doc)

    def label(self, value):
        return next(n for n in children(self.doc,'gr_text') if n[1]==value)

    def test_checked_design_has_every_header_and_service_label(self):
        result=audit(self.doc)
        self.assertEqual(result['header_count'],40)
        self.assertEqual(result['front_service_count'],8)

    def test_top_only_testpad_label_on_back_is_rejected(self):
        one(self.label('SDIO'),'layer')[1]='B.SilkS'
        with self.assertRaisesRegex(ValueError,'services belong on front'):audit(self.doc)

    def test_swapped_programmer_labels_are_rejected(self):
        io,rst=self.label('SDIO'),self.label('SDCK')
        io[1],rst[1]=rst[1],io[1]
        with self.assertRaisesRegex(ValueError,'too far|nearer'):audit(self.doc)

    def test_wrong_header_gpio_is_rejected(self):
        self.label('1\nPB10')[1]='1\nPB11'
        with self.assertRaisesRegex(ValueError,'header label at pin 1'):audit(self.doc)

    def test_correct_header_label_with_wrong_mcu_connection_is_rejected(self):
        fp=next(fp for fp in children(self.doc,'footprint')
                if any(p[1:3]==['Reference','U1'] for p in children(fp,'property')))
        pad=next(p for p in children(fp,'pad') if p[1]=='30')
        one(pad,'net')[-1]='PB11'
        with self.assertRaisesRegex(ValueError,'Header label/MCU mismatch at pin 1'):
            audit(self.doc)

    def test_unmirrored_back_label_is_rejected(self):
        effects=one(self.label('1\nPB10'),'effects')
        effects.remove(one(effects,'justify'))
        with self.assertRaisesRegex(ValueError,'mirroring'):audit(self.doc)

    def test_miswired_programmer_pad_is_rejected(self):
        fp=next(fp for fp in children(self.doc,'footprint')
                if any(p[1:3]==['Reference','TP1'] for p in children(fp,'property')))
        one(one(fp,'pad'),'net')[-1]='SDCK'
        with self.assertRaisesRegex(ValueError,'TP1 label/net mismatch'):audit(self.doc)

    def test_missing_ground_legend_is_rejected(self):
        n=next(n for n in children(self.doc,'gr_text')
               if n[1]=='GND' and one(n,'layer')[1]=='F.SilkS')
        self.doc.remove(n)
        with self.assertRaisesRegex(ValueError,'front label for TP4'):audit(self.doc)
