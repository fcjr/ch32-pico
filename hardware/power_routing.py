# SPDX-License-Identifier: MIT
"""Replay the reviewed layout delta over its pinned base, then run independent checks.

The delta includes the pinned router's copper and manual DRC corrections.
It is a deterministic layout checkpoint, not a claim of thermal qualification.
"""
import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from .library import ROOT
from .sexp import parse, dump, children, Atom
from .fabrication import copy_rules
from .routing import grade

BASE='461bf67'
BASE_PATH='hardware/review/ch32-pico.kicad_pcb'
PATCH=ROOT/'hardware/research/power-route-patch.json'


def normalized(text):
    doc=parse(text)
    for zone in children(doc,'zone'):
        zone[:]=[n for n in zone if not (isinstance(n,list) and n[0] in ('filled_polygon','fill_segments'))]
    return doc


def entries(doc):
    return Counter(dump(n) if isinstance(n,list) else str(n) for n in doc[1:])


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def apply_delta(base,patch):
    if digest(base)!=patch['base_sha256']:
        raise ValueError('Power-routing base differs from the pinned checkpoint')
    remaining=entries(normalized(base))
    for text,count in patch['remove'].items():
        if remaining[text]<count:raise ValueError('Missing node in power-routing base')
        remaining[text]-=count
    remaining+=Counter(patch['add'])
    nodes=[parse(text) for text,count in sorted(remaining.items()) for _ in range(count)]
    prefix=('version','generator','generator_version','general','paper','layers','setup','net')
    nodes.sort(key=lambda n:prefix.index(n[0]) if isinstance(n,list) and n[0] in prefix else len(prefix))
    return [Atom('kicad_pcb'),*nodes]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',type=Path,help='Record a reviewed board as the deterministic delta')
    args=parser.parse_args()
    base=subprocess.check_output(['git','show',f'{BASE}:{BASE_PATH}'],cwd=ROOT,text=True)
    if args.capture:
        before,after=entries(normalized(base)),entries(normalized(args.capture.read_text()))
        patch={'base_commit':BASE,'base_path':BASE_PATH,'base_sha256':digest(base),
               'status':'four-layer direct-VBUS layout; geometry checked, physical qualification and order release remain open',
               'remove':dict(before-after),'add':dict(after-before)}
        PATCH.write_text(json.dumps(patch,indent=2)+'\n')
        assert entries(apply_delta(base,patch))==after
        return
    patch=json.loads(PATCH.read_text())
    if (patch['base_commit'],patch['base_path'])!=(BASE,BASE_PATH):
        raise ValueError('Unexpected power-routing baseline')
    out=ROOT/'build/routing';out.mkdir(parents=True,exist_ok=True)
    board=out/'power-corrected.kicad_pcb'
    board.write_text(dump(apply_delta(base,patch))+'\n')
    copy_rules(ROOT/'build/ch32-pico-seed.kicad_pcb',board)
    result=grade(board)
    (out/'comparison.json').write_text(json.dumps({'status':patch['status'],
        'candidates':{'power-corrected':result}},indent=2)+'\n')
    if not result['passes_connectivity_and_drc']:raise SystemExit('Power checkpoint failed independent checks')
    print('Power checkpoint passes geometry checks; no current rating or order release assigned')


if __name__=='__main__':main()
