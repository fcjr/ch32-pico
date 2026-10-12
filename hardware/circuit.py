# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Low-cost electrical source; every terminal has an explicit net or NC.

Both MCUs are CH32V003F4P6. The programmer is factory-flashed externally;
normal target programming and debug printf use the USB-C HID connection.
Manufacturing release requires the documented prototype qualification.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Component:
    ref: str
    part: str
    nets: dict[str, str | None]
    section: str
    value: str = ''
    note: str = ''
    fitted: bool = True


COMPONENTS = (
    # USB/5 V input and two 3.3 V LDOs
    Component('#FLG01', 'POWER_FLAG', {'1': 'GND'}, 'power', value='GND', note='External/passive power source', fitted=False),
    Component('#FLG02', 'POWER_FLAG', {'1': 'VBUS'}, 'power', value='VBUS', note='External/passive power source', fitted=False),
    Component('#FLG03', 'POWER_FLAG', {'1': 'VSYS'}, 'power', value='VSYS', note='External/passive power source', fitted=False),
    Component('C1', 'C52923', {'1': 'VSYS', '2': 'GND'}, 'power', value='1uF', note='At corresponding LDO input/output'),
    Component('C2', 'C52923', {'1': '3V3_OUT', '2': 'GND'}, 'power', value='1uF', note='At corresponding LDO input/output'),
    Component('C3', 'C52923', {'1': 'VSYS', '2': 'GND'}, 'power', value='1uF', note='At corresponding LDO input/output'),
    Component('C4', 'C52923', {'1': 'TARGET_3V3', '2': 'GND'}, 'power', value='1uF', note='At corresponding LDO input/output'),
    Component('D1', 'C8598', {'1': 'VSYS', '2': 'VBUS'}, 'power', value='B5819W', note='USB-to-VSYS only; cathode at VSYS'),
    Component('R1', 'C25741', {'1': 'VSYS', '2': '3V3_EN'}, 'power', value='100k', note='Pico-compatible enable pull-up to VSYS'),
    Component('R12', 'C11702', {'1': 'TARGET_3V3', '2': 'GND'}, 'power', value='1k', note='Target discharge; 3.3 mA when powered'),
    Component('R2', 'C25741', {'1': 'TARGET_EN', '2': 'GND'}, 'power', value='100k', note='Target off while programmer is blank/reset'),
    Component('U4', 'C82942', {'1': 'VSYS', '2': 'GND', '3': '3V3_EN', '4': None, '5': '3V3_OUT'}, 'power'),
    Component('U5', 'C82942', {'1': 'VSYS', '2': 'GND', '3': 'TARGET_EN', '4': None, '5': 'TARGET_3V3'}, 'power'),
    # USB-C low-speed HID, ESD and VBUS detection
    Component('C5', 'C1525', {'1': 'VBUS', '2': 'GND'}, 'usb', value='100nF', note='Direct VBUS capacitance kept small'),
    Component('D2', 'C15999', {'1': 'USB_DP', '2': 'GND', '3': 'USB_DM', '4': 'USB_DM', '5': 'VBUS', '6': 'USB_DP'}, 'usb'),
    Component('J2', 'C2988369', {'A1B12': 'GND', 'B1A12': 'GND', '1': 'GND', '2': 'GND', '3': 'GND', '4': 'GND', 'A4B9': 'VBUS', 'B4A9': 'VBUS', 'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DM', 'B7': 'USB_DM', 'A8': None, 'B8': None}, 'usb', value='', note='All Pico holes retained; prototype cable/underside fit pending'),
    Component('Q1', 'C8545', {'1': 'VBUS', '2': 'GND', '3': 'VBUS_N'}, 'usb'),
    Component('R3', 'C25905', {'1': 'CC1', '2': 'GND'}, 'usb', value='5.1k'),
    Component('R4', 'C25905', {'1': 'CC2', '2': 'GND'}, 'usb', value='5.1k'),
    Component('R5', 'C25118', {'1': 'USB_DP', '2': 'PROBE_DP'}, 'usb', value='47', note='At programmer PD4, USB D+'),
    Component('R6', 'C25118', {'1': 'USB_DM', '2': 'PROBE_DM'}, 'usb', value='47', note='At programmer PD3, USB D-'),
    Component('R7', 'C25741', {'1': '3V3_OUT', '2': 'VBUS_N'}, 'usb', value='100k'),
    Component('R8', 'C25741', {'1': 'VBUS', '2': 'GND'}, 'usb', value='100k', note='Discharge VBUS/gate after disconnect'),
    Component('R9', 'C25867', {'1': 'USB_DPU', '2': 'USB_DM'}, 'usb', value='1.5k', note='Low-speed USB pull-up'),
    # Open-source CH32V003 SWIO programmer
    Component('C6', 'C1525', {'1': '3V3_OUT', '2': 'GND'}, 'probe', value='100nF', note='At U2 VDD pin 9'),
    Component('D3', 'C2286', {'1': 'LED_A', '2': 'GND'}, 'probe', value='RED / PROBE'),
    Component('R10', 'C25744', {'1': 'PROBE_RUN', '2': '3V3_OUT'}, 'probe', value='10k'),
    Component('R11', 'C11702', {'1': 'PROBE_LED', '2': 'LED_A'}, 'probe', value='1k'),
    Component('U2', 'C5187096', {'1': 'PROBE_DP', '2': 'USB_DPU', '3': None, '4': 'PROBE_RUN', '5': None, '6': None, '7': 'GND', '8': None, '9': '3V3_OUT', '10': 'PROBE_LED', '11': 'PROBE_SWIO', '12': 'PROBE_SWIO', '13': None, '14': None, '15': None, '16': 'VBUS_N', '17': None, '18': 'PROBE_BOOT_SWIO', '19': 'TARGET_EN', '20': 'PROBE_DM'}, 'probe', value='', note='rv003usb; initial external SWIO provisioning'),
    # CH32V003 target and switched supply
    Component('C21', 'C1525', {'1': 'TARGET_3V3', '2': 'GND'}, 'target', value='100nF', note='At CH32 VDD pin 9'),
    Component('C22', 'C52923', {'1': 'TARGET_3V3', '2': 'GND'}, 'target', value='1uF'),
    Component('R14', 'C25744', {'1': 'PD7', '2': 'TARGET_3V3'}, 'target', value='10k', note='Keep PD7 option bytes in reset mode'),
    Component('R15', 'C25076', {'1': 'PROBE_SWIO', '2': 'PD1'}, 'target', value='100', note='Remove to isolate onboard SWIO'),
    Component('R16', 'C25905', {'1': 'PD1', '2': 'TARGET_3V3'}, 'target', value='5.1k', note='SWIO pull-up to switched target supply'),
    Component('SW1', 'C720477', {'1': 'PD7', '2': 'GND'}, 'target', value='TARGET RESET'),
    Component('U1', 'C5187096', {'1': 'PD4', '2': 'PD5', '3': 'PD6', '4': 'PD7', '5': 'PA1', '6': 'PA2', '7': 'GND', '8': 'PD0', '9': 'TARGET_3V3', '10': 'PC0', '11': 'PC1', '12': 'PC2', '13': 'PC3', '14': 'PC4', '15': 'PC5', '16': 'PC6', '17': 'PC7', '18': 'PD1', '19': 'PD2', '20': 'PD3'}, 'target'),
    # Pico header positions and programming pads
    Component('J1', 'PICO_HEADER', {'1': 'PD5', '2': 'PD6', '3': 'GND', '4': 'PD0', '5': 'PC3', '6': 'PC1', '7': 'PC2', '8': 'GND', '9': 'PD4', '10': 'PD3', '11': 'PD2', '12': None, '13': 'GND', '14': None, '15': None, '16': None, '17': None, '18': 'GND', '19': None, '20': None, '21': 'PC7', '22': 'PC0', '23': 'GND', '24': 'PC5', '25': 'PC6', '26': None, '27': None, '28': 'GND', '29': None, '30': 'PD7', '31': 'PA2', '32': 'PA1', '33': 'GND', '34': 'PC4', '35': None, '36': '3V3_OUT', '37': '3V3_EN', '38': 'GND', '39': 'VSYS', '40': 'VBUS'}, 'header', value='PICO 40-PIN', note='Bare PCB pads, not an assembled connector', fitted=False),
    Component('TP1', 'TESTPAD', {'1': 'PROBE_BOOT_SWIO'}, 'header', value='PROBE_BOOT_SWIO', note='Bare copper test pad', fitted=False),
    Component('TP2', 'TESTPAD', {'1': 'PROBE_RUN'}, 'header', value='PROBE_RUN', note='Bare copper test pad', fitted=False),
    Component('TP3', 'TESTPAD', {'1': 'TARGET_3V3'}, 'header', value='TARGET_3V3', note='Bare copper test pad', fitted=False),
    Component('TP4', 'TESTPAD', {'1': 'GND'}, 'header', value='GND', note='Bare copper test pad', fitted=False),
    Component('TP5', 'TESTPAD', {'1': 'PD1'}, 'header', value='PD1', note='Bare copper test pad', fitted=False),
    Component('TP6', 'TESTPAD', {'1': 'PD7'}, 'header', value='PD7', note='Bare copper test pad', fitted=False),
    Component('TP7', 'TESTPAD', {'1': '3V3_OUT'}, 'header', value='3V3_OUT', note='Bare copper test pad', fitted=False),
)

SECTIONS = {'power': 'USB/5 V input and two 3.3 V LDOs',
 'usb': 'USB-C low-speed HID, ESD and VBUS detection',
 'probe': 'Open-source CH32V003 SWIO programmer',
 'target': 'CH32V003 target and switched supply',
 'header': 'Pico header positions and programming pads'}
