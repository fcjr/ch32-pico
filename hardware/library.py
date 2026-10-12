# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Read exact procurement metadata; assign reviewed electrical pin types.

EasyEDA geometry is a local input, never authoritative for electrical rules.
The schematic generator draws compact symbols from this typed pin model.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from .sexp import parse, children, one
from .design import HEADER, TARGET_PINS

ROOT = Path(__file__).resolve().parents[1]
LIBDIR = ROOT / 'hardware/lib'


@dataclass(frozen=True)
class Pin:
    number: str
    name: str
    electrical: str = 'passive'


@dataclass(frozen=True)
class Part:
    code: str
    mpn: str
    manufacturer: str
    footprint: str
    pins: tuple[Pin, ...]


def pin_sort(pin):
    return (0,int(pin.number)) if pin.number.isdecimal() else (1,pin.number)


def load_library():
    library = {}
    for s in children(parse((LIBDIR/'ch32-pico.kicad_sym').read_text()),'symbol'):
        props={p[1]:p[2] for p in children(s,'property')}
        code=props['LCSC Part']
        pins=[]
        for sub in children(s,'symbol'):
            for p in children(sub,'pin'):
                number=one(p,'number')[1]
                name=one(p,'name')[1]
                electrical='passive'
                if code=='C5187096':
                    name=next(k for k,v in TARGET_PINS.items() if str(v)==number)
                    electrical='power_in' if number in {'7','9'} else 'input' if number=='4' else 'bidirectional'
                elif code=='C82942':
                    electrical={'1':'power_in','2':'power_in','3':'input',
                                '4':'passive','5':'power_out'}[number]
                elif code=='C15999':
                    name={'1':'IO1','2':'GND','3':'IO2','4':'IO2','5':'VBUS','6':'IO1'}[number]
                    electrical='power_in' if number in {'2','5'} else 'passive'
                pins.append(Pin(number,name,electrical))
        pins=tuple(sorted(pins,key=pin_sort))
        if len(pins)!=len({p.number for p in pins}):
            raise ValueError(f'Duplicate symbol pins: {code}')
        library[code]=Part(code,props['MPN'],props.get('Manufacturer',''),props['Footprint'].split(':')[-1],pins)
    library['PICO_HEADER']=Part('','Pico header pads','','Pico_Header',
        tuple(Pin(str(p.number),p.pico.split(' / ')[0]) for p in HEADER))
    library['TESTPAD']=Part('','Test pad','','TestPad_1mm',(Pin('1','TP'),))
    library['POWER_FLAG']=Part('','PWR_FLAG','','',(Pin('1','pwr','power_out'),))
    return library


def validate_library(components, library):
    refs=set()
    for c in components:
        if c.ref in refs: raise ValueError(f'Duplicate reference {c.ref}')
        refs.add(c.ref)
        part=library[c.part]
        actual=set(c.nets)
        expected={p.number for p in part.pins}
        if actual!=expected:
            raise ValueError(f'{c.ref}: missing pins {expected-actual}, extra pins {actual-expected}')
        if c.fitted and not part.code.startswith('C'):
            raise ValueError(f'{c.ref}: fitted component without LCSC identifier')
        if part.code:
            fp=parse((LIBDIR/'ch32-pico.pretty'/f'{part.footprint}.kicad_mod').read_text())
            pads={p[1] for p in children(fp,'pad') if p[1]}
            if pads!=expected:
                raise ValueError(f'{c.ref}: footprint pads differ from symbol pins: {pads ^ expected}')
        for pin in part.pins:
            if pin.electrical=='unspecified': raise ValueError(f'{c.ref}.{pin.number} unspecified type')
            if pin.electrical in {'power_in','power_out'} and c.nets[pin.number] is None:
                raise ValueError(f'{c.ref}.{pin.number} supply pin left NC')
