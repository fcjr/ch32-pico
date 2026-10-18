# SPDX-License-Identifier: MIT
from pathlib import Path
from unittest import TestCase
from hardware.power_layout import audit,ground_returns,vbus_connections
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

    def test_narrow_clamp_ground_return_rejected(self):
        from hardware.usb_review import pad_centers
        center=pad_centers(self.doc)['D5','7']
        for s in children(self.doc,'segment'):
            if one(s,'net')[-1]=='GND' and any(tuple(map(float,one(s,k)[1:3]))==center for k in ('start','end')):
                one(s,'width')[1]='0.15'
        with self.assertRaisesRegex(ValueError,'D5'):ground_returns(self.doc)

    def test_clamp_and_header_trunk_are_direct(self):
        result=vbus_connections(self.doc)
        self.assertLess(result['input_clamp_mm'],6)
        self.assertLess(result['header_pin40_trunk_mm'],16)
        self.assertLess(result['header_pin40_front_feed_mm'],16)

    def test_missing_front_feed_rejected(self):
        self.doc[:]=[n for n in self.doc if not (isinstance(n,list) and n[0]=='segment'
                    and one(n,'net')[-1]=='VBUS' and one(n,'layer')[1]=='F.Cu' and float(one(n,'width')[1])==.8)]
        with self.assertRaisesRegex(ValueError,'front-layer VBUS feed'):vbus_connections(self.doc)

    def test_missing_clamp_connection_rejected(self):
        self.doc[:]=[n for n in self.doc if not (isinstance(n,list) and n[0]=='segment'
                    and one(n,'net')[-1]=='VBUS' and one(n,'layer')[1]=='F.Cu')]
        with self.assertRaisesRegex(ValueError,'input_clamp'):vbus_connections(self.doc)

    def test_narrowed_header_trunk_rejected(self):
        trunk=next(n for n in children(self.doc,'segment') if one(n,'net')[-1]=='VBUS'
                   and one(n,'layer')[1]=='B.Cu' and float(one(n,'width')[1])==1.2)
        one(trunk,'width')[1]='0.8'
        with self.assertRaisesRegex(ValueError,'pin 40'):vbus_connections(self.doc)

    def test_local_returns_outside_ground_fill_rejected(self):
        self.doc.append(parse('''(zone (net "GND") (filled_polygon (layer "In1.Cu")
            (pts (xy 0 0) (xy 1 0) (xy 1 1) (xy 0 1))))'''))
        with self.assertRaisesRegex(ValueError,'outside the filled ground plane'):audit(self.doc)
