# SPDX-License-Identifier: MIT
"""Explicit LQFP48 escapes at U1's reviewed 90-degree placement.

Ordinary 0.45/0.20 mm vias stay outside solder lands. Inner rows are
staggered; the crowded left decoupling region uses inward escapes.
"""
from .circuit import COMPONENTS

ROUTES=[]
VIAS=[]
nets=next(c.nets for c in COMPONENTS if c.ref=='U1')


def escape(pin,points):
    net=nets[str(pin)]
    ROUTES.append(('F.Cu',net,.15,points))
    VIAS.append((net,*points[-1]))
    # Give the router an explicit internal-layer endpoint at each escape.
    # A bare through via at the end of a front-layer stub otherwise leaves
    # some multipoint searches confined to the crowded front-layer pocket.
    if net=='PA3':return
    x,y=points[-1]
    if pin<=12: end=(x,y+(.4 if y>30.3 else -.4))
    elif pin<=24: end=(x+.35,y)
    elif pin<=36: end=(x,y+(.4 if y>25.4 else -.4))
    elif pin<=42: end=(x-.35,y)
    else:end=(x+(.35 if x>8 else -.35),y)
    ROUTES.append(('In2.Cu',net,.15,[(x,y),end]))


for pin in range(1,13):
    x=7.75+(pin-1)*.5
    target=(x,30.65 if pin%2 else 30.0)
    if pin==2:target=(8.3,30.05)
    escape(pin,[(x,32.1625),(x,31.3),target])
for pin in range(13,25):
    y=30.75-(pin-13)*.5
    escape(pin,[(14.6625,y),(15.2,y),(16.1,24.7+.6*(24-pin))])
for pin in range(25,37):
    if pin in (32,33):continue  # USB remains on its reviewed front-layer path.
    x=13.25-(pin-25)*.5
    escape(pin,[(x,23.8375),(x,25.1 if (36-pin)%2==0 else 25.75)])
for pin in range(37,43):
    y=25.25+(pin-37)*.5
    escape(pin,[(6.3375,y),(5.75,y),(4.9,24.6+.6*(pin-37))])
for pin in range(43,47):
    y=28.25+(pin-43)*.5
    target=(7.7 if pin%2 else 8.35,y)
    if pin==46:target=(7.65,29.9)
    escape(pin,[(6.3375,y),target])

# Translate the reviewed local fanout with U1; header escapes stay fixed.
from .placement import PLACEMENT
_dx, _dy = PLACEMENT['U1'][0]-10.5, PLACEMENT['U1'][1]-28
ROUTES[:] = [(layer, net, width, [(x+_dx,y+_dy) for x,y in points]) for layer,net,width,points in ROUTES]
VIAS[:] = [(net,x+_dx,y+_dy) for net,x,y in VIAS]

# Explicit internal-layer exits at plated header contacts give both ends of
# a GPIO connection an internal-layer routing endpoint. Supply rails retain
# their separately sized power paths.
from .design import MECHANICAL
header=next(c.nets for c in COMPONENTS if c.ref=='J1')
for pin in range(1,41):
    net=header[str(pin)]
    if net in ('GND','3V3_OUT','VBUS','VSYS') or net is None:continue
    # The local D5 ground-via pair occupies these straight exits.
    # Route from the plated contact around the returns instead of seeding a short.
    if net in ('PA8','PA11'):continue
    x,y=MECHANICAL.position(pin)
    ROUTES.append(('In2.Cu',net,.15,[(x,y),(2.9 if x<10 else 18.1,y)]))


def add_fanout(source, output):
    """Add routing aids; final cleanup may prune unused GPIO exits.

    These are not part of the locked USB/power geometry contract.
    """
    from .sexp import parse, dump
    from .schematic import uid
    from .fabrication import copy_rules
    doc = parse(source.read_text())
    for i, (layer, net, width, points) in enumerate(ROUTES):
        for j, (a, b) in enumerate(zip(points, points[1:])):
            doc.append(parse(f'''(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]})
                (width {width}) (layer "{layer}") (net "{net}")
                (uuid "{uid(f'fanout/route/{i}/{j}')}"))'''))
    for i, (net, x, y) in enumerate(VIAS):
        doc.append(parse(f'''(via (at {x} {y}) (size .45) (drill .2)
            (layers "F.Cu" "B.Cu") (net "{net}")
            (uuid "{uid(f'fanout/via/{i}')}"))'''))
    output.write_text(dump(doc) + '\n')
    copy_rules(source, output)
