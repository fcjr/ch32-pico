# SPDX-License-Identifier: MIT
"""The saved routing delta must preserve the reviewed placement and copper."""
import json
import subprocess
from pathlib import Path
from unittest import TestCase
from hardware.power_routing import BASE,BASE_PATH,PATCH,apply_delta,normalized,entries


class PowerRouting(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=subprocess.check_output(['git','show',f'{BASE}:{BASE_PATH}'],text=True)
        cls.patch=json.loads(PATCH.read_text())

    def test_replay_matches_reviewed_unfilled_board(self):
        reviewed=normalized(Path('hardware/review/ch32-pico.kicad_pcb').read_text())
        self.assertEqual(entries(apply_delta(self.base,self.patch)),entries(reviewed))

    def test_changed_base_rejected(self):
        with self.assertRaisesRegex(ValueError,'pinned checkpoint'):
            apply_delta(self.base+'\n',self.patch)
