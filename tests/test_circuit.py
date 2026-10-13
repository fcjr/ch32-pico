# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Regression checks for faults that a clean ERC alone does not rule out."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from hardware.circuit import COMPONENTS
from hardware.verify import verify_contract, verify_netlist


class CircuitContract(unittest.TestCase):
    def altered(self,ref,changes):
        return tuple(replace(c,nets={**c.nets,**changes}) if c.ref==ref else c for c in COMPONENTS)

    def test_current_design(self):
        verify_contract()

    def test_reversed_input_diode_rejected(self):
        with self.assertRaisesRegex(ValueError,'D1.1'):
            verify_contract(self.altered('D1',{'1':'VBUS','2':'VSYS'}))

    def test_supply_pin_cannot_be_forgotten(self):
        with self.assertRaisesRegex(ValueError,'supply pin left NC'):
            verify_contract(self.altered('U1',{'48':None}))

    def test_usb_pin_swap_rejected(self):
        with self.assertRaisesRegex(ValueError,'U1.32'):
            verify_contract(self.altered('U1',{'32':'USB_DP','33':'USB_DM'}))

    def test_expansion_pad_wrong_gpio_rejected(self):
        with self.assertRaisesRegex(ValueError,'TP7.1'):
            verify_contract(self.altered('TP7',{'1':'PC6'}))

    def test_exported_netlist_corruption_rejected(self):
        path=Path('build/ch32-pico.net.xml')
        if not path.exists(): self.skipTest('Run make electrical-check to export the netlist')
        verify_netlist(path)
        tree=ET.parse(path)
        net=next(n for n in tree.findall('./nets/net') if n.attrib['name']=='CC1')
        net.attrib['name']='CC2'
        with tempfile.TemporaryDirectory() as directory:
            broken=Path(directory)/'broken.xml';tree.write(broken)
            with self.assertRaisesRegex(ValueError,'Netlist differs'):
                verify_netlist(broken)


if __name__=='__main__': unittest.main()
