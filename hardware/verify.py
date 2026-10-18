# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Independent KiCad XML-netlist comparison and circuit contract checks."""
from collections import defaultdict
from pathlib import Path
import json
import re
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
    if c['U1'].part != MCU_PART:
        raise ValueError('U1 must be the reviewed CH32X035C8T6')
    require('U1',{47:'GND',48:'3V3_OUT',7:'PA21',32:'USB_DM',33:'USB_DP',
                  34:'SDIO',37:'SDCK',38:'CC1',39:'CC2'})
    require('D1',{1:'VIN_SYS',2:'VBUS'})
    require('D4',{1:'VIN_SYS',2:'VSYS'})
    require('D2',{2:'GND',5:'3V3_OUT'})
    require('U4',{1:'3V3_OUT',2:'3V3_EN',3:'VIN_SYS',4:'GND',5:'BUCK_SW',6:'BUCK_BST'})
    require('L1',{1:'BUCK_SW',2:'3V3_OUT'})
    # Pin 40 is direct VBUS. The input clamp is the only part on the PD path.
    if c['D5'].part!='C523793':raise ValueError('D5: unreviewed TVS clamp')
    require('D5',{1:'GND',2:'GND',3:'GND',4:'VBUS',5:'VBUS',6:'VBUS',7:'GND'})
    require('R1',{1:'VBUS',2:'VBUS_SENSE'});require('R2',{1:'VBUS_SENSE',2:'GND'})
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
    require('U1',{19:'PC7',24:'PB4'})
    pc7_nodes={(x.ref,p) for x in components for p,n in x.nets.items() if n=='PC7'}
    if pc7_nodes!={('U1','19'),('SJ1','2')}:
        raise ValueError('PC7 must connect only MCU and SJ1; TP7 is PB4')
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
    for net in ('VBUS','VIN_SYS','VSYS'):
        if net in c['U1'].nets.values():raise ValueError('High-voltage net connected directly to MCU')
    shutdown_nodes={(x.ref,p) for x in components for p,n in x.nets.items() if n=='3V3_EN'}
    if shutdown_nodes!={('J1','37'),('U4','2')}:
        raise ValueError('3V3_EN must connect only header 37 and regulator EN, with no VIN pull-up')
    if [p.proposed for p in HEADER if p.number==40]!=['VBUS']:
        raise ValueError('Header pin 40 must be direct USB VBUS')
    rating=library[c['C1'].part].voltage_rating_v
    if rating is None or rating<50:
        raise ValueError('C1: high-voltage capacitor requires a verified 50 V part')
    for item in components:
        if item.ref.startswith('C'):
            label=re.search(r'/\s*(\d+(?:\.\d+)?)V\b',item.value)
            if label and float(label[1])!=library[item.part].voltage_rating_v:
                raise ValueError(f'{item.ref}: capacitor value label differs from vendor voltage rating')
    # Reject accidental direct bypasses of the VSYS isolation diode.
    for x in components:
        nets=set(x.nets.values())
        if 'VSYS' in nets and 'VBUS' in nets and x.ref!='J1':
            raise ValueError('HV backfeed to VSYS')


def verify_netlist(path,components=COMPONENTS):
    tree=ET.parse(path)
    expected={c.ref:c for c in components if not c.ref.startswith('#')}
    actual_refs={e.attrib['ref'] for e in tree.findall('./components/comp')}
    if actual_refs!=set(expected):
        raise ValueError(f'Component mismatch: {actual_refs ^ set(expected)}')
    library=load_library()
    for node in tree.findall('./components/comp'):
        item=expected[node.attrib['ref']]
        fields={f.attrib['name']:f.text or '' for f in node.findall('./fields/field')}
        part=library[item.part]
        if (node.findtext('value'),fields.get('LCSC',''),fields.get('MPN'))!=(item.value or part.mpn,part.code,part.mpn):
            raise ValueError(f'{item.ref}: netlist part/value differs from source')
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
