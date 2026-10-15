# SPDX-License-Identifier: MIT
"""Short, grouped high-current copper; qualification still requires hardware."""
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
route('VBUS',1.6,(6.6,8.65),(4.2,11.05),(4.2,12.0),layer='B.Cu')
bank('VBUS',(3.7,4.2),(11.5,12.1))
route('VBUS',.8,(3.7,11),(4.1,11),(4.1,12.0))
route('VBUS',.8,(4.1,10.52),(4.1,11))
for n in ('1','2','3'):
    x,y=pad('Q1',n);route('VBUS',.4,(x,y),(4.1,y))
route('VBUS',.5,pad('C16','1'),(4.1,11))
# Drain spread: all four drain leads and exposed drain land join locally.
route('PD_INPUT',1.0,pad('Q1','9'),(7.15,13.2),(8.3,13.2))
route('PD_INPUT',.5,pad('Q1','8'),pad('Q1','5'))
bank('PD_INPUT',(7.7,8.3),(13.0,13.55))
route('PD_INPUT',.4,(8.3,13.2),pad('C14','1'))
route('PD_INPUT',1.4,(8.0,13.2),(7.9,14.1),(6.2,14.1),(6.2,15.5),layer='B.Cu')
bank('PD_INPUT',(6.1,6.55),(14.9,15.5))
for n in ('1','2'):
    x,y=pad('U3',n);route('PD_INPUT',.28,(x,y),(6.2,y))
route('PD_INPUT',.7,(6.2,14.9),(6.2,15.55))
# Output spread and a 1.8 mm outer-layer trunk to header pin 40.
for n in ('17','18'):
    x,y=pad('U3',n);route('PD_OUT',.28,(x,y),(11.8,y))
route('PD_OUT',.8,(11.8,15.05),(11.8,15.6),(12.7,15.6))
bank('PD_OUT',(11.8,12.4),(15.0,15.6))
route('PD_OUT',1.8,(12.1,15.3),(17.3,15.3),(17.3,5),layer='B.Cu')
route('PD_OUT',1.2,(17.3,5),(17.7,4.5),(17.7,1.9),(18.2,1.37),(19.39,1.37),layer='B.Cu')
bank('PD_OUT',(14.6,15.15),(17.0,17.55))
route('PD_OUT',1,(14.6,17.0),pad('C12','1'))
route('PD_OUT',1,(14.85,17.3),(17.3,15.3),layer='B.Cu')
route('PD_OUT',.8,pad('C12','1'),pad('D7','1'))
# Sense the output locally; only the divided voltage runs toward the MCU.
route('PD_OUT',.25,pad('R5','1'),(14.2,14.95))
VIAS.append(('PD_OUT',14.2,14.95))
route('PDOUT_SENSE',.15,pad('R5','2'),(13.4,13.37))
VIAS.append(('PDOUT_SENSE',13.4,13.37))
# Local high-current input/output clamps retain their reviewed connector positions.
route('VBUS',.65,(16.45,1.82),(17.75,1.82))
bank('VBUS',(16.3,16.9),(1.1,))
route('VBUS',.6,(16.3,1.1),(16.9,1.1),(16.9,1.82))
route('VBUS',.6,(16.3,1.1),(16.9,1.1),layer='In2.Cu')
route('VBUS',.6,(12.9,7.85),(11.8,7.4),(11.8,4.5),(12.5,4.5),(12.5,.9),(16.3,.9),(16.3,1.1),layer='In2.Cu')
bank('PD_OUT',(15.5,16.0),(4.5,))
route('PD_OUT',.65,(15.5,4.5),(15.5,5.02),(17.75,5.02))
route('PD_OUT',.8,(15.5,4.5),(17.3,5),layer='B.Cu')
for y in (2.8,6):
    route('GND',.5,(16.45,y+.98),(17.75,y+.98))
    route('GND',.5,(17.1,y),(17.1,y+.98))
    route('GND',.4,(17.1,y),(15.7,y));VIAS.append(('GND',15.7,y))
# Programmable slew, current limit and IMON resistor have short top-layer paths.
route('PD_DVDT',.15,pad('U3','9'),pad('C8','1'))
route('PD_ILM',.15,pad('U3','10'),(9.25,19.2),pad('R17','1'))
route('PD_IMON',.15,pad('U3','13'),(11.45,17.55),pad('R25','1'))
route('PD_OVLO',.15,pad('U3','7'),(7.75,18.8),(6.0,19.6),pad('R21','1'))
route('PD_OVLO',.15,(6.0,19.6),pad('R20','2'))
# EP heat exits through grounded perimeter pins to off-pad via banks.
for pin in ('8','11','15'):
    x,y=pad('U3',pin)
    route('GND',.28,pad('U3','25'),(x,17.5) if pin in ('8','11') else (10.2,y),pad('U3',pin))
route('GND',.28,pad('U3','8'),(8.25,18.65))
route('GND',.28,pad('U3','11'),(9.75,18.8))
route('GND',.28,pad('U3','15'),(11.34,16.55))
bank('GND',(8.25,),(18.65,));bank('GND',(9.75,),(18.8,));bank('GND',(11.34,),(16.55,))
# Reserve a legal escape for FAULT between the ground and IMON connections.
route('PD_FAULT_N',.15,pad('U3','14'),(11.74,17.002))
VIAS.append(('PD_FAULT_N',11.74,17.002))
route('GND',.6,pad('D7','2'),(16.8,22.2));bank('GND',(16.5,17.1),(22.2,))
