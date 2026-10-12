# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Functional silkscreen labels and an audit against actual PCB pads and nets."""
import json
import math
from .circuit import COMPONENTS
from .design import HEADER, MECHANICAL, BOARD_REVISION, TARGET_PINS
from .placement import PLACEMENT
from .schematic import uid
from .sexp import parse, children, one, dump
from .usb_review import pad_centers

# ref, legend, net at pin 1, offset from the component center, purpose.
# Service controls and pads are accessible on the front only.
SERVICES = (
    ('TP1', 'SDIO', 'SDIO', (0,1.4), 'U1 PC18 / two-wire SDI data'),
    ('TP2', 'SDCK', 'SDCK', (0,1.4), 'U1 PC19 / two-wire SDI clock'),
    ('TP3', '3V3', '3V3_OUT', (0,1.4), 'Fixed 3.3 V measurement'),
    ('TP4', 'GND', 'GND', (0,1.4), 'Common ground'),
    ('TP5', 'RST', 'PA21', (0,1.4), 'U1 PA21 reset'),
    ('SW1', 'RESET', 'PA21', (0,1.9), 'X035 reset'),
    ('SW2', 'BOOT', 'BOOT_PULLUP', (0,1.9), 'Hold at power-up for USB ISP'),
    ('D3', 'LED', 'LED_A', (0,1.2), 'PB3 application status LED'),
)

ALIASES = {'NC':'NC', '3V3_OUT':'3V3', '3V3_EN':'EN', 'PA21':'RST', 'PD_OUT':'PDOUT'}
LEGACY = {'PROBE SWIO', 'PROBE', 'RESET', 'DBG', 'SWIO'}


def header_legend(pin):
    label = ALIASES.get(pin.proposed, pin.proposed)
    return f'{pin.number}\n{label}' if pin.number in (1,20,21,40) else label


def text(label, x, y, side, identity):
    mirror = '(justify mirror)' if side == 'B.SilkS' else ''
    return parse(f'''(gr_text {json.dumps(label)} (at {x} {y}) (layer "{side}")
        (uuid "{uid('marking/' + identity)}")
        (effects (font (size .8 .8) (thickness .12)) {mirror}))''')


def apply(doc):
    header_labels = {p.proposed for p in HEADER} | set(ALIASES.values()) | {'-', '3V3', 'EN'} | {f'{p.number} {ALIASES.get(p.proposed,p.proposed)}' for p in HEADER if p.number in (1,20,21,40)}
    header_labels |= {header_legend(p) for p in HEADER}
    service_labels = LEGACY | {s[1] for s in SERVICES}
    doc[:] = [n for n in doc if not (isinstance(n,list) and n and n[0]=='gr_text' and
        (n[1] in service_labels or (one(n,'layer')[1]=='B.SilkS' and n[1] in header_labels)))]
    for pin in HEADER:
        _, y = MECHANICAL.position(pin.number)
        x = 3.9 if pin.number<=20 else 17.1
        x = {1:7.7,20:7.7,21:13.1,40:13.1}.get(pin.number,x)
        doc.append(text(header_legend(pin),x,y,'B.SilkS',f'header/{pin.number}'))
    for ref,label,net,(dx,dy),purpose in SERVICES:
        x,y,*_ = PLACEMENT[ref]
        doc.append(text(label,round(x+dx,4),round(y+dy,4),'F.SilkS',ref))


def update(path):
    doc = parse(path.read_text()); apply(doc); path.write_text(dump(doc)+'\n')


