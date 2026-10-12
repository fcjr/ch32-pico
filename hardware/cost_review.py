# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Dated JLC parts-only estimate; assembly, stock allocation and tax are separate."""
import json
from collections import Counter
from .circuit import COMPONENTS
from .library import ROOT


def report(panels=5,boards_per_panel=4,*,components=COMPONENTS,source=None):
    if source is None:
        source=json.loads((ROOT/'hardware/procurement-observation.json').read_text())
    qty=panels*boards_per_panel;counts=Counter(c.part for c in components if c.fitted)
    rows=[]
    for code,count in counts.items():
        part=source['parts'][code];required=count*qty
        tiers=[t for t in part['price_tiers_usd'] if t['minimum']<=required and (t['maximum']<0 or required<=t['maximum'])]
        if len(tiers)!=1:raise ValueError(f'No unique price tier for {code} at {required}')
        price=tiers[0]['unit_usd']
        rows.append({'lcsc':code,'mpn':part['mpn'],'per_board':count,'build_quantity':required,
            'unit_usd':price,'extended_usd':round(required*price,4),'per_board_usd':round(count*price,4),
            'jlc_stock':part['jlc_reported_stock'],'stock_shortfall_before_attrition':max(0,required-part['jlc_reported_stock']),
            'reported_attrition':part['reported_attrition'],'reported_assembly_minimum':part['reported_assembly_minimum'],
            'minimum_prepurchase':part['minimum_prepurchase']})
    total=sum(row['extended_usd'] for row in rows)
    return {'status':'low-cost parts estimate; not a quote',
        'observed_utc':source['observed_utc'],'panels':panels,'boards_per_panel':boards_per_panel,'total_boards':qty,
        'parts_only_usd':round(total,4),'parts_per_board_usd':round(total/qty,4),
        'excludes':['PCB fabrication, castellations, finish and panel charges',
            'Assembly setup, feeder fees, solder joints and any manual insertion',
            'Attrition, minimum purchase uplifts, shipping and tax'],
        'attrition_verified_for_order':False,'prototype_price_tier_confirmed':False,
        'assembly_service':'Standard','economic_eligible':False,
        'economic_exclusion':'Castellated holes; see JLC assembly capabilities.',
        'rows':sorted(rows,key=lambda row:-row['extended_usd'])}


def main():
    result=report();path=ROOT/'build/cost-review.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(f"{result['panels']} panels x {result['boards_per_panel']} boards = {result['total_boards']} boards")
    print(f"Parts only: ${result['parts_per_board_usd']:.2f}/board, ${result['parts_only_usd']:.2f}/batch")
    for row in result['rows'][:8]:print(row['lcsc'],row['mpn'],row['per_board_usd'])


if __name__=='__main__':main()
