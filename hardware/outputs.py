# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Derived procurement and firmware definitions. Draft outputs, not a release."""
import csv
import json
from collections import defaultdict
from .circuit import COMPONENTS
from .library import ROOT, load_library, validate_library


def generate():
    lib=load_library()
    validate_library(COMPONENTS,lib)
    out=ROOT/'build'; out.mkdir(exist_ok=True)
    grouped=defaultdict(list)
    for c in COMPONENTS:
        if c.fitted: grouped[(c.part,c.value)].append(c.ref)
    with (out/'draft-bom.csv').open('w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['Comment','Designator','Footprint','LCSC Part #','Quantity','Manufacturer','MPN'])
        for (code,value),refs in sorted(grouped.items()):
            p=lib[code]
            w.writerow([value or p.mpn,','.join(refs),p.footprint,code,len(refs),p.manufacturer,p.mpn])
    (out/'circuit.json').write_text(json.dumps({c.ref:{'lcsc':lib[c.part].code,'mpn':lib[c.part].mpn,
        'footprint':lib[c.part].footprint,'fitted':c.fitted,'nets':c.nets,'note':c.note}
        for c in COMPONENTS},indent=2)+'\n')
    print(f'Draft BOM: {sum(len(v) for v in grouped.values())} fitted parts, {len(grouped)} BOM rows')


if __name__=='__main__': generate()
