# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Catch wiring regressions that can defeat power cycling or change the header."""
from dataclasses import replace
import unittest
from hardware.lowcost import COMPONENTS_LOWCOST, verify


class LowcostContractTests(unittest.TestCase):
    def changed(self,ref,pin,net):
        return tuple(replace(c,nets={**c.nets,str(pin):net}) if c.ref==ref else c
                     for c in COMPONENTS_LOWCOST)

    def test_candidate_is_complete(self):
        self.assertEqual(verify()['fitted_parts'],33)

    def test_unswitched_swio_pullup_is_rejected(self):
        with self.assertRaises(ValueError):
            verify(self.changed('R16',2,'3V3_OUT'))

    def test_gpio_cannot_supply_target_vdd(self):
        with self.assertRaises(ValueError):
            verify(self.changed('U1',9,'TARGET_EN'))

    def test_enable_cannot_default_on(self):
        with self.assertRaises(ValueError):
            verify(self.changed('R2',2,'3V3_OUT'))

    def test_header_power_position_is_preserved(self):
        with self.assertRaises(ValueError):
            verify(self.changed('J1',36,'TARGET_3V3'))

    def test_low_speed_pullup_cannot_go_on_dp(self):
        with self.assertRaises(ValueError):
            verify(self.changed('R9',2,'USB_DP'))
