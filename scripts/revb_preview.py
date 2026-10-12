# SPDX-License-Identifier: MIT
"""Front/back draft CAD placement preview; no simulated copper or 3D bodies."""
from pathlib import Path
import subprocess,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
SVG='http://www.w3.org/2000/svg';E.register_namespace('',SVG)

def main():
    board=ROOT/'build/ch32-pico-placed.kicad_pcb'
    out=ROOT/'docs/images/rev-b-placement.svg'
    doc=E.Element('{'+SVG+'}svg',{'width':'680','height':'860','viewBox':'0 0 680 860'})
    E.SubElement(doc,'{'+SVG+'}rect',{'width':'680','height':'860','fill':'#17202a'})
    for title,x,layers,mirror in [('FRONT',20,'F.Cu,F.Fab,F.Silkscreen,Edge.Cuts',False),
                                  ('BACK',360,'B.Cu,B.Silkscreen,Edge.Cuts',True)]:
        p=ROOT/f'build/revb-{title.lower()}.svg'
        command=['kicad-cli','pcb','export','svg','--mode-single','--layers',layers,
                 '--fit-page-to-board','--exclude-drawing-sheet','-o',str(p),str(board)]
        if mirror:command.append('--mirror')
        subprocess.run(command,check=True)
        title_node=E.SubElement(doc,'{'+SVG+'}text',{'x':str(x+150),'y':'38','text-anchor':'middle',
            'fill':'white','font-family':'sans-serif','font-size':'20'})
        title_node.text=title
        source=E.parse(p).getroot();source.set('x',str(x));source.set('y','58')
        source.set('width','300');source.set('height','730');doc.append(source)
    label=E.SubElement(doc,'{'+SVG+'}text',{'x':'340','y':'835','text-anchor':'middle',
        'fill':'white','font-family':'sans-serif','font-size':'16'})
    label.text='REV B — UNROUTED PLACEMENT DRAFT'
    E.ElementTree(doc).write(out,encoding='unicode')
    subprocess.run(['rsvg-convert','-o',str(out.with_suffix('.png')),str(out)],check=True)
if __name__=='__main__':main()
