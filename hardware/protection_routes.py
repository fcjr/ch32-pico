# SPDX-License-Identifier: MIT
"""Short VBUS copper from USB-C to the clamp, control supply and header pin 40.

Qualification still requires hardware.
"""
import math
from functools import lru_cache
from .circuit import COMPONENTS
from .library import LIBDIR,load_library
from .placement import PLACEMENT
from .sexp import parse,children,one
ROUTES=[]
VIAS=[]

@lru_cache(None)
def pad(ref,number):
    c=next(c for c in COMPONENTS if c.ref==ref);part=load_library()[c.part]
    fp=parse((LIBDIR/'ch32-pico.pretty'/f'{part.footprint}.kicad_mod').read_text())
    p=next(p for p in children(fp,'pad') if p[1]==number)
    x,y=map(float,one(p,'at')[1:3]);fx,fy,*a=PLACEMENT[ref];angle=math.radians(a[0] if a else 0)
    return (round(fx+x*math.cos(angle)+y*math.sin(angle),6),round(fy-x*math.sin(angle)+y*math.cos(angle),6))

def route(net,width,*points,layer='F.Cu'):
    ROUTES.append((layer,net,width,list(points)))

def bank(net,xs,ys):
    VIAS.extend((net,x,y) for x in xs for y in ys)

# Full pad-width VBUS stubs and parallel through-via banks.
route('VBUS',.6,(8.1,7.09),(8.1,8),(7.5,8.15),(6.6,8.15))
route('VBUS',.6,(12.9,7.09),(12.9,7.85))
bank('VBUS',(6.6,7.2),(8.15,));bank('VBUS',(6.6,),(8.65,))
bank('VBUS',(12.9,),(7.85,))
for layer in ('B.Cu','In2.Cu'):
    route('VBUS',.9,(6.6,8.15),(7.2,7.8),(12.9,7.8),(12.9,7.85),layer=layer)
# Header pin 40 is direct VBUS, like the Pico. The 1.2 mm bottom trunk passes
# below the connector stitch via, then follows the right edge to the pin.
route('VBUS',1.2,(12.9,7.85),(13.6,8.55),(16.0,8.55),(17.3,7.25),(17.3,5),(17.7,4.5),
      (17.7,1.9),(18.2,1.37),(19.39,1.37),layer='B.Cu')
# Second feed: the right connector pad reaches pin 40 on the front layer,
# passing the locating peg and between the shell stakes. Neither connector
# pad then depends on a single through-via for load current.
route('VBUS',.4,(12.9,7.09),(12.9,6.65),(12.6,6.1),(12.2,5.7),(12.2,4.4))
route('VBUS',.8,(12.2,4.4),(16.5,4.4),(18.0,2.9),(19.39,1.37))
# Control-supply branch: left via bank, then In2 to D1.
route('VBUS',1.6,(6.6,8.65),(6.0,10.1),layer='B.Cu')
bank('VBUS',(5.5,5.95),(10.0,10.55))
route('VBUS',.4,(5.95,10.55),(4.6,11.3),(4.6,17.8),(6.3,17.8),layer='In2.Cu')
VIAS.append(('VBUS',6.3,17.8))
route('VBUS',.5,(6.3,17.8),(6.25,17.8),(5.4,18.1))
route('VBUS',.3,(5.4,18.1),(5.4,18.9),(5.1,19.4),(4.9,20.0),pad('D1','2'))
# The clamp sits at the USB breakout, ahead of every other VBUS load.
route('VBUS',.45,pad('D5','6'),pad('D5','4'))
route('VBUS',.6,(6.6,8.15),(5.2,8.02),pad('D5','4'))
route('GND',.5,pad('D5','1'),pad('D5','3'))
route('GND',.5,pad('D5','7'),pad('D5','2'))
route('GND',.4,pad('D5','7'),(2.9,9.0),(2.9,8.7),(2.9,9.3))
bank('GND',(2.9,),(8.7,9.3))
route('GND',.4,pad('R3','2'),(5.2,9.3),pad('D5','7'))
# Connector-control escapes sit outside the VBUS banks and USB return keepouts.
route('CC1',.15,pad('R3','1'),(7.9,9.3));VIAS.append(('CC1',7.9,9.3))
route('BOOT_PULLUP',.15,pad('R12','2'),(12.1,10.7),(12.1,11.2));VIAS.append(('BOOT_PULLUP',12.1,11.2))
