# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Rev E electrical source. Every terminal has an explicit net or NC.

CH32X035 is the only MCU and PD controller. PD_OUT is switched VBUS;
the fixed buck powers only the MCU and 3V3 header. Prototype, not released.
"""
from __future__ import annotations
from dataclasses import dataclass
from .diagnostics import DIAGNOSTICS
from .design import HEADER, TARGET_PINS, INTERNAL_SIGNALS, MCU_PART, EXPANSION_SIGNALS

@dataclass(frozen=True)
class Component:
    ref: str
    part: str
    nets: dict[str, str | None]
    section: str
    value: str = ''
    note: str = ''
    fitted: bool = True


def two(ref, part, a, b, section, value='', note=''):
    return Component(ref,part,{'1':a,'2':b},section,value,note)


def mcu_nets():
    nets={str(n):None for n in TARGET_PINS.values()}
    for p in HEADER:
        if p.proposed in TARGET_PINS:nets[str(TARGET_PINS[p.proposed])]=p.proposed
    for port,net in INTERNAL_SIGNALS.items():nets[str(TARGET_PINS[port])]=net
    for port in EXPANSION_SIGNALS:
        if port in TARGET_PINS:nets[str(TARGET_PINS[port])]=port
    nets[str(TARGET_PINS['PC7'])]='PC7'  # SJ1 optional header connection
    nets['47']='GND';nets['48']='3V3_OUT'
    return nets


COMPONENTS = (
    *(Component(f'#FLG{i:02}', 'POWER_FLAG', {'1':n}, 'power', n, fitted=False)
      for i,n in enumerate(('GND','VBUS','VSYS','VIN_SYS','3V3_OUT'),1)),
    # Diode OR feeds ONLY the control supply. Header VSYS never sees PD VBUS.
    two('D1','C8598','VIN_SYS','VBUS','power','B5819W','Cathode pin 1; control-rail current only'),
    two('D4','C8598','VIN_SYS','VSYS','power','B5819W','Cathode pin 1; blocks PD backfeed into header 39'),
    Component('U4','C780769',{'1':'3V3_OUT','2':'3V3_EN','3':'VIN_SYS','4':'GND','5':'BUCK_SW','6':'BUCK_BST'},'power',note='AP63203 fixed 3.3 V; EN to header 37; ground to shut down, release for autostart'),
    two('L1','C48496','BUCK_SW','3V3_OUT','power','4.7uH'),
    two('C1','C13585','VIN_SYS','GND','power','10uF / 50V','Input capacitance/inrush requires bench qualification'),
    two('C2','C29277','3V3_OUT','GND','power','22uF / 10V'),
    two('C3','C29277','3V3_OUT','GND','power','22uF / 10V'),
    two('C4','C1525','BUCK_BST','BUCK_SW','power','100nF / 50V'),
    # Native USB. CC pins have independent external Rd, even while MCU is blank.
    Component('J2','C963411',{'A1B12':'GND','B1A12':'GND',**{str(i):'GND' for i in range(13,17)},'A4B9':'VBUS','B4A9':'VBUS','A5':'CC1','B5':'CC2','A6':'USB_DP','B6':'USB_DP','A7':'USB_DM','B7':'USB_DM','A8':None,'B8':None},'usb',note='G-Switch AW drawing 2023-02-01: 5 A VBUS; qualify cable and assembly fit'),
    two('R3','C25905','CC1','GND','usb','5.1k'),
    two('R4','C25905','CC2','GND','usb','5.1k'),
    two('C5','C1525','VBUS','GND','usb','100nF / 50V'),
    Component('D2','C7519',{'1':'USB_DP','2':'GND','3':'USB_DM','4':'USB_DM','5':'3V3_OUT','6':'USB_DP'},'usb',note='ESD rail is 3.3 V, NEVER negotiated VBUS'),
    two('C11','C1525','3V3_OUT','GND','usb','100nF / 50V'),
    # Load switch: integrated back-to-back FETs, reverse blocking, current limit,
    # OVLO, controlled slew, thermal shutdown and latch-off. No PD controller here.
    Component('U3','C3662793',{'1':'PD_ENABLE','2':'PD_OVLO','3':None,'4':'PD_FAULT_N','5':'VBUS','6':'PD_OUT','7':'PD_DVDT','8':'GND','9':'PD_ILM','10':None},'pd',note='TPS259470L; 470 variant required for adjustable OVLO, not 472 clamp variant'),
    two('R7','C25744','PD_ENABLE','GND','pd','10k','Default OFF while MCU blank, reset or bootloader'),
    two('R8','C25744','PD_OUT','GND','pd','10k','Output bleed; external capacitance affects discharge time'),
    two('R9','C25744','PD_FAULT_N','3V3_OUT','pd','10k'),
    two('C8','C1525','PD_DVDT','GND','pd','100nF / 50V','Slew capacitor rated above VBUS + 5 V'),
    two('C12','C1525','PD_OUT','GND','pd','100nF / 50V'),
    two('R17','C11702','PD_ILM','GND','pd','1k','Parallel R18: 600 ohm, ~5.56 A nominal fault limit; not usable-load rating'),
    two('R18','C25867','PD_ILM','GND','pd','1.5k'),
    two('R20','C4142','VBUS','PD_OVLO','pd','82k'),
    two('R21','C25900','PD_OVLO','GND','pd','4.7k','OVLO nominal 22.14 V; resistor and comparator tolerances reviewed'),
    two('R1','C25741','VBUS','VBUS_SENSE','pd','100k'),
    two('R2','C25744','VBUS_SENSE','GND','pd','10k'),
    two('R5','C25741','PD_OUT','PDOUT_SENSE','pd','100k'),
    two('R6','C25744','PDOUT_SENSE','GND','pd','10k'),
    two('C9','C1525','VBUS_SENSE','GND','pd','100nF / 50V'),
    two('C10','C1525','PDOUT_SENSE','GND','pd','100nF / 50V'),
    two('R24','C11702','PD_ILM','CURRENT_SENSE','pd','1k','ADC filter isolates ILM programming node'),
    two('C13','C1525','CURRENT_SENSE','GND','pd','100nF / 50V'),
    Component('U1',MCU_PART,mcu_nets(),'target',note='Only MCU; native USB, CC1/CC2 PD PHY, SDI recovery'),
    two('C6','C1525','3V3_OUT','GND','target','100nF / 50V','Adjacent to U1 pins 48/47'),
    two('C7','C52923','3V3_OUT','GND','target','1uF'),
    two('R10','C25744','PA21','3V3_OUT','target','10k','Keep PA21 configured as reset in option bytes'),
    two('R11','C11702','STATUS_LED','LED_A','target','1k'),
    two('D3','C2286','LED_A','GND','target','RED / STATUS'),
    two('R12','C25900','USB_DP','BOOT_PULLUP','target','4.7k','WCH reference download-button pull-up'),
    two('SW1','C720477','PA21','GND','target','RESET'),
    two('SW2','C720477','BOOT_PULLUP','3V3_OUT','target','BOOT','Hold during power-up, release before USB ISP'),
    Component('J1','PICO_HEADER',{str(p.number):None if p.proposed=='NC' else p.proposed for p in HEADER},'header','PICO 40-PIN','Pin 40 is switched 5-20 V; not fixed 5 V VBUS',False),
    Component('SJ1','SOLDER_JUMPER',{'1':'GPIO35','2':'PC7'},'header','PC7 OPTION','Normally open; user solder bridge connects header 35 to PC7. No factory paste or assembly.',False),
    *(Component(f'TP{i}','TESTPAD',{'1':n},'header',n,'SDI recovery / measurement pad',False)
      for i,n in enumerate(('SDIO','SDCK','3V3_OUT','GND','PA21'),1)),
    *(Component(f'TP{i}','TESTPAD',{'1':n},'header',n,'Underside expansion solder pad',False)
      for i,n in enumerate((*EXPANSION_SIGNALS,'GND'),6)),
    *(Component(d.ref,d.part,{'1':d.net},'header',d.net,
                'Diagnostic probe contact; no paste or fitted component',False) for d in DIAGNOSTICS),
)
SECTIONS={'power':'Fixed 3.3 V control supply','usb':'Native USB-C and PD CC interface',
          'pd':'Switched negotiated VBUS output','target':'CH32X035 and USB boot entry',
          'header':'Pico headers and SDI recovery'}
