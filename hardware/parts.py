# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Procurement catalogue derived from the circuit's exact fitted LCSC parts.

Listing URLs identify candidates. Stock and JLC assembly availability must be
recorded separately and rechecked for the production quantity before release.
"""
import csv
import re
from .circuit import COMPONENTS
from .library import load_library, validate_library


def validate_parts(root):
    library=load_library()
    validate_library(COMPONENTS,library)
    for c in COMPONENTS:
        if c.fitted and not re.fullmatch(r'C[1-9][0-9]*',library[c.part].code):
            raise ValueError(f'{c.ref}: invalid LCSC identifier')


def export_candidates(root):
    validate_parts(root)
    library=load_library()
    codes=sorted({c.part for c in COMPONENTS if c.fitted},key=lambda c:int(c[1:]))
    with (root/'build/candidate-parts.csv').open('w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['MPN','Manufacturer','LCSC Part','LCSC URL','JLCPCB URL','Footprint','Availability status'])
        for code in codes:
            p=library[code]
            w.writerow([p.mpn,p.manufacturer,code,f'https://www.lcsc.com/product-detail/{code}.html',
                f'https://jlcpcb.com/partdetail/{code}',p.footprint,'Live stock and assembly quantity check required'])
