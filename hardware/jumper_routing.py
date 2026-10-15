# SPDX-License-Identifier: MIT
"""Reproduce Rev E's optional GPIO and FAULT pad from the Rev D checkpoint.

Only the obsolete PC7 route is removed. All other existing traces/vias must
remain identical. The pinned native router passed this incremental workflow
where Freerouting's exchange of fixed copper did not; see Rev D's review.
"""
import hashlib
import json
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from .library import ROOT
from .diagnostics import DIAGNOSTICS
from .sexp import parse, children, one, dump
from .fabrication import copy_rules
from .route_geometry import fingerprint
from .routing import KRT_COMMIT, KRT_ENV, run, grade
from .verify_placement import verify_board

BASE_COMMIT = '23297c116df01721b025ebf881abdad9f37ba455'
BASE_SHA256 = '27489e68613338e101c4d50829765f8548391e422342914963f9be58d9745e6a'
CHANGED_NETS = {'PC7', 'GPIO35', 'PD_FAULT_N'} | {d.net for d in DIAGNOSTICS}


def prepare(doc, placed):
    # The historical checkpoint predates the capacitor/ILM BOM correction.
    # Keep its routed copper but take purchasing fields from the current seed.
    from .library import update_board_parts
    from .circuit import COMPONENTS
    update_board_parts(doc,COMPONENTS)
    for fp in children(doc, 'footprint'):
        ref=next(p[2] for p in children(fp,'property') if p[1]=='Reference')
        for pad in children(fp,'pad'):
            if (ref,pad[1]) == ('J1','35'):
                if children(pad,'net'):raise ValueError('Expected unconnected Rev D header 35')
                pad.append(parse('(net "GPIO35")'))
            if (ref,pad[1]) == ('TP7','1'):
                if one(pad,'net')[-1]!='PC7':raise ValueError('Expected Rev D PC7 pad')
                one(pad,'net')[-1]='PD_FAULT_N'
    doc[:]=[n for n in doc if not (isinstance(n,list) and n[0] in ('segment','via')
            and one(n,'net')[-1]=='PC7')]
    additions={'SJ1'} | {d.ref for d in DIAGNOSTICS}
    for fp in children(placed,'footprint'):
        ref=next(p[2] for p in children(fp,'property') if p[1]=='Reference')
        if ref in additions:doc.append(deepcopy(fp))
    from .markings import apply as markings
    from .branding import apply as branding
    markings(doc);branding(doc)
    from .stitching import apply as stitch
    stitch(doc)