def audit(doc):
    """Reject wrong functions, sides, mirrored orientation and ambiguous pad associations.

    KiCad DRC separately checks mask/hole/text clearance. Visual review checks
    the populated model for component-body obstruction and practical readability.
    """
    fps = {next(p[2] for p in children(fp,'property') if p[1]=='Reference'):fp
           for fp in children(doc,'footprint')}
    circuit = {c.ref:c for c in COMPONENTS}
    pads = pad_centers(doc)
    texts = children(doc,'gr_text')
    front = [n for n in texts if one(n,'layer')[1]=='F.SilkS']
    back = [n for n in texts if one(n,'layer')[1]=='B.SilkS']
    if len(back)!=40: raise ValueError('Back must contain exactly 40 header labels; services belong on front')
    for n in front+back:
        effects=one(n,'effects'); font=one(effects,'font')
        mirrored=any('mirror' in j[1:] for j in children(effects,'justify'))
        if mirrored != (one(n,'layer')[1]=='B.SilkS'):
            raise ValueError(f'Wrong text mirroring: {n[1]}')
        if 'hide' in n or 'hide' in effects:
            raise ValueError(f'Hidden marking: {n[1]}')
        if min(map(float,one(font,'size')[1:]))<.8 or float(one(font,'thickness')[1])<.1:
            raise ValueError(f'Undersized marking: {n[1]}')
    allowed={s[1] for s in SERVICES}|{'ch32-pico','LEFT SHIFT','LOGICAL',f'REV {BOARD_REVISION}', 'PDOUT 5-20V'}
    if any(n[1] not in allowed for n in front):raise ValueError('Unknown front legend')
    header=[]
    for pin in HEADER:
        px,py=pads['J1',str(pin.number)]
        # Match by row and physical side, independently of text UUIDs.
        matched=[n for n in back if abs(float(one(n,'at')[2])-py)<.01 and
                 ((float(one(n,'at')[1])<MECHANICAL.width/2)==(px<MECHANICAL.width/2))]
        if len(matched)!=1 or matched[0][1]!=header_legend(pin):
            raise ValueError(f'Incorrect header label at pin {pin.number}')
        expected=None if pin.proposed=='NC' else pin.proposed
        lands=[p for p in children(fps['J1'],'pad') if p[1]==str(pin.number)]
        for pad in lands:
            actual=one(pad,'net')[-1] if children(pad,'net') else None
            if actual!=expected: raise ValueError(f'Header label/net mismatch at pin {pin.number}')
        if expected in TARGET_PINS:
            mcu_pin=str(TARGET_PINS[expected])
            mcu_pad=next(p for p in children(fps['U1'],'pad') if p[1]==mcu_pin)
            if one(mcu_pad,'net')[-1]!=expected:
                raise ValueError(f'Header label/MCU mismatch at pin {pin.number}: U1.{mcu_pin}')
        header.append({'pin':pin.number,'label':matched[0][1],'net':expected,'side':'back',
                       'pad_xy_mm':[px,py]})
    service=[]
    for ref,label,net,offset,purpose in SERVICES:
        matched=[n for n in front if n[1]==label]
        if len(matched)!=1:raise ValueError(f'Missing/duplicate front label for {ref}: {label}')
        n=matched[0];x,y=map(float,one(n,'at')[1:3])
        fp=fps[ref];pad=next(p for p in children(fp,'pad') if p[1]=='1')
        if one(fp,'layer')[1]!='F.Cu' or 'F.Mask' not in one(pad,'layers')[1:]:
            raise ValueError(f'{ref} is not accessible on front')
        if one(pad,'net')[-1]!=net or circuit[ref].nets['1']!=net:
            raise ValueError(f'{ref} label/net mismatch: {label}')
        cx,cy=map(float,one(fp,'at')[1:3])
        if math.dist((x,y),(cx,cy))>3:raise ValueError(f'Label too far from {ref}')
        if ref.startswith('TP'):
            nearest=min((r for r in fps if r.startswith('TP')),
                        key=lambda r:math.dist((x,y),pads[r,'1']))
            if nearest!=ref:raise ValueError(f'{label} is nearer {nearest} than {ref}')
        service.append({'ref':ref,'label':label,'net':net,'purpose':purpose,'side':'front',
                        'pad_xy_mm':list(pads[ref,'1']),'text_xy_mm':[x,y]})
    # Follow the named controls to actual MCU package pins and the LED resistor.
    endpoints = {('U1','34'):'SDIO',('U1','37'):'SDCK',('U1','7'):'PA21',
                 ('U1','48'):'3V3_OUT',('U1','47'):'GND',('SW1','2'):'GND',
                 ('U1','23'):'STATUS_LED',('R11','1'):'STATUS_LED',
                 ('R11','2'):'LED_A',('D3','2'):'GND',('U3','6'):'PD_OUT'}
    for (ref,pin),net in endpoints.items():
        pad=next(p for p in children(fps[ref],'pad') if p[1]==pin)
        if one(pad,'net')[-1]!=net:raise ValueError(f'Wrong marked-function endpoint: {ref}.{pin}')
    # Verify the reset and application LED beyond their pad-1 nets.
    if circuit['SW1'].nets != {'1':'PA21','2':'GND'} or circuit['D3'].nets != {'1':'LED_A','2':'GND'}:
        raise ValueError('Reset/LED function changed')
    if any(n[1] in {'PROBE SWIO','PROBE','DBG','SWIO'} for n in texts):
        raise ValueError('Ambiguous legacy service legend remains')
    return {'header_labels':header,'service_labels':service,'header_count':len(header),
            'front_service_count':len(service),'all_markings_verified':True,
            'coordinate_convention':'PCB coordinates, X right/Y down in front view; back text mirrored'}
