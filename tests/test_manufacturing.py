# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Reject missing assembly parts and coordinate conversion regressions."""
import csv
import tempfile
import unittest
from pathlib import Path
from hardware.circuit import COMPONENTS
from hardware.manufacturing import assembly_files
from hardware.placement import PLACEMENT


class ManufacturingTests(unittest.TestCase):
    def positions(self,directory,mutate):
        rows=[]
        for c in COMPONENTS:
            if c.fitted:
                x,y,angle=PLACEMENT[c.ref]
                rows.append({'Ref':c.ref,'PosX':x,'PosY':-y,'Rot':angle,'Side':'top'})
        mutate(rows)
        p=directory/'positions.csv'
        with p.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['Ref','PosX','PosY','Rot','Side']);w.writeheader();w.writerows(rows)
        return p

    def test_hybrid_usb_connector_cannot_be_omitted(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            p=self.positions(directory,lambda rows:rows.remove(next(r for r in rows if r['Ref']=='J2')))
            with self.assertRaisesRegex(ValueError,'coverage mismatch'):
                assembly_files(p,directory)

    def test_positive_y_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            p=self.positions(directory,lambda rows:next(r for r in rows if r['Ref']=='J2').update(PosY=4.925))
            with self.assertRaisesRegex(ValueError,'position/orientation/side'):
                assembly_files(p,directory)
