# SPDX-License-Identifier: MIT
"""Reviewed Rev B land patterns. No network or workstation library dependency."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hardware.sexp import parse,children,one,dump,Atom
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'hardware/lib/ch32-pico.pretty'


def main():
    # G-Switch GT-USB-7010AW, drawing 2023-02-01. 5A on VBUS.
    # Same shell/stake family as the vendored KiCad ASV. Correct the AW row
    # and rear stake dimensions, and move the SMT row 0.050 mm tailward
    # within the drawing's +/-0.05 land-pattern tolerance for 0.20 hole gap.
    from scripts.usb_candidate_fit import prepare_footprint
    prepare_footprint(DEST)
    old='USB_C_Receptacle_G-Switch_GT-USB-7010ASV'
    name='USB_C_Receptacle_G-Switch_GT-USB-7010AW'
    doc=parse((DEST/(old+'.kicad_mod')).read_text());doc[1]=name
    for prop in children(doc,'property'):
        if prop[1]=='Value':prop[2]=name
    for p in children(doc,'pad'):
        if p[2]=='smd':
            one(p,'at')[2]=Atom('-3.715');one(p,'size')[2]=Atom('1.15')
        elif p[1]=='SH':
            x,y=map(float,one(p,'at')[1:3])
            p[1]=str(13 if x<0 and y<0 else 14 if x>0 and y<0 else 15 if x<0 else 16)
            if y<0:one(p,'at')[2]=Atom('-3.105')
    (DEST/(name+'.kicad_mod')).write_text(dump(doc)+'\n')
    # TI RPW0010A drawing 4225183/A. The two rectangles of each corner
    # deliberately share a terminal number; this avoids a 5um custom-pad
    # anchor in the imported model. Copper union follows the L-shaped land.
    name='TI_RPW0010A_VQFN-HR-10_2x2mm'
    d=[f'(footprint "{name}" (version 20241229) (generator "ch32-pico") (layer "F.Cu") (attr smd)',
       '(descr "TI RPW0010A 4225183/A; 0.45 pitch, 2.4mm IN/OUT lands")',
       '(fp_rect (start -1 -1) (end 1 1) (stroke (width .1) (type solid)) (fill none) (layer "F.Fab"))',
       '(fp_rect (start -1.425 -1.425) (end 1.425 1.425) (stroke (width .05) (type solid)) (fill none) (layer "F.CrtYd"))']
    def pad(n,x,y,w,h):
        d.append(f'(pad "{n}" smd rect (at {x} {y}) (size {w} {h}) (layers "F.Cu" "F.Mask"))')
    def paste(x,y,w,h):
        d.append(f'(pad "" smd roundrect (at {x} {y}) (size {w} {h}) '
                 f'(layers "F.Paste") (roundrect_rratio {0.05/min(w,h):.9f}))')
    for n,sx,sy in ((1,-1,-1),(4,-1,1),(7,1,1),(10,1,-1)):
        pad(n,sx*.9,sy*.7,.6,.3);pad(n,sx*.725,sy*.875,.25,.65)
        # TI 4225183/A, example for a 0.100 mm stencil. Separate paste lands
        # preserve the full copper land while reducing corner paste to ~93%.
        paste(sx*.9,sy*.6875,.6,.275);paste(sx*.7125,sy*.875,.225,.65)
    for n,x,y in ((2,-.9,-.225),(3,-.9,.225),(8,.9,.225),(9,.9,-.225)):
        pad(n,x,y,.6,.25)
        paste(x,y,.6,.25)
    pad(5,-.25,0,.3,2.4);pad(6,.25,0,.3,2.4)
    for x in (-.25,.25):
        # Two apertures per IN/OUT terminal, ~82% copper coverage.
        for y in (-.63,.63):paste(x,y,.28,1.06)
    d.append(')');(DEST/(name+'.kicad_mod')).write_text(dump(parse('\n'.join(d)))+'\n')
    symbols=ROOT/'hardware/lib/ch32-pico.kicad_sym';doc=parse(symbols.read_text())
    aliases={'C963411':'USB_C_Receptacle_G-Switch_GT-USB-7010AW','C3662793':name}
    for sym in children(doc,'symbol'):
        p={p[1]:p for p in children(sym,'property')}
        code=p['LCSC Part'][2]
        if code in aliases:p['Footprint'][2]='ch32-pico:'+aliases[code]
    symbols.write_text(dump(doc)+'\n')

if __name__=='__main__':main()
