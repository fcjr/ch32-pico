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
      for i,n in enumerate(('GND','VBUS','VSYS','VIN_SYS','3V3_OUT','PD_INPUT'),1)),
    # Diode OR feeds ONLY the control supply. Header VSYS never sees PD VBUS.
    two('D1','C8598','VIN_SYS','VBUS','power','B5819W','Cathode pin 1; control-rail current only'),
    two('D4','C8598','VIN_SYS','VSYS','power','B5819W','Cathode pin 1; blocks PD backfeed into header 39'),
    Component('U4','C780769',{'1':'3V3_OUT','2':'3V3_EN','3':'VIN_SYS','4':'GND','5':'BUCK_SW','6':'BUCK_BST'},'power',note='AP63203 fixed 3.3 V; EN to header 37; ground to shut down, release for autostart'),
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
    # MX26631 integrates the reverse-blocking driver. Q1 source faces VBUS;
    # Q2 pulls its gate to source on reverse voltage. MODE grounded enables
    # ILIM fault detection. PGTH grounded keeps recovery slew controlled.
    Component('U3','C18197523',{'1':'PD_INPUT','2':'PD_INPUT','3':'PD_GATE','4':'PD_DRV',
        '5':'VBUS','6':'VBUS','7':'PD_OVLO','8':'GND','9':'PD_DVDT',
        '10':'PD_ILM','11':'GND','12':'PD_SHDN','13':'PD_IMON','14':'PD_FAULT_N',
        '15':'GND','16':None,'17':'PD_OUT','18':'PD_OUT',
        **{str(i):None for i in range(19,25)},'25':'GND'},'pd',
        note='MX26631DL: auto-retry current limiting; external Q1/Q2 reverse blocking; PGTH and MODE grounded'),
    Component('Q1','C431191',{'1':'VBUS','2':'VBUS','3':'VBUS','4':'PD_GATE',
        **{str(i):'PD_INPUT' for i in range(5,10)}},'pd',note='AON7264E, 60 V, +/-20 V gate; source at VBUS, drain at PD_INPUT'),
    Component('Q2','C40912',{'1':'PD_DRV','2':'VBUS','3':'PD_GATE'},'pd',
        note='BSS138-7-F fast gate pull-down; referenced to VBUS, not GND; reverse turn-off needs bench validation'),
    Component('U6','C132788',{'1':'PD_SHDN','2':'GND','3':'PD_UV_SENSE','4':'GND',
        '5':'3V3_OUT','6':None},'pd',note='TPS3701 hardware undervoltage interlock; unused OV input grounded and output NC'),
    two('R7','C25744','PD_ENABLE','GND','pd','10k','Default OFF while MCU blank, reset or bootloader'),
    two('R26','C25900','PD_ENABLE','PD_SHDN','pd','4.7k','Allows U6 to force shutdown without shorting a push-pull GPIO'),
    two('R27','C852928','VBUS','PD_UV_SENSE','pd','82.5k / 0.1%'),
    two('R28','C852919','PD_UV_SENSE','GND','pd','7.68k / 0.1%'),
    two('R8','C25741','PD_OUT','GND','pd','100k','Low-dissipation output bleed; wait for measured discharge before voltage changes'),
    two('R9','C25744','PD_FAULT_N','3V3_OUT','pd','10k'),
    two('C8','C1532','PD_DVDT','GND','pd','22nF / 50V','Nominal 2.29 V/ms slew; load driver must remain disabled during startup'),
    two('C12','C51205','PD_OUT','GND','pd','4.7uF / 50V','X7R 1206; DC-bias screened using Samsung characteristic data'),
    two('C14','C28323','PD_INPUT','GND','pd','1uF / 50V','Local eFuse input bypass'),
    two('C16','C28323','VBUS','GND','pd','1uF / 50V','Local IN_SYS and blocking-FET source bypass'),
    two('C17','C307331','3V3_OUT','GND','pd','100nF / 50V','U6 local supply bypass'),
    two('R17','C25749','PD_ILM','GND','pd','11k','40/R_kohm gives 3.636 A nominal; +/-15% engineering screen is not a guaranteed tolerance; bench qualification required'),
    two('R25','C190095','PD_IMON','GND','pd','10k / 0.1%','Separate current monitor: nominal 0.260 V/A above 2 A'),
    two('R20','C852928','VBUS','PD_OVLO','pd','82.5k / 0.1%','25 ppm/C thin film'),
    two('R21','C851038','PD_OVLO','GND','pd','4.75k / 0.1%','Static OVLO tolerance screened; TVS clamps input transients'),
    *(Component(ref,'C523793',{'1':'GND','2':'GND','3':'GND','4':net,'5':net,'6':net,'7':'GND'},
        'pd',note='TVS2200; 22 V standoff, 28.35 V specified hot surge clamp; no continuous regeneration rating')
        for ref,net in (('D5','VBUS'),('D6','PD_OUT'))),
    two('D7','C5709679','PD_OUT','GND','pd','PMEG4030ER-QX','Cathode at OUT; local negative-transient Schottky per TI layout guidance'),
    two('R1','C25741','VBUS','VBUS_SENSE','pd','100k'),
    two('R2','C25744','VBUS_SENSE','GND','pd','10k'),
    two('R5','C25741','PD_OUT','PDOUT_SENSE','pd','100k'),
    two('R6','C25744','PDOUT_SENSE','GND','pd','10k'),
    two('C9','C307331','VBUS_SENSE','GND','pd','100nF / 50V'),
    two('C10','C307331','PDOUT_SENSE','GND','pd','100nF / 50V'),
    two('R24','C11702','PD_IMON','CURRENT_SENSE','pd','1k','ADC filter on independent IMON output'),
    two('C13','C307331','CURRENT_SENSE','GND','pd','100nF / 50V'),
    Component('U1',MCU_PART,mcu_nets(),'target',note='Only MCU; native USB, CC1/CC2 PD PHY, SDI recovery'),
    two('C6','C307331','3V3_OUT','GND','target','100nF / 50V','Adjacent to U1 pins 48/47'),
    two('C7','C52923','3V3_OUT','GND','target','1uF'),
    two('R10','C25744','PA21','3V3_OUT','target','10k','Keep PA21 configured as reset in option bytes'),
    two('R11','C11702','STATUS_LED','LED_A','target','1k'),
    two('D3','C2286','LED_A','GND','target','RED / STATUS'),
    two('R12','C25900','USB_DP','BOOT_PULLUP','target','4.7k','WCH reference download-button pull-up'),
    two('SW1','C720478','PA21','GND','target','RESET'),
    two('SW2','C720478','BOOT_PULLUP','3V3_OUT','target','BOOT','Hold during power-up, release before USB ISP'),
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
