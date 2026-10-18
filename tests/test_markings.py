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
        self.assertEqual(len(result['expansion_labels']),8)

    def test_expansion_pad_label_on_wrong_side_is_rejected(self):
        one(self.label('PB4'),'layer')[1]='F.SilkS'
        with self.assertRaisesRegex(ValueError,'Back must contain'):audit(self.doc)

    def test_stale_pc7_pad_label_is_rejected(self):
        self.label('PB4')[1]='PC7'
        with self.assertRaisesRegex(ValueError,'Incorrect back expansion label/pad: TP7'):
            audit(self.doc)

    def test_top_only_testpad_label_on_back_is_rejected(self):
        one(self.label('SDIO'),'layer')[1]='B.SilkS'
        with self.assertRaisesRegex(ValueError,'services belong on front'):audit(self.doc)

    def test_swapped_service_labels_are_rejected(self):
        io,rst=self.label('SDIO'),self.label('SDCK')
        io[1],rst[1]=rst[1],io[1]
        with self.assertRaisesRegex(ValueError,'too far|nearer'):audit(self.doc)

    def test_wrong_header_gpio_is_rejected(self):
        self.label('1 PB10')[1]='1 PB11'
        with self.assertRaisesRegex(ValueError,'header label at pin 1'):audit(self.doc)

    def test_correct_header_label_with_wrong_mcu_connection_is_rejected(self):
        fp=next(fp for fp in children(self.doc,'footprint')
                if any(p[1:3]==['Reference','U1'] for p in children(fp,'property')))
        pad=next(p for p in children(fp,'pad') if p[1]=='30')
        one(pad,'net')[-1]='PB11'
        with self.assertRaisesRegex(ValueError,'Header label/MCU mismatch at pin 1'):
            audit(self.doc)

    def test_unmirrored_back_label_is_rejected(self):
        effects=one(self.label('1 PB10'),'effects')
        effects.remove(one(effects,'justify'))
        with self.assertRaisesRegex(ValueError,'mirroring'):audit(self.doc)

    def test_miswired_service_pad_is_rejected(self):
        fp=next(fp for fp in children(self.doc,'footprint')
                if any(p[1:3]==['Reference','TP1'] for p in children(fp,'property')))
        one(one(fp,'pad'),'net')[-1]='SDCK'
        with self.assertRaisesRegex(ValueError,'TP1 label/net mismatch'):audit(self.doc)

    def test_missing_ground_legend_is_rejected(self):
        n=next(n for n in children(self.doc,'gr_text')
               if n[1]=='GND' and one(n,'layer')[1]=='F.SilkS')
        self.doc.remove(n)
        with self.assertRaisesRegex(ValueError,'front label for TP4'):audit(self.doc)

    def test_diagnostic_pads_cannot_receive_paste(self):
        fp=next(fp for fp in children(self.doc,'footprint')
                if any(p[1:3]==['Reference','TP15'] for p in children(fp,'property')))
        one(one(fp,'pad'),'layers').append('B.Paste')
        with self.assertRaisesRegex(ValueError,'Diagnostic pad must have no paste'):
            audit(self.doc)

    def test_diagnostic_label_cannot_swap_gpio_and_voltage(self):
        self.label('PA3')[1]='VSNS'
        with self.assertRaisesRegex(ValueError,'Incorrect diagnostic label'):
            audit(self.doc)

    def test_jumper_cannot_receive_factory_paste(self):
        fp=next(fp for fp in children(self.doc,'footprint')
                if any(p[1:3]==['Reference','SJ1'] for p in children(fp,'property')))
        one(children(fp,'pad')[0],'layers').append('B.Paste')
        with self.assertRaisesRegex(ValueError,'no paste'):audit(self.doc)

    def test_top_header_leader_cannot_be_lost(self):
        from hardware.schematic import uid
        line=next(n for n in children(self.doc,'gr_line')
                  if one(n,'uuid')[1]==uid('marking/header-leader/40/0'))
        self.doc.remove(line)
        with self.assertRaisesRegex(ValueError,'Header leader missing'):audit(self.doc)

    def test_diagnostic_label_nearer_an_expansion_pad_is_rejected(self):
        from dataclasses import replace
        from unittest.mock import patch
        from hardware.diagnostics import DIAGNOSTICS
        old=tuple(replace(d,text_position=(14.7,33.05)) if d.ref=='TP22' else d
                  for d in DIAGNOSTICS)
        with patch('hardware.markings.DIAGNOSTICS',old):
            apply(self.doc)
            with self.assertRaisesRegex(ValueError,'TP22 is nearer TP6'):audit(self.doc)
