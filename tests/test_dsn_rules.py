# SPDX-License-Identifier: MIT
"""Keep router interchange consistent with the actual stack and lock intent."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from hardware.dsn_rules import configure
from hardware.sexp import parse,children,one

class DsnRules(TestCase):
    def test_stack_via_and_unlocked_copper_translation(self):
        with TemporaryDirectory() as directory:
            p=Path(directory)/'test.dsn'
            p.write_text('''(pcb test
              (structure (boundary (path pcb 0 0 0 21000 0 21000 -51000 0 -51000 0 0))
                         (rule (width 150)))
              (library (padstack "Via[0-3]_450:200_um"))
              (network (class default GND SIGNAL (rule (width 150))))
              (wiring (wire (net SIGNAL) (type route))
                      (wire (net USB_DP) (type fix))
                      (via "Via[0-3]_450:200_um" 1000 -1000 (net SIGNAL) (type route))))''')
            configure(p);d=parse(p.read_text());w=one(d,'wiring')
            self.assertEqual([one(x,'type')[1] for x in children(w,'wire')],['normal','fix'])
            self.assertEqual(one(children(w,'via')[0],'type')[1],'normal')
            power=children(one(d,'network'),'class')[1:]
            self.assertTrue(power)
            self.assertTrue(all(one(one(c,'circuit'),'use_via')[1]=='Via[0-3]_450:200_um' for c in power))
