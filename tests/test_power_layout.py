# SPDX-License-Identifier: MIT
from pathlib import Path
from unittest import TestCase
from hardware.power_layout import audit
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
