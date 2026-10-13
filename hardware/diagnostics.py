# SPDX-License-Identifier: MIT
"""Bare diagnostic contacts. Coordinates use the front-view board convention.

USB contacts lie within existing F.Cu traces; they add mask openings, not stubs.
The underside measurement pads are 1 mm; the shared LED control pad is 0.6 mm.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Diagnostic:
    ref: str
    net: str
    label: str
    position: tuple[float, float]
    text_position: tuple[float, float]
    side: str = 'B'
    part: str = 'TESTPAD'


DIAGNOSTICS = (
    Diagnostic('TP14','CURRENT_SENSE','ISNS',(9.4,32.2),(9.4,30.9)),
    Diagnostic('TP15','VBUS','VBUS',(8.6,4.9),(9,7.3)),
    Diagnostic('TP16','GND','GND',(11.3,4.4),(11,5.9)),
    Diagnostic('TP17','VBUS_SENSE','VSNS',(8,21.6),(8,22.75)),
    Diagnostic('TP18','PDOUT_SENSE','OSNS',(14.2,25.6),(11.5,25.6)),
    Diagnostic('TP19','CC1','CC1',(7.8565,9),(7.8565,10.4)),
    Diagnostic('TP20','CC2','CC2',(10.8,10.2),(10.8,11.35)),
    Diagnostic('TP21','PD_ENABLE','PDEN',(12.3,18.3),(12.3,19.45)),
    Diagnostic('TP22','STATUS_LED','PB3',(14.5,34.2),(14.7,33.05),'B','SMALL_PROBE'),
    Diagnostic('TP23','USB_DP','D+',(13.8,22.3),(14.6,21.2),'F','USB_PROBE'),
    Diagnostic('TP24','USB_DM','D-',(14.7,22.7),(15.8,23.8),'F','USB_PROBE'),
)

# VBUS needs a leader around the connector locating hole to avoid ambiguity.
LEADERS = {"TP15": ((8.9,6.5),(8.7,5.65))}
