# SPDX-License-Identifier: MIT
"""Use KiCad's plotted strokes in the disposable 3D render copy.

The macOS 10.0.6 3D text path intermittently drops glyphs. The SVG plotter
provides the complete stroke geometry. The source board keeps editable text;
only its render copy gets line primitives. No raster image is retouched.
"""
from collections import Counter
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

from hardware.sexp import children, one, parse
from hardware.schematic import uid


LINE = re.compile(r'\s*M\s*([-\d.]+)\s+([-\d.]+)\s*L\s*([-\d.]+)\s+([-\d.]+)\s*')


def apply(doc, source: Path, directory: Path):
    replacements=[]
    for layer in ('F.SilkS','B.SilkS'):
        svg=directory/(layer+'.svg')
        subprocess.run(['kicad-cli','pcb','export','svg','--mode-single','--layers',layer,
                        '--fit-page-to-board','--exclude-drawing-sheet','-o',str(svg),str(source)],check=True)
        root=ET.parse(svg).getroot()
        expected=Counter(n[1] for n in children(doc,'gr_text') if one(n,'layer')[1]==layer)
        plotted=Counter(e.text for e in root.iter() if e.tag.endswith('}text'))
        if expected!=plotted:raise ValueError('Plotted silk text differs from the checked board')
        def walk(element, width=None):
            if element.tag.endswith('}text'):return
            transform=element.attrib.get('transform')
            if transform and transform!='translate(0 0) scale(1 1)':
                raise ValueError('Unexpected SVG transform; review render coordinate conversion')
            style=dict(item.strip().split(':',1) for item in element.attrib.get('style','').split(';') if ':' in item)
            if 'stroke-width' in style:width=float(style['stroke-width'])
            if element.tag.endswith('}path'):
                match=LINE.fullmatch(element.attrib['d'])
                if not match or width is None:raise ValueError('Unsupported plotted silk geometry')
                x1,y1,x2,y2=map(float,match.groups())
                replacements.append(parse(f'''(gr_line (start {x1} {y1}) (end {x2} {y2})
                    (stroke (width {width}) (type solid)) (layer "{layer}")
                    (uuid "{uid('render/silk/'+str(len(replacements)))}"))'''))
            for child in element:walk(child,width)
        walk(root)
    doc[:]=[n for n in doc if not (isinstance(n,list) and n and n[0] in ('gr_text','gr_line')
            and one(n,'layer')[1] in ('F.SilkS','B.SilkS'))]
    doc.extend(replacements)
    return len(replacements)
