# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Read JLC's public part-page inventory; no account, cart, or order mutation.

Observations are dated and retain response hashes. They are not reservations.
The exact C-number and MPN must match before accepting any reported stock.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import concurrent.futures
import datetime
import hashlib
import json
import re
import urllib.request
from hardware.circuit import COMPONENTS
from hardware.library import ROOT,load_library


def inspect(code,part):
    url=f'https://jlcpcb.com/partdetail/{code}'
    raw=urllib.request.urlopen(url,timeout=40).read()
    cache=ROOT/'build/procurement';cache.mkdir(exist_ok=True)
    (cache/(code+'.html')).write_bytes(raw)
    chunks=[]
    for match in re.finditer(r'self\.__next_f\.push\((.*?)\)</script>',raw.decode()):
        try:chunks.extend(x for x in json.loads(match[1]) if isinstance(x,str))
        except (ValueError,TypeError):continue
    # React Flight text records can be length-delimited instead of newline
    # terminated. Decode JSON records at their own offsets, including the
    # first price tier following a datasheet text record.
    records={};decoder=json.JSONDecoder();payload=''.join(chunks)
    for match in re.finditer(r'([0-9a-f]+):(?=[\[{])',payload):
        try:records[match[1]]=decoder.raw_decode(payload,match.end())[0]
        except ValueError:continue
    objects=[o for o in records.values() if isinstance(o,dict) and o.get('componentCode')==code]
    item=next((o for o in objects if 'overseasStockCount' in o),None)
    if item is None:raise ValueError('No exact-part inventory record in response')
    if item.get('componentModelEn')!=part.mpn:raise ValueError(f'MPN mismatch: {item.get("componentModelEn")} != {part.mpn}')
    tiers=sorted(({'minimum':o['startNumber'],'maximum':o['endNumber'],'unit_usd':o['productPrice']}
        for o in objects if all(k in o for k in ('startNumber','endNumber','productPrice'))),key=lambda o:o['minimum'])
    return {'mpn':part.mpn,'jlc_url':url,'lcsc_url':f'https://www.lcsc.com/product-detail/{code}.html',
        'jlc_reported_stock':item['overseasStockCount'],'jlc_can_presale_number':item.get('canPresaleNumber'),
        'is_buy_component':item.get('isBuyComponent'),'minimum_prepurchase':item.get('preMinPurchaseNum'),
        'no_buy_reason':item.get('noBuyReason'),'package':item.get('componentSpecificationEn'),
        'price_tiers_usd':tiers,'displayed_initial_unit_usd':item.get('initialPrice'),
        'reported_attrition':item.get('lossNumber'),'reported_assembly_minimum':item.get('leastPatchNumber'),
        'response_sha256':hashlib.sha256(raw).hexdigest(),'exact_mpn_match':True}


def main():
    lib=load_library();codes=sorted({c.part for c in COMPONENTS if c.fitted})
    results={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(inspect,c,lib[c]):c for c in codes}
        for f in concurrent.futures.as_completed(futures):
            code=futures[f]
            try:results[code]=f.result();print(code,results[code]['jlc_reported_stock'],flush=True)
            except Exception as e:results[code]={'mpn':lib[code].mpn,'error':str(e)};print(code,str(e),flush=True)
    report={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source':'JLCPCB public product pages','stock_is_not_reserved':True,
        'lcsc_live_stock_independently_verified':False,'assembly_attrition_quantity_reviewed':False,
        'parts':dict(sorted(results.items()))}
    (ROOT/'hardware/procurement-observation.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
