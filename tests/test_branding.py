# SPDX-License-Identifier: MIT
from unittest import TestCase
from hardware.branding import apply,artwork
from hardware.sexp import children,dump,one


class Branding(TestCase):
    def test_repeated_review_does_not_duplicate_voltage_legend(self):
        doc=['kicad_pcb']
        apply(doc)
        first=dump(doc)
        apply(doc)
        self.assertEqual(dump(doc),first)
        self.assertEqual([n[1] for n in children(doc,'gr_text')].count('VBUS 5-20V'),1)
        ids=[one(n,'uuid')[1] for n in artwork()]
        self.assertEqual(len(ids),len(set(ids)))