def main():
    from .design import BOARD_REVISION
    if BOARD_REVISION!='E':raise ValueError('This migration applies to Rev E only')
    from .circuit import COMPONENTS
    parts={c.ref:c.part for c in COMPONENTS}
    if 'R18' not in parts or parts.get('C12')!='C307331':
        raise ValueError('Historical jumper migration predates the power-layout corrections; use just route-power')
    out=ROOT/'build/routing';out.mkdir(exist_ok=True)
    base=subprocess.check_output(['git','show',f'{BASE_COMMIT}:hardware/review/ch32-pico.kicad_pcb'],cwd=ROOT)
    if hashlib.sha256(base).hexdigest()!=BASE_SHA256:raise ValueError('Rev D checkpoint hash mismatch')
    doc=parse(base.decode())
    prepare(doc,parse((ROOT/'build/ch32-pico-placed.kicad_pcb').read_text()))
    existing=deepcopy(doc)
    source=out/'jumper-input.kicad_pcb';source.write_text(dump(doc)+'\n')
    copy_rules(ROOT/'build/ch32-pico-placed.kicad_pcb',source)
    (out/'fp-lib-table').write_text((ROOT/'build/fp-lib-table').read_text().replace(
        '${KIPRJMOD}/../hardware','${KIPRJMOD}/../../hardware'))
    verify_board(source)
    initial=grade(source)
    if initial['violations']:raise ValueError('Jumper placement conflicts with existing copper or silk')
    issues=json.loads(source.with_suffix('.drc.json').read_text())['unconnected_items']
    if any(any(not any(f'[{net}]' in item['description'] for net in CHANGED_NETS)
               for item in issue['items']) for issue in issues):
        raise ValueError('Unexpected open connection outside changed nets')
    krt=Path.home()/'git/KiCadRoutingTools'
    if subprocess.check_output(['git','-C',krt,'rev-parse','HEAD'],text=True).strip()!=KRT_COMMIT:
        raise ValueError('KiCadRoutingTools revision differs from the reviewed pin')
    if subprocess.check_output(['git','-C',krt,'status','--porcelain','--untracked-files=no'],text=True).strip():
        raise ValueError('KiCadRoutingTools has tracked modifications')
    # Route the optional PC7 header first; later probe branches must not consume
    # its only escape corridor. Each stage preserves all earlier copper.
    duration=0
    for label,nets in [('jumper-core',{'GPIO35','PC7','PD_FAULT_N'}),
                       ('krt-jumper',CHANGED_NETS-{'GPIO35','PC7','PD_FAULT_N','USB_DP','USB_DM'})]:
        target=out/(label+'.kicad_pcb')
        duration+=run([krt/'.venv/bin/python',krt/'py_router/route.py',source,target,
            '--nets',*sorted(nets),
            '--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1','-1','3','3',
            '--track-width','.15','--clearance','.15','--via-size','.45','--via-drill','.2',
            '--grid-step','.05','--no-fix-drc-settings','--same-net-pad-clearance','.1',
            '--no-stub-layer-swap','--keep-input-copper','--fab-overrides',ROOT/'hardware/fab-limits.txt',
            '--escalation','off','--max-iterations','500000','--max-ripup','0'],out/(label+'-krt.log'),env=KRT_ENV)
        copy_rules(source,target)
        # The router's final cleanup can prune earlier routed branches even
        # with keep-input-copper. Restore their exact geometry, then let KiCad
        # reject any collision with newly routed copper.
        previous=parse(source.read_text());routed=parse(target.read_text())
        from collections import Counter
        present=Counter(fingerprint(['kicad_pcb',n]) for kind in ('segment','via')
                        for n in children(routed,kind))
        restored=0
        for kind in ('segment','via'):
            for n in children(previous,kind):
                key=fingerprint(['kicad_pcb',n])
                if present[key]:present[key]-=1
                else:routed.append(deepcopy(n));restored+=1
        if restored:target.write_text(dump(routed)+'\n')
        print(f'{label}: restored {restored} pre-existing copper items pruned by router cleanup')
        source=target
    result=grade(target)
    routed=parse(target.read_text())
    # New FAULT branches may share the old net; compare geometry as a multiset
    # rather than excluding that entire net from the preservation requirement.
    from collections import Counter
    def copper(doc):
        return Counter(fingerprint(['kicad_pcb',n]) for kind in ('segment','via') for n in children(doc,kind))
    if copper(existing)-copper(routed):raise ValueError('Router changed pre-existing copper')
    result.update(seconds=duration,preexisting_copper_preserved=True,
                  replaced_net='PC7',added_connections=['SJ1 to header 35','SJ1 to PC7','TP7 to FAULT',*[d.ref+' to '+d.net for d in DIAGNOSTICS]])
    manifest={'status':'passed' if result['passes_connectivity_and_drc'] else 'failed',
        'started_at':datetime.now(timezone.utc).isoformat(),'base_commit':BASE_COMMIT,
        'base_board_sha256':BASE_SHA256,'krt_commit':KRT_COMMIT,
        'operation':'Replace PC7 branch with open SJ1; expose FAULT and diagnostic contacts; preserve other copper',
        'candidates':{'krt-jumper':result},'fabrication_ready':False}
    (out/'comparison.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if not result['passes_connectivity_and_drc']:raise ValueError('Jumper route failed independent checks')
    print('Rev E jumper and FAULT routing passed')


if __name__=='__main__':main()
