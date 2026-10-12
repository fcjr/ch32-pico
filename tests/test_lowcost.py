# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Catch wiring regressions that can defeat PD power isolation or change the header."""
from dataclasses import replace
import unittest
from hardware.lowcost import COMPONENTS_LOWCOST, verify


class LowcostContractTests(unittest.TestCase):
    def changed(self,ref,pin,net):
        return tuple(replace(c,nets={**c.nets,str(pin):net}) if c.ref==ref else c
                     for c in COMPONENTS_LOWCOST)

    def test_candidate_is_complete(self):
        self.assertEqual(verify()['fitted_parts'],41)

    def test_vsys_backfeed_is_rejected(self):
        with self.assertRaises(ValueError):
            verify(self.changed('D4',1,'VBUS'))

    def test_gpio_cannot_supply_target_vdd(self):
        with self.assertRaises(ValueError):
            verify(self.changed('U1',48,'PD_ENABLE'))

    def test_enable_cannot_default_on(self):
        with self.assertRaises(ValueError):
            verify(self.changed('R7',2,'3V3_OUT'))

    def test_header_power_position_is_preserved(self):
        with self.assertRaises(ValueError):
            verify(self.changed('J1',36,'TARGET_3V3'))

    def test_esd_cannot_use_negotiated_vbus(self):
        with self.assertRaises(ValueError):
            verify(self.changed('D2',5,'VBUS'))
