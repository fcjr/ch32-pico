# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Functional silkscreen labels and an audit against actual PCB pads and nets."""
import json
import math
from .circuit import COMPONENTS
from .diagnostics import DIAGNOSTICS, LEADERS
from .design import HEADER, MECHANICAL, BOARD_REVISION, TARGET_PINS, EXPANSION_SIGNALS
from .placement import PLACEMENT
from .schematic import uid
from .sexp import parse, children, one, dump, Atom
from .usb_review import pad_centers

# ref, legend, net at pin 1, offset from the component center, purpose.
# Service controls and pads are accessible on the front only.
SERVICES = (
    ('TP1', 'SDIO', 'SDIO', (-.3,1.4), 'U1 PC18 / two-wire SDI data'),
    ('TP2', 'SDCK', 'SDCK', (0,1.4), 'U1 PC19 / two-wire SDI clock'),
    ('TP3', '3V3', '3V3_OUT', (.3,1.4), 'Fixed 3.3 V measurement'),
    ('TP4', 'GND', 'GND', (-.8,-1.5), 'Common ground'),
    ('TP5', 'RST', 'PA21', (0,-1.2), 'U1 PA21 reset'),
    ('SW1', 'RESET', 'PA21', (0,-2), 'X035 reset'),
    ('SW2', 'BOOT', 'BOOT_PULLUP', (0,-2), 'Hold at power-up for USB ISP'),
    ('D3', 'LED', 'LED_A', (0,-1.3), 'PB3 application status LED'),
)

ALIASES = {'NC':'NC', '3V3_OUT':'3V3', '3V3_EN':'EN', 'PA21':'RST', 'PD_OUT':'PDOUT', 'GPIO35':'PC7*', 'PD_FAULT_N':'FAULT'}
LEGACY = {'PROBE SWIO', 'PROBE', 'RESET', 'DBG', 'SWIO'}
EXPANSIONS = tuple((f'TP{i}', n) for i,n in enumerate((*EXPANSION_SIGNALS,'GND'),6))


def header_legend(pin):
    label = ALIASES.get(pin.proposed, pin.proposed)
    if pin.number in (1,20,21,40):
        return f'{pin.number} {label}'
    return label


def header_label_position(pin):
    _, y = MECHANICAL.position(pin.number)
    x = 4.4 if pin.number <= 20 else 16.6
    # Two numbered rows fit between the USB shell stakes at the top end.
    if pin.number == 1:
        return 10, y
    if pin.number == 40:
        return 10.5, 3.15
    return {3:3.9,20:6.5,21:13.8,38:17.1}.get(pin.number,x), y


def text(label, x, y, side, identity, size=.9):
    mirror = '(justify mirror)' if side == 'B.SilkS' else ''
    return parse(f'''(gr_text {json.dumps(label)} (at {x} {y}) (layer "{side}")
        (uuid "{uid('marking/' + identity)}")
        (effects (font (size {size} {size}) (thickness .15)) {mirror}))''')


