# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Deterministic hierarchical KiCad schematic from the typed circuit model.

Short wires join each pin to an explicit global label. There is no proximity
wiring and no ERC suppression. Exported netlist parity is a separate check.
"""
import json
from .design import BOARD_REVISION
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
from .circuit import COMPONENTS, SECTIONS
from .library import load_library, validate_library

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build'
PROJECT = 'ch32-pico'


def uid(name): return str(uuid5(NAMESPACE_URL, 'ch32-pico/electrical/'+name))
def q(text): return json.dumps(str(text))
def n(value): return f'{value:.4f}'.rstrip('0').rstrip('.')
def snap(value): return round(round(value/1.27)*1.27,4)


def geometry(part):
    pins=part.pins
    if len(pins)<=2:
        return 2.54,2.54,{p.number:((-5.08 if i==0 else 5.08),0,0 if i==0 else 180)
                          for i,p in enumerate(pins)}
    half=(len(pins)+1)//2
    height=max(5.08,half*2.54)
    coords={}
    for i,p in enumerate(pins[:half]): coords[p.number]=(-17.78,height/2-1.27-i*2.54,0)
    for i,p in enumerate(reversed(pins[half:])): coords[p.number]=(17.78,height/2-1.27-i*2.54,180)
    return 15.24,height/2,coords


def symbol(code,part, qualified=False):
    name=f'ch32-pico:{code}' if qualified else code
    w,h,coords=geometry(part)
    ref='U' if code.startswith('C') else '#FLG' if code=='POWER_FLAG' else 'J'
    small=len(part.pins)<=2
    pin_display='(pin_numbers hide) (pin_names hide)' if small else '(pin_names (offset 0.635))'
    stroke='(stroke (width 0.254) (type default))'
    def line(points):
        return '(polyline (pts '+ ' '.join(f'(xy {px} {py})' for px,py in points)+') '+stroke+' (fill (type none)))'
    pin_length=2.54
    if part.footprint.startswith('C0'):
        drawing=line([(-0.635,-2.54),(-0.635,2.54)])+line([(0.635,-2.54),(0.635,2.54)])
        pin_length=4.445
    elif part.footprint.startswith('SW-'):
        drawing=line([(-2.54,0),(1.8,2.0)])
        for px in (-2.54,2.54):
            drawing+=f'(circle (center {px} 0) (radius 0.35) {stroke} (fill (type none)))'
    elif part.footprint.startswith(('SOD-','LED-')):
        direction=1 if part.footprint.startswith('LED-') else -1
        drawing=line([(-2.54,0),(-1.27,0)])+line([(1.27,0),(2.54,0)])
        drawing+=line([(-1.27*direction,-1.27),(-1.27*direction,1.27),(1.27*direction,0),(-1.27*direction,-1.27)])
        drawing+=line([(1.27*direction,-1.27),(1.27*direction,1.27)])
        if direction==1:
            drawing+=line([(0,2),(1.5,3.5)])+line([(1,2),(2.5,3.5)])
    elif part.footprint.startswith('IND-'):
        drawing=''.join(f'(arc (start {px} 0) (mid {px+0.635} 0.635) (end {px+1.27} 0) {stroke} (fill (type none)))'
                        for px in (-2.54,-1.27,0,1.27))
    elif code == 'SOLDER_JUMPER':
        drawing=line([(-2.54,0),(-0.8,0)])+line([(0.8,0),(2.54,0)])
        for px in (-0.8,0.8):
            drawing+=f'(circle (center {px} 0) (radius 0.3) {stroke} (fill (type none)))'
    elif code in ('POWER_FLAG','TESTPAD','USB_PROBE','SMALL_PROBE'):
        drawing=f'(circle (center 0 0) (radius 1) {stroke} (fill (type none)))'+line([(-2.54,0),(-1,0)])
    else:
        box_h=1.016 if small else h
        drawing=f'(rectangle (start {-w} {n(box_h)}) (end {w} {n(-box_h)}) {stroke} (fill (type background)))'
    body=[f'(symbol {q(name)} {pin_display} (in_bom yes) (on_board yes)',
          f'(property "Reference" {q(ref)} (at 0 {n(h+3.81)} 0) (effects (font (size 1.27 1.27))))',
          f'(property "Value" {q(part.mpn)} (at 0 {n(h+1.27)} 0) (effects (font (size 1.27 1.27))))',
          f'(symbol {q(code+"_0_1")} {drawing})',
          f'(symbol {q(code+"_1_1")}']
    for p in part.pins:
        x,y,angle=coords[p.number]
        body.append(f'(pin {p.electrical} line (at {n(x)} {n(y)} {angle}) (length {pin_length}) '
            f'(name {q(p.name)} (effects (font (size 0.9 0.9)))) '
            f'(number {q(p.number)} (effects (font (size 0.9 0.9)))))')
    return '\n'.join(body)+'))'


def text(value,x,y,size=1.27):
    return f'(text {q(value)} (at {n(x)} {n(y)} 0) (effects (font (size {size} {size})) (justify left)) (uuid {q(uid("text/"+value))}))'


def instance(c,part,x,y,path):
    w,h,coords=geometry(part)
    is_flag=c.part=='POWER_FLAG'
    lines=[f'(symbol (lib_id {q("ch32-pico:"+c.part)}) (at {n(x)} {n(y)} 0) (unit 1)',
           f'(exclude_from_sim no) (in_bom {"yes" if c.fitted else "no"}) (on_board {"no" if is_flag else "yes"}) (dnp no)',
           f'(uuid {q(uid("component/"+c.ref))})']
    fields={'Reference':c.ref,'Value':c.value or part.mpn,'Footprint':('ch32-pico:'+part.footprint) if part.footprint else '',
            'LCSC':part.code,'MPN':part.mpn,'Manufacturer':part.manufacturer,'Design note':c.note}
    for i,(key,value) in enumerate(fields.items()):
        hide='' if i<2 else ' (hide yes)'
        yy=y-h-6.35+i*2.54 if i<2 else y
        lines.append(f'(property {q(key)} {q(value)} (at {n(x)} {n(yy)} 0) (effects (font (size 1.1 1.1)){hide}))')
    lines.append(f'(instances (project {q(PROJECT)} (path {q(path)} (reference {q(c.ref)}) (unit 1)))))')
    for p in part.pins:
        px,py,angle=coords[p.number]
        ax,ay=round(x+px,4),round(y-py,4)
        net=c.nets[p.number]
        identity=f'{c.ref}/{p.number}'
        if net is None:
            lines.append(f'(no_connect (at {n(ax)} {n(ay)}) (uuid {q(uid("nc/"+identity))}))')
            continue
        end=round(ax+(-5.08 if angle==0 else 5.08),4)
        lines.append(f'(wire (pts (xy {n(ax)} {n(ay)}) (xy {n(end)} {n(ay)})) '
                     f'(stroke (width 0) (type default)) (uuid {q(uid("wire/"+identity))}))')
        label_angle=180 if angle==0 else 0
        justify='left' if label_angle==0 else 'right'
        lines.append(f'(global_label {q(net)} (shape bidirectional) (at {n(end)} {n(ay)} {label_angle}) '
                     f'(effects (font (size 1 1)) (justify {justify})) (uuid {q(uid("label/"+identity))}))')
    return '\n'.join(lines)


def generate(*,components=COMPONENTS,sections=SECTIONS,out=OUT,
             subtitle='CH32X035 native USB + switched USB PD output',source='hardware/circuit.py'):
    COMPONENTS,SECTIONS,OUT=components,sections,out
    OUT.mkdir(exist_ok=True)
    library=load_library()
    validate_library(COMPONENTS,library)
    rootid=uid('root')
    root=[f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(rootid)}) (paper "A4")',
          f'(title_block (title "ch32-pico development board") (rev "{BOARD_REVISION} - prototype"))',
          '(lib_symbols)',text(subtitle,25.4,22.86,2),
          text('Electrical draft. Not a fabrication release.',25.4,30.48),
          text('USB-C CC -> CH32X035; VBUS -> load switch -> header 40',25.4,38.1),
          text(f'Python source: {source}. See docs/compatibility.md.',25.4,45.72)]
    for index,(section,title) in enumerate(SECTIONS.items()):
        sheetid=uid('sheet/'+section)
        docid=uid('document/'+section)
        sx=25.4+(index%2)*132.08
        sy=63.5+(index//2)*40.64
        filename=f'{section}.kicad_sch'
        root.append(f'(sheet (at {n(sx)} {n(sy)}) (size 111.76 25.4) (stroke (width 0.254) (type default)) '
          f'(fill (color 0 0 0 0)) (uuid {q(sheetid)}) '
          f'(property "Sheetname" {q(title)} (at {n(sx)} {n(sy-1.27)} 0) (effects (font (size 1.1 1.1)) (justify left bottom))) '
          f'(property "Sheetfile" {q(filename)} (at {n(sx)} {n(sy+26.67)} 0) (effects (font (size 1.1 1.1)) (justify left top))) '
          f'(instances (project {q(PROJECT)} (path {q("/"+rootid)} (page {q(index+2)})))))')
        comps=[c for c in COMPONENTS if c.section==section]
        codes=sorted({c.part for c in comps})
        contents=[f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(docid)}) (paper "A3")',
          f'(title_block (title {q(title)}) (rev "{BOARD_REVISION} - prototype"))',
          '(lib_symbols\n'+'\n'.join(symbol(code,library[code],True) for code in codes)+')',
          text(title,15.24,15.24,2),text('Explicit global-net connections. All NC pins are intentional.',15.24,22.86)]
        # Column packing keeps the 48-pin MCU and 40-pin header intact on one page.
        bottoms=[35.56]*4
        for c in sorted(comps,key=lambda c: (-len(library[c.part].pins),c.ref)):
            col=min(range(4),key=lambda i:bottoms[i])
            x=snap(53.34+col*101.6)
            h=geometry(library[c.part])[1]
            y=snap(bottoms[col]+h+7.62)
            if y+h>260: raise ValueError(f'{section} exceeds page height')
            contents.append(instance(c,library[c.part],x,y,'/'+rootid+'/'+sheetid))
            bottoms[col]=y+h+12.7
        contents.append(')')
        (OUT/filename).write_text('\n'.join(contents)+'\n')
    root.append(f'(sheet_instances (path "/" (page "1"))))')
    (OUT/f'{PROJECT}.kicad_sch').write_text('\n'.join(root)+'\n')
    used=sorted({c.part for c in COMPONENTS})
    (OUT/'ch32-pico.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+
        '\n'.join(symbol(code,library[code]) for code in used)+')\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "ch32-pico") (type "KiCad") '
        '(uri "${KIPRJMOD}/ch32-pico.kicad_sym") (options "") (descr "Generated typed circuit symbols")))\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "ch32-pico") (type "KiCad") '
        f'(uri {q(ROOT/"hardware/lib/ch32-pico.pretty")}) (options "") (descr "Local reviewed footprints")))\n')
    (OUT/f'{PROJECT}.kicad_pro').write_text('{}\n')
    print(f'Generated {len(SECTIONS)+1}-sheet schematic, {len(COMPONENTS)} components')


if __name__=='__main__': generate()
