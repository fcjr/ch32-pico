# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Mechanical contract and proposed electrical allocation.

Coordinates are mm, viewed from the component side with USB at the top.
Origin is the upper-left board corner. The netlist is in hardware/circuit.py.
"""
from __future__ import annotations


from dataclasses import dataclass

BOARD_REVISION = 'A'


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

# Requirements, not measured capabilities. Component selection and prototype
# testing must establish startup, load capacity, and enable behavior.
POWER_REQUIREMENTS = {
    "topology": "dual-LDO",
    "vsys_min_v": 4.3,
    "vsys_max_v": 5.5,
    "output_v": 3.3,
    "header_current_goal_ma": 50,
    "usb_backfeed_allowed": False,
}

# CH32V003F4P6 TSSOP-20 physical package pins, independent of header numbering.
TARGET_PINS = {
    "PD4": 1, "PD5": 2, "PD6": 3, "PD7": 4,
    "PA1": 5, "PA2": 6, "VSS": 7, "PD0": 8, "VDD": 9,
    "PC0": 10, "PC1": 11, "PC2": 12, "PC3": 13, "PC4": 14,
    "PC5": 15, "PC6": 16, "PC7": 17, "PD1": 18, "PD2": 19, "PD3": 20,
}

HEADER = tuple(HeaderPin(*row) for row in (
    (1, "GP0", "PD5", "USART1 TX"),
    (2, "GP1", "PD6", "USART1 RX; no onboard UART bridge"),
    (3, "GND", "GND", "Ground"),
    (4, "GP2", "PD0", "GPIO"),
    (5, "GP3", "PC3", "GPIO"),
    (6, "GP4", "PC1", "I2C1 SDA"),
    (7, "GP5", "PC2", "I2C1 SCL"),
    (8, "GND", "GND", "Ground"),
    (9, "GP6", "PD4", "GPIO / TIM2 CH1 / ADC A7"),
    (10, "GP7", "PD3", "GPIO / TIM2 CH2 / ADC A4"),
    (11, "GP8", "PD2", "GPIO / TIM1 CH1 / ADC A3"),
    (12, "GP9", "NC", "Unconnected"),
    (13, "GND", "GND", "Ground"),
    (14, "GP10", "NC", "Unconnected"),
    (15, "GP11", "NC", "Unconnected"),
    (16, "GP12", "NC", "Unconnected"),
    (17, "GP13", "NC", "Unconnected"),
    (18, "GND", "GND", "Ground"),
    (19, "GP14", "NC", "Unconnected"),
    (20, "GP15", "NC", "Unconnected"),
    (21, "GP16", "PC7", "SPI1 MISO"),
    (22, "GP17", "PC0", "Software-controlled SPI chip select"),
    (23, "GND", "GND", "Ground"),
    (24, "GP18", "PC5", "SPI1 SCK"),
    (25, "GP19", "PC6", "SPI1 MOSI"),
    (26, "GP20", "NC", "Unconnected"),
    (27, "GP21", "NC", "Unconnected"),
    (28, "GND", "GND", "Ground"),
    (29, "GP22", "NC", "Unconnected"),
    (30, "RUN", "PD7", "Target reset; retain reset option-byte configuration"),
    (31, "GP26 / ADC0", "PA2", "ADC A0; use internal target oscillator"),
    (32, "GP27 / ADC1", "PA1", "ADC A1; use internal target oscillator"),
    (33, "AGND", "GND", "Ground; continuous ground plane"),
    (34, "GP28 / ADC2", "PC4", "ADC A2"),
    (35, "ADC_VREF", "NC", "No external ADC reference input on CH32V003"),
    (36, "3V3_OUT", "3V3_OUT", "3.3 V output; current budget pending regulator selection"),
    (37, "3V3_EN", "3V3_EN", "Pull low to disable board supply, including onboard probe"),
    (38, "GND", "GND", "Ground"),
    (39, "VSYS", "VSYS", "4.3-5.5 V provisional input range; qualify LDO dropout/thermal limits"),
    (40, "VBUS", "VBUS", "USB 5 V; isolate VSYS from upstream USB"),
))


def validate() -> None:
    if [p.number for p in HEADER] != list(range(1, 41)):
        raise ValueError("Header must contain pins 1 through 40 exactly once")
    signals = [p.proposed for p in HEADER if p.proposed.startswith(("PA", "PC", "PD"))]
    if len(set(signals)) != len(signals):
        raise ValueError("Do not duplicate GPIOs to fill unused Pico positions")
    if set(signals) != set(TARGET_PINS) - {"VSS", "VDD", "PD1"}:
        raise ValueError("Every target GPIO except reserved SWIO must be accounted for")
    if any(p.proposed != "GND" for p in HEADER if p.pico in {"GND", "AGND"}):
        raise ValueError("Pico ground positions must remain ground")
