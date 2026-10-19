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

    def test_gpio_probe_pad_cannot_be_miswired_to_vbus(self):
        with self.assertRaisesRegex(ValueError,'TP14.1'):
            verify_contract(self.altered('TP14',{'1':'VBUS'}))

    def test_voltage_probe_cannot_be_miswired_to_raw_vbus(self):
        with self.assertRaisesRegex(ValueError,'TP17.1'):
            verify_contract(self.altered('TP17',{'1':'VBUS'}))

    def test_current_design(self):
        verify_contract()

    def test_16v_parts_rejected_on_each_high_voltage_position(self):
        for ref in ('C1',):
            with self.subTest(ref=ref), self.assertRaisesRegex(ValueError,ref+': high-voltage'):
                verify_contract(tuple(replace(c,part='C1525') if c.ref==ref else c for c in COMPONENTS))

    def test_low_voltage_capacitor_cannot_masquerade_as_50v(self):
        with self.assertRaisesRegex(ValueError,'C6: capacitor value label'):
            verify_contract(tuple(replace(c,part='C1525') if c.ref=='C6' else c for c in COMPONENTS))

    def test_clamp_must_stay_on_vbus(self):
        with self.assertRaisesRegex(ValueError,'D5.4'):
            verify_contract(self.altered('D5',{'4':'VSYS','5':'VSYS','6':'VSYS'}))

    def test_header_40_must_be_direct_vbus(self):
        with self.assertRaisesRegex(ValueError,'J1.40'):
            verify_contract(self.altered('J1',{'40':'VSYS'}))

    def test_exported_part_substitution_rejected(self):
        path=Path('build/ch32-pico.net.xml')
        if not path.exists(): self.skipTest('Run just electrical-check to export the netlist')
        tree=ET.parse(path)
        cap=next(n for n in tree.findall('./components/comp') if n.attrib['ref']=='C1')
        next(f for f in cap.findall('./fields/field') if f.attrib['name']=='LCSC').text='C1525'
        with tempfile.TemporaryDirectory() as directory:
            broken=Path(directory)/'wrong-part.xml';tree.write(broken)
            with self.assertRaisesRegex(ValueError,'C1: netlist part/value'):
                verify_netlist(broken)

    def test_shutdown_cannot_be_left_unconnected(self):
        with self.assertRaisesRegex(ValueError, 'U4.4'):
            verify_contract(self.altered('U4', {'4': None}))

    def test_feedback_divider_cannot_be_retuned_silently(self):
        with self.assertRaisesRegex(ValueError, 'R14: the 3.3 V setpoint'):
            verify_contract(tuple(replace(c,part='C25744',value='10k') if c.ref=='R14' else c for c in COMPONENTS))

    def test_header_35_cannot_bypass_jumper(self):
        with self.assertRaisesRegex(ValueError, 'J1.35'):
            verify_contract(self.altered('J1', {'35': 'PC7'}))

    def test_jumper_must_be_open_between_distinct_nets(self):
        with self.assertRaisesRegex(ValueError, 'SJ1.1'):
            verify_contract(self.altered('SJ1', {'1': 'PC7'}))

    def test_shutdown_pull_up_must_use_the_diode_or_node(self):
        with self.assertRaisesRegex(ValueError, 'R15.1'):
            verify_contract(self.altered('R15', {'1': 'VBUS'}))

    def test_reversed_input_diode_rejected(self):
        with self.assertRaisesRegex(ValueError,'D1.1'):
            verify_contract(self.altered('D1',{'1':'VBUS','2':'VSYS'}))

    def test_supply_pin_cannot_be_forgotten(self):
        with self.assertRaisesRegex(ValueError,'supply pin left NC'):
            verify_contract(self.altered('U1',{'48':None}))

    def test_usb_pin_swap_rejected(self):
        with self.assertRaisesRegex(ValueError,'U1.32'):
            verify_contract(self.altered('U1',{'32':'USB_DP','33':'USB_DM'}))

    def test_pb4_pad_cannot_retain_old_pc7_connection(self):
        with self.assertRaisesRegex(ValueError,'TP7.1'):
            verify_contract(self.altered('TP7',{'1':'PC7'}))

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