def apply(doc):
    header_labels = {p.proposed for p in HEADER} | set(ALIASES.values()) | {'-', '3V3', 'EN'} | {f'{p.number} {ALIASES.get(p.proposed,p.proposed)}' for p in HEADER if p.number in (1,20,21,40)}
    header_labels |= {header_legend(p) for p in HEADER}
    header_labels |= {'1\nPB10', '20\nPA22', '21\nPA6', '40\nPDOUT'}
    service_labels = LEGACY | {s[1] for s in SERVICES} | set(EXPANSION_SIGNALS) | {'SJ1','PC7','FAULT'} | {d.label for d in DIAGNOSTICS}
    doc[:] = [n for n in doc if not (isinstance(n,list) and n and n[0]=='gr_text' and
        (n[1] in service_labels or (one(n,'layer')[1]=='B.SilkS' and n[1] in header_labels)))]
    leader_ids={uid('marking/leader/'+ref) for ref in LEADERS}
    doc[:]=[n for n in doc if not (isinstance(n,list) and n and n[0]=='gr_line'
            and children(n,'uuid') and one(n,'uuid')[1] in leader_ids)]
    for ref,(a,b) in LEADERS.items():
        doc.append(parse(f'''(gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]})
            (stroke (width .15) (type solid)) (layer "B.SilkS")
            (uuid "{uid('marking/leader/'+ref)}"))'''))
    for pin in HEADER:
        x,y = header_label_position(pin)
        doc.append(text(header_legend(pin),x,y,'B.SilkS',f'header/{pin.number}'))
    for ref,label,net,(dx,dy),purpose in SERVICES:
        x,y,*_ = PLACEMENT[ref]
        doc.append(text(label,round(x+dx,4),round(y+dy,4),'F.SilkS',ref,
                         size=.8 if ref in {'TP1','TP2','TP3'} else .9))
    for ref,net in EXPANSIONS:
        x,y,*_ = PLACEMENT[ref]
        tx,ty=(13.7,31.1) if ref=='TP6' else (x,y+1.15)
        doc.append(text(ALIASES.get(net,net),tx,ty,'B.SilkS',ref,size=.8))
    for d in DIAGNOSTICS:
        doc.append(text(d.label,*d.text_position,d.side+'.SilkS',d.ref,size=.8))
    x,y,*_ = PLACEMENT['SJ1']
    doc.append(text('SJ1',x,y-1.45,'B.SilkS','SJ1'))


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
    from .branding import artwork
    brand_count=sum(n[0]=='gr_text' and one(n,'layer')[1]=='B.SilkS' for n in artwork())
    if len(back)!=41+brand_count+len(EXPANSIONS)+sum(d.side=='B' for d in DIAGNOSTICS):
        raise ValueError('Back must contain 40 header, 8 expansion, diagnostic, jumper and current branding labels; services belong on front')
    for n in front+back:
        effects=one(n,'effects'); font=one(effects,'font')
        mirrored=any('mirror' in j[1:] for j in children(effects,'justify'))
        if mirrored != (one(n,'layer')[1]=='B.SilkS'):
            raise ValueError(f'Wrong text mirroring: {n[1]}')
        if 'hide' in n or 'hide' in effects:
            raise ValueError(f'Hidden marking: {n[1]}')
        minimum=.8
        # 0.8 mm type / 0.15 mm strokes are the smallest reviewed service
        # legends; the main header labels use 0.9 mm type.
        if min(map(float,one(font,'size')[1:]))<minimum or float(one(font,'thickness')[1])<.15:
            raise ValueError(f'Undersized marking: {n[1]}')
    allowed={s[1] for s in SERVICES}|{'ch32-pico','LEFT SHIFT','LOGICAL',f'REV {BOARD_REVISION}', 'PDOUT 5-20V'}
    allowed |= {d.label for d in DIAGNOSTICS if d.side=='F'}
    if any(n[1] not in allowed for n in front):raise ValueError('Unknown front legend')
    header=[]
    for pin in HEADER:
        px,py=pads['J1',str(pin.number)]
        # Match the specified physical label position, not merely a shared
        # row: diagnostic contacts now occupy some of the same Y coordinates.
        label_xy=header_label_position(pin)
        matched=[n for n in back if math.dist(tuple(map(float,one(n,'at')[1:3])),label_xy)<.01]
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
        if math.dist((x,y),(cx,cy))>(4 if ref.startswith('SW') else 3):raise ValueError(f'Label too far from {ref}')
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
                 ('R11','2'):'LED_A',('D3','2'):'GND',('U3','17'):'PD_OUT',('U3','14'):'PD_FAULT_N',('U1','24'):'PD_FAULT_N',
                 ('R9','1'):'PD_FAULT_N',('R9','2'):'3V3_OUT',('U1','19'):'PC7'}
    for (ref,pin),net in endpoints.items():
        pad=next(p for p in children(fps[ref],'pad') if p[1]==pin)
        if one(pad,'net')[-1]!=net:raise ValueError(f'Wrong marked-function endpoint: {ref}.{pin}')
    # Verify the reset and application LED beyond their pad-1 nets.
    if circuit['SW1'].nets != {'1':'PA21','2':'GND'} or circuit['D3'].nets != {'1':'LED_A','2':'GND'}:
        raise ValueError('Reset/LED function changed')
    if any(n[1] in {'PROBE SWIO','PROBE','DBG','SWIO'} for n in texts):
        raise ValueError('Ambiguous legacy service legend remains')
    expansion=[]
    for ref,net in EXPANSIONS:
        fp=fps[ref];pad=one(fp,'pad');x,y=pads[ref,'1']
        label_xy=(13.7,31.1) if ref=='TP6' else (x,y+1.15)
        labels=[n for n in back if n[1]==ALIASES.get(net,net) and
                math.dist(tuple(map(float,one(n,'at')[1:3])),label_xy)<.01]
        if len(labels)!=1 or one(fp,'layer')[1]!='B.Cu' or 'B.Mask' not in one(pad,'layers')[1:]:
            raise ValueError(f'Incorrect back expansion label/pad: {ref}')
        if one(pad,'net')[-1]!=net:raise ValueError(f'Expansion net mismatch: {ref}')
        if net in TARGET_PINS:
            mp=next(p for p in children(fps['U1'],'pad') if p[1]==str(TARGET_PINS[net]))
            if one(mp,'net')[-1]!=net:raise ValueError(f'Expansion MCU mismatch: {ref}')
        expansion.append({'ref':ref,'net':net,'side':'back','pad_xy_mm':[x,y]})
    diagnostic=[]
    for d in DIAGNOSTICS:
        fp=fps[d.ref];pad=one(fp,'pad')
        labels=[n for n in texts if n[1]==d.label and one(n,'layer')[1]==d.side+'.SilkS'
                and math.dist(tuple(map(float,one(n,'at')[1:3])),d.text_position)<.01]
        if len(labels)!=1 or one(fp,'layer')[1]!=d.side+'.Cu':
            raise ValueError(f'Incorrect diagnostic label/side: {d.ref}')
        if one(pad,'net')[-1]!=d.net or circuit[d.ref].nets['1']!=d.net:
            raise ValueError(f'Diagnostic label/net mismatch: {d.ref}')
        if set(one(pad,'layers')[1:])!={d.side+'.Cu',d.side+'.Mask'}:
            raise ValueError(f'Diagnostic pad must have no paste: {d.ref}')
        if math.dist(pads[d.ref,'1'],d.position)>.001:
            raise ValueError(f'Diagnostic pad position mismatch: {d.ref}')
        if d.ref in LEADERS:
            lines=[n for n in children(doc,'gr_line') if children(n,'uuid')
                   and one(n,'uuid')[1]==uid('marking/leader/'+d.ref)]
            a,b=LEADERS[d.ref]
            if (len(lines)!=1 or one(lines[0],'layer')[1]!=d.side+'.SilkS'
                or tuple(map(float,one(lines[0],'start')[1:]))!=a
                or tuple(map(float,one(lines[0],'end')[1:]))!=b):
                raise ValueError(f'Diagnostic leader missing or displaced: {d.ref}')
            anchor=b
        else:anchor=d.text_position
        same_side=[p for p in DIAGNOSTICS if p.side==d.side]
        nearest=min(same_side,key=lambda p:math.dist(anchor,p.position))
        if nearest.ref!=d.ref:raise ValueError(f'Ambiguous diagnostic label: {d.ref}')
        diagnostic.append({'ref':d.ref,'label':d.label,'net':d.net,'side':d.side,
                           'pad_xy_mm':list(d.position),'text_xy_mm':list(d.text_position)})
    sj=fps['SJ1'];x,y,*_=map(float,one(sj,'at')[1:])
    labels=[n for n in back if n[1]=='SJ1' and
            math.dist(tuple(map(float,one(n,'at')[1:3])),(x,y-1.45))<.01]
    if len(labels)!=1 or one(sj,'layer')[1]!='B.Cu':
        raise ValueError('SJ1 label must identify the back-side solder jumper')
    for number,net in (('1','GPIO35'),('2','PC7')):
        pad=next(p for p in children(sj,'pad') if p[1]==number)
        if one(pad,'net')[-1]!=net or set(one(pad,'layers')[1:])!={'B.Cu','B.Mask'}:
            raise ValueError('SJ1 must expose separate header/PC7 pads with no paste')
    return {'header_labels':header,'service_labels':service,'expansion_labels':expansion,'header_count':len(header),'diagnostic_labels':diagnostic,
            'jumper':{'ref':'SJ1','side':'back','default':'open','header_pin':35,'optional_gpio':'PC7'},
            'front_service_count':len(service),'all_markings_verified':True,
            'coordinate_convention':'PCB coordinates, X right/Y down in front view; back text mirrored'}
