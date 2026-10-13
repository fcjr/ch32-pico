# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Check the interface contract against independently recorded Pico dimensions."""

import unittest

from hardware.design import HEADER, MECHANICAL, TARGET_PINS, validate
from hardware.generate import board, footprint


class DesignContract(unittest.TestCase):
    def test_pico_header_orientation(self):
        # Datasheet figure 3 and KiCad's Module:RaspberryPi_Pico_Common_THT.
        self.assertEqual(MECHANICAL.position(1), (1.61, 1.37))
        self.assertEqual(MECHANICAL.position(20), (1.61, 49.63))
        self.assertEqual(MECHANICAL.position(21), (19.39, 49.63))
        self.assertEqual(MECHANICAL.position(40), (19.39, 1.37))
        for n in range(1, 20):
            self.assertAlmostEqual(MECHANICAL.position(n + 1)[1] - MECHANICAL.position(n)[1], 2.54)

    def test_ground_and_supply_positions(self):
        pins = {p.number: p.proposed for p in HEADER}
        self.assertEqual({n for n, net in pins.items() if net == "GND"}, {3, 8, 13, 18, 23, 28, 33, 38})
        self.assertEqual({n: pins[n] for n in (35, 36, 37, 39, 40)},
                         {35: "NC", 36: "3V3_OUT", 37: "3V3_EN", 39: "VSYS", 40: "PD_OUT"})

    def test_gpio_budget_and_debug_reservation(self):
        validate()
        gpio = [p for p in HEADER if p.proposed in TARGET_PINS and p.number != 30]
        self.assertEqual(len(gpio), 26)
        self.assertNotIn("PC18", {p.proposed for p in HEADER})
        self.assertEqual(HEADER[29].proposed, "PA21")

    def test_peripheral_placement(self):
        pins = {p.number: p.proposed for p in HEADER}
        # CH32 default peripheral pins from WCH PeripheralPins.c. No remap
        # conflicts between these UART, I2C, SPI, and ADC assignments.
        self.assertEqual([pins[n] for n in (1, 2)], ["PB10", "PB11"])
        self.assertEqual([pins[n] for n in (6, 7)], ["PA11", "PA10"])
        self.assertEqual([pins[n] for n in (21, 24, 25)], ["PA6", "PA5", "PA7"])
        self.assertEqual([pins[n] for n in (31, 32, 34)], ["PA0", "PA1", "PA2"])

    def test_holes_fit_and_clear_header_copper(self):
        self.assertEqual(MECHANICAL.mounting_holes,())
        self.assertNotIn('np_thru_hole',footprint())

    def test_generation_is_stable(self):
        self.assertEqual(board(footprint()), board(footprint()))


if __name__ == "__main__":
    unittest.main()
