# SPDX-License-Identifier: MIT
"""Tolerance and startup checks must not turn a nominal limit into a rating."""
from dataclasses import replace
from unittest import TestCase
from hardware.circuit import COMPONENTS
from hardware.power_review import qualification_screen


class PowerScreen(TestCase):
    def test_three_amp_load_exceeds_low_current_limit_corner(self):
        report=qualification_screen()
        self.assertAlmostEqual(report['ilm']['screen_min_a'],2.6127,places=4)
        self.assertAlmostEqual(report['ilm']['screen_max_a'],3.2578,places=4)
        self.assertLess(report['ilm']['screen_min_a'],3)
        self.assertGreater(report['ilm']['screen_max_a'],3)
        self.assertTrue(all(row['continuous_rating_a'] is None for row in report['mode_checks']))

    def test_review_reads_timing_capacitor_from_circuit(self):
        original=qualification_screen()
        changed=qualification_screen(tuple(replace(c,value='10nF / 50V') if c.ref=='C8' else c for c in COMPONENTS))
        self.assertAlmostEqual(original['mode_checks'][-1]['nominal_rise_time_ms'],1000)
        self.assertAlmostEqual(changed['mode_checks'][-1]['nominal_rise_time_ms'],100)
        self.assertFalse(any('C8 exceeds' in note for note in changed['required_before_power_qualification']))

    def test_voltage_sweep_catches_high_voltage_stress(self):
        report=qualification_screen()
        low,high=report['mode_checks'][0],report['mode_checks'][-1]
        self.assertEqual([row['nominal_v'] for row in report['mode_checks']],[5,9,12,15,20])
        self.assertAlmostEqual(high['r8_power_at_upper_check_mw']/low['r8_power_at_upper_check_mw'],16,places=2)
        self.assertEqual(high['resistive_startup_example']['peak_switch_w'],10)
        self.assertGreater(high['resistive_startup_example']['switch_energy_j'],6)
        self.assertLess(report['ovlo_headroom_below_23v_operating_limit_v'],.001)
