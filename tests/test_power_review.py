# SPDX-License-Identifier: MIT
"""Tolerance and startup checks must not turn a nominal limit into a rating."""
from dataclasses import replace
from unittest import TestCase
from hardware.circuit import COMPONENTS
from hardware.power_review import qualification_screen


class PowerScreen(TestCase):
    def test_limit_headroom_does_not_assign_output_rating(self):
        report=qualification_screen()
        self.assertGreater(report['ilm']['screen_min_a'],3)
        self.assertLess(report['ilm']['screen_max_a'],4.32)
        self.assertAlmostEqual(report['ilm']['nominal_a'],3.6364,places=4)
        self.assertTrue(all(row['continuous_rating_a'] is None for row in report['mode_checks']))
        self.assertFalse(report['physical_measurements_available'])

    def test_review_reads_timing_capacitor_from_circuit(self):
        original=qualification_screen()
        changed=qualification_screen(tuple(replace(c,value='44nF / 50V') if c.ref=='C8' else c for c in COMPONENTS))
        self.assertAlmostEqual(original['mode_checks'][-1]['nominal_rise_time_ms'],8.73)
        self.assertAlmostEqual(changed['mode_checks'][-1]['nominal_rise_time_ms'],17.46)

    def test_voltage_sweep_and_hardware_interlock(self):
        report=qualification_screen()
        low,high=report['mode_checks'][0],report['mode_checks'][-1]
        self.assertEqual([row['nominal_v'] for row in report['mode_checks']],[5,9,12,15,20])
        self.assertAlmostEqual(high['r8_power_at_upper_check_mw']/low['r8_power_at_upper_check_mw'],16,delta=.01)
        self.assertGreater(report['ovlo_static_screen_v']['minimum'],21)
        # Consolidated 82.5k gives 23.751 V at the screened upper corner.
        # Keep a 24 V static ceiling, below the 28.35 V surge clamp and
        # 32 V regulator operating maximum; this does not qualify transients.
        self.assertLess(report['ovlo_static_screen_v']['maximum'],24)
        self.assertGreater(report['uvlo_static_screen_v']['falling_minimum'],4.5)
        self.assertLess(report['uvlo_static_screen_v']['rising_maximum'],4.90)
        self.assertGreater(report['uvlo_static_screen_v']['input_at_trip_minimum_at_fault_screen_a'],4.5)
        self.assertTrue(low['low_input_shutdown_possible'])
        self.assertAlmostEqual(report['imon']['nominal_v_per_a'],.260)
