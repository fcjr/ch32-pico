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
    require('D1',{1:'VSYS',2:'VBUS'})
    from .lowcost import verify
    verify(components)
    require('R1',{1:'VSYS',2:'3V3_EN'})
    require('Q1',{1:'VBUS',2:'GND',3:'VBUS_N'})
    require('R3',{1:'CC1',2:'GND'})
    require('R4',{1:'CC2',2:'GND'})
    require('J2',{'A5':'CC1','B5':'CC2','A6':'USB_DP','B6':'USB_DP','A7':'USB_DM','B7':'USB_DM'})
    for p in HEADER:
        require('J1',{p.number:None if p.proposed=='NC' else p.proposed})
        if p.proposed in TARGET_PINS: require('U1',{TARGET_PINS[p.proposed]:p.proposed})
    require('R15',{1:'PROBE_SWIO',2:'PD1'})
    require('R16',{1:'PD1',2:'TARGET_3V3'})
    require('R5',{1:'USB_DP',2:'PROBE_DP'})
    require('R6',{1:'USB_DM',2:'PROBE_DM'})
    # Removing an interface resistor must isolate the two nets. A hidden
    # parallel jumper or copied short would defeat the documented controls.
    for ref,pair in {'R15':{'PROBE_SWIO','PD1'}}.items():
        for other in components:
            if other.ref!=ref and pair.issubset(set(other.nets.values())):
                raise ValueError(f'{other.ref} bypasses interface isolation {ref}')


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
