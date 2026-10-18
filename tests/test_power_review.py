# SPDX-License-Identifier: MIT
"""Screening checks must not turn a nominal limit into a rating."""
from dataclasses import replace
from unittest import TestCase
from hardware.circuit import COMPONENTS
from hardware.power_review import qualification_screen


class PowerScreen(TestCase):
    def test_no_output_rating_or_switch_is_claimed(self):
        report=qualification_screen()
        self.assertTrue(all(row['continuous_rating_a'] is None for row in report['mode_checks']))
        self.assertFalse(report['physical_measurements_available'])
        self.assertFalse(report['pin40']['switched'])
        self.assertEqual(report['pin40']['default_v'],5)

    def test_voltage_sweep_follows_vbus(self):
        report=qualification_screen()
        self.assertEqual([row['nominal_v'] for row in report['mode_checks']],[5,9,12,15,20])
        self.assertEqual([row['pin40_v'] for row in report['mode_checks']],[5,9,12,15,20])
        self.assertEqual([row['default_on_attach'] for row in report['mode_checks']],[True,False,False,False,False])

    def test_clamp_stays_below_buck_limit(self):
        screen=qualification_screen()['transient_screen']
        self.assertLess(screen['specified_hot_clamp_v'],screen['buck_operating_max_v'])
        self.assertGreater(screen['tvs_standoff_v'],20*1.05)

    def test_sense_divider_reads_circuit_values(self):
        original=qualification_screen()
        changed=qualification_screen(tuple(replace(c,value='20k') if c.ref=='R2' else c for c in COMPONENTS))
        self.assertAlmostEqual(original['vbus_sense']['at_20v'],20/11,places=4)
        self.assertGreater(changed['vbus_sense']['at_20v'],original['vbus_sense']['at_20v'])
