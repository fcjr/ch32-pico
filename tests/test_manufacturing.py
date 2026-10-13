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
    def test_bom_has_50v_caps_and_reduced_current_limit(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            assembly_files(self.positions(directory,lambda rows:None),directory)
            with (directory/'bom.csv').open() as f:
                by_ref={ref:row for row in csv.DictReader(f) for ref in row['Designator'].split(',')}
            for ref in ('C4','C5','C6','C8','C9','C10','C11','C12','C13'):
                self.assertEqual(by_ref[ref]['LCSC Part #'],'C307331')
                self.assertEqual(by_ref[ref]['MPN'],'CL05B104KB54PNC')
                self.assertEqual(by_ref[ref]['Comment'],'100nF / 50V')
            self.assertEqual(by_ref['R17']['LCSC Part #'],'C25900')
            self.assertEqual(by_ref['R17']['Comment'],'4.7k')
            self.assertEqual(by_ref['R18']['Comment'],'1.5k')

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
