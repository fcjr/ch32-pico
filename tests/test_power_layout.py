# SPDX-License-Identifier: MIT
from pathlib import Path
from unittest import TestCase
from hardware.power_layout import audit,ground_returns
from hardware.sexp import parse,children,one


class PowerLayout(TestCase):
    def setUp(self):
        self.doc=parse(Path('build/ch32-pico-seed.kicad_pcb').read_text())

    def test_short_local_input_loop(self):
        self.assertLess(audit(self.doc)['input_capacitor_connections_mm']['VIN_SYS'],2)

    def test_missing_input_connection_rejected(self):
        s=next(s for s in children(self.doc,'segment')
               if one(s,'net')[-1]=='VIN_SYS' and one(s,'layer')[1]=='F.Cu')
        self.doc.remove(s)
        with self.assertRaises(ValueError):audit(self.doc)

    def test_switch_node_via_rejected(self):
        self.doc.append(parse('(via (at 8.2 14.7) (net "BUCK_SW"))'))
        with self.assertRaisesRegex(ValueError,'must not acquire vias'):audit(self.doc)

    def test_feedback_plane_shortcut_rejected(self):
        self.doc.append(parse('''(zone (net "3V3_OUT") (filled_polygon (layer "In2.Cu")
            (pts (xy 5 23) (xy 6.2 23) (xy 6.2 24.1) (xy 5 24.1))))'''))
        with self.assertRaisesRegex(ValueError,'bypasses'):audit(self.doc)

    def test_capacitor_and_clamps_have_two_short_wide_ground_returns(self):
        for paths in ground_returns(self.doc).values():
            self.assertGreaterEqual(len(paths),2)
            self.assertTrue(all(p['path_mm']<=2.5 for p in paths))

    def test_missing_local_ground_via_rejected(self):
        for ref,paths in ground_returns(self.doc).items():
            with self.subTest(ref=ref):
                via=next(v for v in children(self.doc,'via')
                         if list(map(float,one(v,'at')[1:3]))==paths[0]['via_mm'])
                self.doc.remove(via)
                with self.assertRaisesRegex(ValueError,ref):ground_returns(self.doc)
                self.doc.append(via)

    def test_narrow_capacitor_ground_return_rejected(self):
        from hardware.usb_review import pad_centers
        center=pad_centers(self.doc)['C12','2']
        for s in children(self.doc,'segment'):
            if one(s,'net')[-1]=='GND' and any(tuple(map(float,one(s,k)[1:3]))==center for k in ('start','end')):
                one(s,'width')[1]='0.15'
        with self.assertRaisesRegex(ValueError,'C12'):ground_returns(self.doc)
