# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Remove KiCad-reported unused vias, their dead escapes, and tiny stubs.

Always checks the resulting board again. No exception is added to DRC, and a
connectivity regression rejects the cleanup. Use unused-via removal only after
signal routing; those vias may be useful escape points before routing.
"""
import argparse
import json
import math
import shutil
import subprocess
import re
from collections import Counter
from pathlib import Path
from .sexp import parse,children,one,dump
from .fabrication import copy_rules
from .route_geometry import trim_to_junctions
from .critical_routes import PROTECTED_NETS


def check(board):
    report=board.with_suffix('.cleanup-drc.json')
    subprocess.run(['kicad-cli','pcb','drc','--severity-all','--refill-zones',
        '--save-board','--format','json','-o',str(report),str(board)],check=True,
        stdout=subprocess.DEVNULL)
    return json.loads(report.read_text())


def clean(source,output,unused_vias=False):
    output.with_suffix('.cleanup.json').unlink(missing_ok=True)
    shutil.copyfile(source,output)
    copy_rules(source,output)
    before=check(output);doc=parse(output.read_text());remove=[];trimmed=[]
    nodes={one(n,'uuid')[1]:n for kind in ('segment','via') for n in children(doc,kind)}
    for violation in before['violations']:
        kind=violation['type']
        if kind!='track_dangling' and not (unused_vias and kind=='via_dangling'):continue
        for item in violation['items']:
            node=nodes.get(item['uuid'])
            if node is None:continue
            if node[0]=='segment':
                start=tuple(map(float,one(node,'start')[1:3]));end=tuple(map(float,one(node,'end')[1:3]))
                if math.dist(start,end)>.05:continue
            remove.append(item['uuid'])
    doc[:]=[n for n in doc if not (isinstance(n,list) and n[0] in ('segment','via') and one(n,'uuid')[1] in remove)]
    output.write_text(dump(doc)+'\n')
    def open_nets(report):
        counts=Counter()
        for violation in report['unconnected_items']:
            names={name for item in violation['items'] for name in re.findall(r'\[([^]]+)\]',item['description'])}
            for name in names:counts[name]+=1
        return counts
    def reject(message):
        shutil.copyfile(source,output)
        check(output)
        output.with_suffix('.cleanup.json').write_text(json.dumps({'accepted':False,'reason':message})+'\n')
        raise ValueError(message+'; restored input board')
    baseline=open_nets(before)
    after=check(output)
    if open_nets(after)-baseline:reject('Cleanup increased a net\'s unconnected count')
    old={(v['type'],tuple(sorted(i['uuid'] for i in v['items']))) for v in before['violations']}
    # Removing an unused via exposes its now-dead escape as a dangling track.
    # Follow only these newly reported dead ends; check each removal round.
    for _ in range(10):
        dead=[];doc=parse(output.read_text())
        nodes={one(n,'uuid')[1]:n for n in children(doc,'segment')}
        if unused_vias:
            for violation in after['violations']:
                signature=(violation['type'],tuple(sorted(i['uuid'] for i in violation['items'])))
                if signature in old or violation['type']!='track_dangling':continue
                for item in violation['items']:
                    node=nodes.get(item['uuid'])
                    if node is None:continue
                    # Electrical critical paths must not be pruned by this pass.
                    if one(node,'net')[-1] in PROTECTED_NETS:continue
                    dead.append(item['uuid'])
        if not dead:break
        for identifier in dead:
            node=nodes[identifier]
            if trim_to_junctions(doc,node):trimmed.append(identifier)
            else:doc.remove(node);remove.append(identifier)
        output.write_text(dump(doc)+'\n');after=check(output)
        if open_nets(after)-baseline:reject('Dead-escape removal increased a net\'s unconnected count')
    new={(v['type'],tuple(sorted(i['uuid'] for i in v['items']))) for v in after['violations']}
    if new-old:reject('Cleanup introduced new DRC issues')
    summary={'accepted':True,'removed_uuids':sorted(set(remove)),'trimmed_uuids':sorted(set(trimmed)),
        'unconnected_before':len(before['unconnected_items']),
        'unconnected_after':len(after['unconnected_items']),'violations_before':len(before['violations']),
        'violations_after':len(after['violations'])}
    output.with_suffix('.cleanup.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--unused-vias',action='store_true');a=p.parse_args()
    if a.source.resolve()==a.output.resolve():p.error('Use a separate candidate output')
    clean(a.source,a.output,a.unused_vias)
