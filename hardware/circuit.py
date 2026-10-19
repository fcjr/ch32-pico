# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Electrical source. Every terminal has an explicit net or NC.

CH32X035 is the only MCU and PD controller. Header pin 40 is USB VBUS,
unswitched like the Pico's; the fixed buck powers only the MCU and 3V3 header.
Prototype, not released.
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
    for d in DIAGNOSTICS:
        if d.net in TARGET_PINS:nets[str(TARGET_PINS[d.net])]=d.net
    nets[str(TARGET_PINS['PC7'])]='PC7'  # SJ1 optional header connection
    nets['47']='GND';nets['48']='3V3_OUT'
    return nets


COMPONENTS = (
    *(Component(f'#FLG{i:02}', 'POWER_FLAG', {'1':n}, 'power', n, fitted=False)
      for i,n in enumerate(('GND','VBUS','VSYS','VIN_SYS','3V3_OUT'),1)),
    # Diode OR feeds ONLY the control supply. Header VSYS never sees PD VBUS.
    two('D1','C8598','VIN_SYS','VBUS','power','B5819W','Cathode pin 1; control-rail current only'),
    two('D4','C8598','VIN_SYS','VSYS','power','B5819W','Cathode pin 1; blocks PD backfeed into header 39'),
    Component('U4','C2927130',{'1':'BUCK_BST','2':'GND','3':'BUCK_FB','4':'3V3_EN','5':'VIN_SYS','6':'BUCK_SW'},'power',note='SY8301 2 MHz buck, 0.8 V reference; EN pulled up to VIN_SYS by R15, header 37 grounds it to shut down'),
    two('R13','C25792','3V3_OUT','BUCK_FB','power','47k','Feedback divider top; senses the output capacitors through a dedicated trace'),
    two('R14','C25756','BUCK_FB','GND','power','15k','Feedback divider bottom: 0.8 V x (1 + 47/15) = 3.307 V'),
    two('R15','C25741','VIN_SYS','3V3_EN','power','100k','EN pull-up to the diode-OR node so VSYS-only power still starts the regulator'),
    two('L1','C48496','BUCK_SW','3V3_OUT','power','4.7uH'),
    two('C1','C13585','VIN_SYS','GND','power','10uF / 50V','Input capacitance/inrush requires bench qualification'),
    two('C2','C29277','3V3_OUT','GND','power','22uF / 10V'),
    two('C3','C29277','3V3_OUT','GND','power','22uF / 10V'),
    two('C4','C307331','BUCK_BST','BUCK_SW','power','100nF / 50V'),
    # Native USB. CC pins have independent external Rd, even while MCU is blank.
    Component('J2','C963411',{'A1B12':'GND','B1A12':'GND',**{str(i):'GND' for i in range(13,17)},'A4B9':'VBUS','B4A9':'VBUS','A5':'CC1','B5':'CC2','A6':'USB_DP','B6':'USB_DP','A7':'USB_DM','B7':'USB_DM','A8':None,'B8':None},'usb',note='G-Switch AW drawing 2023-02-01: 5 A VBUS; qualify cable and assembly fit'),
    two('R3','C25905','CC1','GND','usb','5.1k'),
    two('R4','C25905','CC2','GND','usb','5.1k'),
    Component('D2','C7519',{'1':'USB_DP','2':'GND','3':'USB_DM','4':'USB_DM','5':'3V3_OUT','6':'USB_DP'},'usb',note='ESD rail is 3.3 V, NEVER negotiated VBUS'),
    two('C11','C307331','3V3_OUT','GND','usb','100nF / 50V'),
    # Pin 40 is direct VBUS. D5 clamps cable hot-plug ringing below U4's
    # 32 V operating limit when a source is already at a higher PD voltage.
    Component('D5','C523793',{'1':'GND','2':'GND','3':'GND','4':'VBUS','5':'VBUS','6':'VBUS','7':'GND'},
        'pd',note='TVS2200; 22 V standoff, 28.35 V specified hot surge clamp; no continuous regeneration rating'),
    two('R1','C25741','VBUS','VBUS_SENSE','pd','100k'),
    two('R2','C25744','VBUS_SENSE','GND','pd','10k'),
    two('C9','C307331','VBUS_SENSE','GND','pd','100nF / 50V'),
    Component('U1',MCU_PART,mcu_nets(),'target',note='Only MCU; native USB, CC1/CC2 PD PHY, SDI recovery'),
    two('C6','C307331','3V3_OUT','GND','target','100nF / 50V','Adjacent to U1 pins 48/47'),
    two('C7','C52923','3V3_OUT','GND','target','1uF'),
    two('R10','C25744','PA21','3V3_OUT','target','10k','Keep PA21 configured as reset in option bytes'),
    two('R11','C11702','STATUS_LED','LED_A','target','1k'),
    two('D3','C2286','LED_A','GND','target','RED / STATUS'),
    two('R12','C25900','USB_DP','BOOT_PULLUP','target','4.7k','WCH reference download-button pull-up'),
    two('SW1','C49234124','PA21','GND','target','RESET'),
    two('SW2','C49234124','BOOT_PULLUP','3V3_OUT','target','BOOT','Hold during power-up, release before USB ISP'),
    Component('J1','PICO_HEADER',{str(p.number):None if p.proposed=='NC' else p.proposed for p in HEADER},'header','PICO 40-PIN','Pin 40 is USB VBUS: 5 V by default, higher only after PD negotiation',False),
    Component('SJ1','SOLDER_JUMPER',{'1':'GPIO35','2':'PC7'},'header','PC7 OPTION','Normally open; user solder bridge connects header 35 to PC7. No factory paste or assembly.',False),
    *(Component(f'TP{i}','TESTPAD',{'1':n},'header',n,'SDI recovery / measurement pad',False)
      for i,n in enumerate(('SDIO','SDCK','3V3_OUT','GND','PA21'),1)),
    *(Component(f'TP{i}','TESTPAD',{'1':n},'header',n,'Underside expansion solder pad',False)
      for i,n in enumerate((*EXPANSION_SIGNALS,'GND'),6)),
    *(Component(d.ref,d.part,{'1':d.net},'header',d.net,
                'Diagnostic probe contact; no paste or fitted component',False) for d in DIAGNOSTICS),
)
SECTIONS={'power':'Fixed 3.3 V control supply','usb':'Native USB-C and PD CC interface',
          'pd':'VBUS clamp and sense','target':'CH32X035 and USB boot entry',
          'header':'Pico headers and SDI recovery'}
