# SPDX-License-Identifier: MIT
from unittest import TestCase
from hardware.ground_review import crossovers, audit
from hardware.sexp import parse, children, one


class GroundReview(TestCase):
    def board(self):
        return parse('''(kicad_pcb
            (segment (start 8.7329 37.0378) (end 1.61 36.93)
                (width .15) (layer "In1.Cu") (net "PA17"))
            (via (at 5 35) (net "GND"))
            (via (at 5 39) (net "GND"))
            (zone (net "GND") (filled_polygon (layer "In1.Cu")
                (pts (xy 0 0) (xy 21 0) (xy 21 51) (xy 0 51)))))''')

    def test_bounded_gpio_crossover_and_connected_ground(self):
        self.assertEqual(audit(self.board())['ground_via_count'],2)

    def test_other_signal_rejected(self):
        doc=self.board();one(children(doc,'segment')[0],'net')[1]='USB_DP'
        with self.assertRaisesRegex(ValueError,'Unreviewed'):crossovers(doc)

    def test_crossover_cannot_extend_toward_usb(self):
        doc=self.board();one(children(doc,'segment')[0],'start')[2]='28.3'
        with self.assertRaisesRegex(ValueError,'corridor'):crossovers(doc)

    def test_separate_ground_islands_rejected(self):
        doc=self.board();doc.remove(children(doc,'zone')[0])
        for y0,y1 in ((34,36),(38,40)):
            doc.append(parse(f'''(zone (net "GND") (filled_polygon (layer "In1.Cu")
                (pts (xy 4 {y0}) (xy 6 {y0}) (xy 6 {y1}) (xy 4 {y1}))))'''))
        with self.assertRaisesRegex(ValueError,'one connected'):audit(doc)
