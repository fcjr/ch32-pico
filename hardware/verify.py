# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Independent KiCad XML-netlist comparison and circuit contract checks."""
from collections import defaultdict
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from .circuit import COMPONENTS
from .library import load_library, validate_library
from .design import HEADER, TARGET_PINS

ROOT=Path(__file__).resolve().parents[1]


def verify_contract(components=COMPONENTS):
    library=load_library()
    validate_library(components,library)
    c={x.ref:x for x in components}
    def require(ref, pins):
        for pin,net in pins.items():
            if c[ref].nets[str(pin)]!=net:
                raise ValueError(f'Contract violation: {ref}.{pin} must be {net}')
    from .design import INTERNAL_SIGNALS, MCU_PART, EXPANSION_SIGNALS, validate
    validate()
    if c['U1'].part != MCU_PART or any(x.part=='C5187096' for x in components):
        raise ValueError('The X035 design requires one X035 and no V003 programmer')
    require('U1',{47:'GND',48:'3V3_OUT',7:'PA21',32:'USB_DM',33:'USB_DP',
                  34:'SDIO',37:'SDCK',38:'CC1',39:'CC2'})
    require('D1',{1:'VIN_SYS',2:'VBUS'})
    require('D4',{1:'VIN_SYS',2:'VSYS'})
    require('D2',{2:'GND',5:'3V3_OUT'})
    require('U4',{1:'3V3_OUT',2:'3V3_EN',3:'VIN_SYS',4:'GND',5:'BUCK_SW',6:'BUCK_BST'})
    require('L1',{1:'BUCK_SW',2:'3V3_OUT'})
    require('U3',{1:'PD_ENABLE',2:'PD_OVLO',4:'PD_FAULT_N',5:'VBUS',6:'PD_OUT',8:'GND',9:'PD_ILM'})
    if c['U3'].part!='C3662793':raise ValueError('Use the reviewed 470L load-switch variant')
    require('R7',{1:'PD_ENABLE',2:'GND'})
    require('R3',{1:'CC1',2:'GND'});require('R4',{1:'CC2',2:'GND'})
    require('J2',{'A5':'CC1','B5':'CC2','A6':'USB_DP','B6':'USB_DP','A7':'USB_DM','B7':'USB_DM',
                  'A4B9':'VBUS','B4A9':'VBUS'})
    for p in HEADER:
        require('J1',{p.number:None if p.proposed=='NC' else p.proposed})
        if p.proposed in TARGET_PINS:require('U1',{TARGET_PINS[p.proposed]:p.proposed})
    for port,net in INTERNAL_SIGNALS.items():require('U1',{TARGET_PINS[port]:net})
    for i,port in enumerate(EXPANSION_SIGNALS,6):
        if port in TARGET_PINS:require('U1',{TARGET_PINS[port]:port})
        require(f'TP{i}',{1:port})
    require('TP13',{1:'GND'})
    from .diagnostics import DIAGNOSTICS
    for d in DIAGNOSTICS:
        require(d.ref,{1:d.net})
        if c[d.ref].fitted:raise ValueError('Diagnostic pads must be bare copper')
    require('SJ1',{1:'GPIO35',2:'PC7'})
    require('U1',{19:'PC7',24:'PD_FAULT_N'})
    require('R9',{1:'PD_FAULT_N',2:'3V3_OUT'})
    pc7_nodes={(x.ref,p) for x in components for p,n in x.nets.items() if n=='PC7'}
    if pc7_nodes!={('U1','19'),('SJ1','2')}:
        raise ValueError('PC7 must connect only MCU and SJ1; TP7 is FAULT')
    if c['SJ1'].fitted:
        raise ValueError('SJ1 must remain a bare, normally open copper jumper')
    jumper_nodes={(x.ref,p) for x in components for p,n in x.nets.items() if n=='GPIO35'}
    if jumper_nodes!={('J1','35'),('SJ1','1')}:
        raise ValueError('Header 35 must be isolated from PC7 by SJ1')
    exposed={net for item in components if item.ref=='J1' or item.ref=='SJ1' or item.ref.startswith('TP')
             for net in item.nets.values() if net is not None}
    if set(c['U1'].nets.values())-exposed:
        raise ValueError('Every MCU net must have header, jumper or probe access')
    require('SW1',{1:'PA21',2:'GND'})
    require('SW2',{1:'BOOT_PULLUP',2:'3V3_OUT'})
    require('R12',{1:'USB_DP',2:'BOOT_PULLUP'})
    for net in ('VBUS','PD_OUT','VIN_SYS','VSYS'):
        if net in c['U1'].nets.values():raise ValueError('High-voltage net connected directly to MCU')
    shutdown_nodes={(x.ref,p) for x in components for p,n in x.nets.items() if n=='3V3_EN'}
    if shutdown_nodes!={('J1','37'),('U4','2')}:
        raise ValueError('3V3_EN must connect only header 37 and regulator EN, with no VIN pull-up')
    enable_nodes={(x.ref,p) for x in components for p,n in x.nets.items() if n=='PD_ENABLE'}
    if enable_nodes!={('U1','22'),('U3','1'),('R7','1'),('TP21','1')}:
        raise ValueError('PD_ENABLE must carry control only')
    for ref in ('C1','C5','C8','C12'):
        if c[ref].part not in {'C13585','C1525'}:raise ValueError('High-voltage capacitor rating changed')
    # Reject accidental direct bypasses of the switch or VSYS isolation diode.
    for x in components:
        nets=set(x.nets.values())
        if {'VBUS','PD_OUT'}<=nets and x.ref!='U3':raise ValueError('Bypassed PD load switch')
        if 'VSYS' in nets and nets & {'VBUS','PD_OUT'} and x.ref!='J1':
            raise ValueError('HV backfeed to VSYS')


def verify_netlist(path,components=COMPONENTS):
    tree=ET.parse(path)
    expected={c.ref:c for c in components if not c.ref.startswith('#')}
    actual_refs={e.attrib['ref'] for e in tree.findall('./components/comp')}
    if actual_refs!=set(expected):
        raise ValueError(f'Component mismatch: {actual_refs ^ set(expected)}')
    observed={}
    for net in tree.findall('./nets/net'):
        nodes=net.findall('node')
        for node in nodes:
            key=node.attrib['ref'],node.attrib['pin']
            if key in observed: raise ValueError(f'Pin occurs on multiple nets: {key}')
            name=net.attrib['name']
            if 'no_connect' in node.attrib.get('pintype',''):
                if len(nodes)!=1 or not name.startswith('unconnected-'):
                    raise ValueError(f'NC pin has other connections: {key}')
                name=None
            observed[key]=name
    source={(c.ref,pin):net for c in expected.values() for pin,net in c.nets.items()}
    if set(source)!=set(observed):
        raise ValueError(f'Pin coverage mismatch: {set(source)^set(observed)}')
    differences=[(key,net,observed[key]) for key,net in source.items() if observed[key]!=net]
    if differences: raise ValueError(f'Netlist differs from source: {differences}')
    return {'components':len(expected),'pins':len(source),
            'connected_nets':len({n for n in source.values() if n is not None}),
            'explicit_nc_pins':sum(n is None for n in source.values()),'netlist_parity':True}


def main():
    verify_contract()
    report=verify_netlist(ROOT/'build/ch32-pico.net.xml')
    (ROOT/'build/electrical-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__': main()
