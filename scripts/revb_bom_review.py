# SPDX-License-Identifier: MIT
"""Fitted-component cost only, from the checked public inventory snapshot."""
from pathlib import Path
import sys,json
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from hardware.circuit import COMPONENTS
from hardware.design import BOARD_REVISION

def main():
    source=json.loads((ROOT/'hardware/procurement-observation.json').read_text());rows=[]
    for code,n in sorted(Counter(c.part for c in COMPONENTS if c.fitted).items()):
        p=source['parts'][code]
        if not p.get('exact_mpn_match'):raise ValueError(f'No verified price observation: {code}')
        tier=max((t for t in p['price_tiers_usd'] if t['minimum']<=20*n),key=lambda t:t['minimum'])
        rows.append({'lcsc':code,'mpn':p['mpn'],'per_board':n,'net_20_board_quantity':20*n,
            'unit_usd':tier['unit_usd'],'per_board_usd':round(n*tier['unit_usd'],4),
            'reported_stock':p['jlc_reported_stock'],'stock_covers_net_quantity':p['jlc_reported_stock']>=20*n})
    d={'revision':BOARD_REVISION,'status':'draft fitted BOM estimate, not an order quote',
       'observed_utc':source['observed_utc'],'boards':20,'fitted_per_board':sum(r['per_board'] for r in rows),
       'per_board_bom_usd':round(sum(r['per_board_usd'] for r in rows),4),
       'excludes':['PCB/panel','assembly','setup','attrition','MOQ rounding','shipping','tax'],
       'stock_is_not_reserved':True,'parts':rows}
    (ROOT/'build/revb-bom-review.json').write_text(json.dumps(d,indent=2)+'\n')
    print(f"Draft fitted BOM: ${d['per_board_bom_usd']:.4f}/board, {d['fitted_per_board']} parts")
if __name__=='__main__':main()
