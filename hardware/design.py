# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Mechanical contract and proposed electrical allocation.

Coordinates are mm, viewed from the component side with USB at the top.
Origin is the upper-left board corner. The netlist is in hardware/circuit.py.
"""
from __future__ import annotations


from dataclasses import dataclass

BOARD_REVISION = 'B'


@dataclass(frozen=True)
class Mechanical:
    width: float = 21.0
    length: float = 51.0
    thickness: float = 1.0
    pitch: float = 2.54
    row_spacing: float = 17.78
    header_drill: float = 1.0
    header_pad: float = 1.6
    mounting_drill: float = 2.1

    def position(self, pin: int) -> tuple[float, float]:
        if not 1 <= pin <= 40:
            raise ValueError(f"Invalid Pico pin: {pin}")
        x = (self.width - self.row_spacing) / 2
        y = (self.length - 19 * self.pitch) / 2
        if pin <= 20:
            return round(x, 3), round(y + (pin - 1) * self.pitch, 3)
        return round(self.width - x, 3), round(y + (40 - pin) * self.pitch, 3)

    @property
    def mounting_holes(self) -> tuple[tuple[float, float], ...]:
        return ((4.8, 2.0), (16.2, 2.0), (4.8, 49.0), (16.2, 49.0))


@dataclass(frozen=True)
class HeaderPin:
    number: int
    pico: str
    proposed: str
    function: str


MECHANICAL = Mechanical()

# Rev B separates the negotiated USB rail from Pico carrier power pins.
MCU_PART = 'C29779902'
MCU_MPN = 'CH32X035C8T6'
POWER_REQUIREMENTS = {
    "topology": "fixed-3v3-buck-and-switched-pd-vbus",
    "vsys_min_v": 4.3, "vsys_max_v": 5.5, "output_v": 3.3,
    "header_current_goal_ma": 50, "usb_backfeed_allowed": False,
    "pd_voltage_steps_v": (5, 9, 12, 15, 20),
    "pd_output_current_goal_ma": 5000,
    "pd_output_location": "Pico pin 40, replaces fixed 5 V VBUS",
}

# WCH CH32X035 datasheet, LQFP48 pin diagram and table 2-1.
TARGET_PINS = dict(zip(
    ('PA15 PA16 PA17 PA18 PA19 PA20 PA21 PA22 PA23 PA0 PA1 PA2 '
     'PA3 PA4 PA5 PA6 PA7 PC6 PC7 PB0 PB1 PB2 PB3 PB4 PB5 PB6 PB7 '
     'PB8 PB9 PB10 PB11 PC16 PC17 PC18 PB12 PB13 PC19 PC14 PC15 '
     'PA8 PA9 PA10 PA11 PA12 PA13 PA14 VSS VDD').split(),range(1,49)))

# Pins reserved for USB, PD, recovery and board power control.
INTERNAL_SIGNALS = {
    'PC16':'USB_DM', 'PC17':'USB_DP', 'PC14':'CC1', 'PC15':'CC2',
    'PC18':'SDIO', 'PC19':'SDCK', 'PB0':'VBUS_SENSE',
    'PB1':'PDOUT_SENSE', 'PB2':'PD_ENABLE', 'PB3':'STATUS_LED',
    'PB4':'PD_FAULT_N', 'PA3':'CURRENT_SENSE',
}

HEADER = tuple(HeaderPin(*row) for row in (
    (1, "GP0", "PB10", "USART1 TX, default mapping"),
    (2, "GP1", "PB11", "USART1 RX, default mapping"),
    (3, "GND", "GND", "Ground"),
    (4, "GP2", "PA8", "GPIO"),
    (5, "GP3", "PA9", "GPIO"),
    (6, "GP4", "PA11", "I2C SDA, default mapping"),
    (7, "GP5", "PA10", "I2C SCL, default mapping"),
    (8, "GND", "GND", "Ground"),
    (9, "GP6", "PA12", "GPIO"),
    (10, "GP7", "PA13", "GPIO"),
    (11, "GP8", "PA14", "GPIO"),
    (12, "GP9", "PA15", "GPIO; USART2 TX remap 2"),
    (13, "GND", "GND", "Ground"),
    (14, "GP10", "PA16", "GPIO; USART2 RX remap 2"),
    (15, "GP11", "PA17", "GPIO"),
    (16, "GP12", "PA18", "GPIO"),
    (17, "GP13", "PA19", "GPIO"),
    (18, "GND", "GND", "Ground"),
    (19, "GP14", "PA20", "GPIO"),
    (20, "GP15", "PA22", "GPIO"),
    (21, "GP16", "PA6", "SPI MISO, default mapping"),
    (22, "GP17", "PA4", "SPI NSS or software chip select"),
    (23, "GND", "GND", "Ground"),
    (24, "GP18", "PA5", "SPI SCK, default mapping"),
    (25, "GP19", "PA7", "SPI MOSI, default mapping"),
    (26, "GP20", "PB6", "GPIO"),
    (27, "GP21", "PB7", "GPIO"),
    (28, "GND", "GND", "Ground"),
    (29, "GP22", "PA23", "GPIO"),
    (30, "RUN", "PA21", "RST input; preserve reset option-byte configuration"),
    (31, "GP26 / ADC0", "PA0", "ADC channel 0"),
    (32, "GP27 / ADC1", "PA1", "ADC channel 1"),
    (33, "AGND", "GND", "Continuous ground plane"),
    (34, "GP28 / ADC2", "PA2", "ADC channel 2"),
    (35, "ADC_VREF", "NC", "No independent external ADC reference input"),
    (36, "3V3_OUT", "3V3_OUT", "Fixed 3.3 V output; prototype load rating pending"),
    (37, "3V3_EN", "NC", "Reserved; isolated from high-voltage regulator control"),
    (38, "GND", "GND", "Ground"),
    (39, "VSYS", "VSYS", "4.3-5.5 V input only; diode-isolated from PD VBUS"),
    (40, "VBUS", "PD_OUT", "Switched negotiated 5-20 V output; incompatible with fixed-5V Pico carriers"),
))


def validate() -> None:
    if [p.number for p in HEADER] != list(range(1,41)):
        raise ValueError("Header must contain pins 1 through 40 exactly once")
    signals=[p.proposed for p in HEADER if p.proposed in TARGET_PINS]
    if len(set(signals)) != len(signals) or len(signals)!=27:
        raise ValueError("Require 26 distinct GPIOs and one reset input")
    if set(signals) & set(INTERNAL_SIGNALS):
        raise ValueError("Board controls, USB, PD and debug must not share header GPIO")
    if any(p.proposed!='GND' for p in HEADER if p.pico in {'GND','AGND'}):
        raise ValueError("Pico ground positions must remain ground")
    if {p.number for p in HEADER if p.proposed=='NC'}!={35,37}:
        raise ValueError("Rev B reserves ADC_VREF and 3V3_EN header positions")
