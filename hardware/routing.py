# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Reproducible router comparison; processes exit normally, without timeouts.

Requires the pinned KiCadRoutingTools checkout and checksum-verified Freerouting
JAR. Each candidate gets independent KiCad DRC and source-net parity checks.
A router's successful process exit is never treated as a passed board.
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from .library import ROOT
from .verify_placement import verify_board
from .dsn_rules import configure,POWER_WIDTHS
from .assembly_checks import via_in_paste
from .sexp import parse,children,one
from .fabrication import copy_rules
from .route_cleanup import clean
from .route_geometry import fingerprint
from .routing_checks import unpreserved_segments,unpreserved_vias,outside_outline_copper
from .planes import add_planes

KRT_COMMIT='ad7f24deb8fbffa6c498a09a6ebda46e012c37ff'
JAR_SHA256='f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7'
KICAD_PYTHON='/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3'
KRT_ENV={'KICAD_RIP_PREEXISTING':'0'}


def run(command,log,env=None):
    started=time.monotonic()
    with log.open('w') as f:
        f.write(json.dumps(list(map(str,command)))+'\n');f.flush()
        if env:f.write('Environment overrides: '+json.dumps(env,sort_keys=True)+'\n');f.flush()
        result=subprocess.run(list(map(str,command)),cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,
            env=os.environ | (env or {}))
    elapsed=round(time.monotonic()-started,2)
    print(f'{log.name}: exit {result.returncode}, {elapsed}s',flush=True)
    if result.returncode: raise RuntimeError(f'Command failed; see {log}')
    return elapsed


def grade(path):
    report=path.with_suffix('.drc.json')
    run(['kicad-cli','pcb','drc','--severity-all','--refill-zones','--save-board',
        '--format','json','-o',report,path],path.with_suffix('.drc.log'))
    source_parity=verify_board(path)
    data=json.loads(report.read_text())
    result={'physical_components':source_parity,'source_pad_net_parity':True,
        'violations':len(data['violations']),'unconnected':len(data['unconnected_items']),
        'violation_types':dict(Counter(v['type'] for v in data['violations']))}
    doc=parse(path.read_text())
    from .routing_checks import stackup_matches
    placed=parse((ROOT/'build/ch32-pico-placed.kicad_pcb').read_text())
    result['stackup_matches_source']=stackup_matches(placed,doc)
    result['outside_outline_copper']=outside_outline_copper(doc)
    result['via_count']=len(children(doc,'via'))
    result['trace_length_mm']=round(sum(math.dist(
        tuple(map(float,one(t,'start')[1:3])),tuple(map(float,one(t,'end')[1:3])))
        for t in children(doc,'segment')),3)
    result['trace_via_geometry_sha256']=fingerprint(doc)
    result['via_in_paste']=via_in_paste(doc)
    seed=parse((ROOT/'build/ch32-pico-seed.kicad_pcb').read_text())
    result['changed_critical_segments']=unpreserved_segments(seed,doc)
    result['changed_critical_vias']=unpreserved_vias(seed,doc)
    result['foreign_tracks_on_ground_layer']=sum(1 for t in children(doc,'segment')
        if one(t,'layer')[1]=='In1.Cu' and one(t,'net')[-1]!='GND')
    from .ground_review import audit as ground_audit
    try:
        result['ground_plane']=ground_audit(doc)
        result['ground_plane_passes']=True
    except ValueError as error:
        result['ground_plane']={'error':str(error)}
        result['ground_plane_passes']=False
    from .usb_review import report as usb_report
    try:
        result['usb_geometry']=usb_report(path)
        result['usb_geometry_passes']=not result['usb_geometry']['ground_reference_sampling']['uncovered_sample_count']
    except ValueError as error:
        result['usb_geometry']={'error':str(error)}
        result['usb_geometry_passes']=False
    from .markings import audit as audit_markings
    try:
        result['silkscreen']=audit_markings(doc)
        result['silkscreen_passes']=True
    except ValueError as error:
        result['silkscreen']={'error':str(error)}
        result['silkscreen_passes']=False
    from .power_layout import audit as power_audit
    result['power_layout_passes']=True
    try:
        result['power_layout']=power_audit(doc)
    except ValueError as error:
        result['power_layout']={'error':str(error)}
        result['power_layout_passes']=False
    result['passes_connectivity_and_drc']=not (not result['stackup_matches_source'] or not result['power_layout_passes'] or not result['silkscreen_passes'] or result['violations'] or result['unconnected']
        or result['via_in_paste'] or not result['ground_plane_passes'] or result['outside_outline_copper']
        or result['changed_critical_segments'] or result['changed_critical_vias']
        or not result['usb_geometry_passes'])
    return result


def finish(raw,board):
    try:
        clean(raw,board,unused_vias=True)
    except ValueError as error:
        # Cleanup restores its input on rejection. Keep the failed candidate
        # reviewable and let the independent grade explain what remains.
        print(f'{board.name}: cleanup rejected: {error}',flush=True)
    return grade(board)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--krt',type=Path,default=Path.home()/'git/KiCadRoutingTools')
    p.add_argument('--kicad-python',default=KICAD_PYTHON)
    p.add_argument('--engine',choices=['both','krt','freerouting'],default='both')
    p.add_argument('--signal-layers',nargs='+',default=['F.Cu','In2.Cu','B.Cu'],
        choices=['F.Cu','In2.Cu','B.Cu'],help='In1.Cu remains the ground reference')
    a=p.parse_args()
    out=ROOT/'build/routing';out.mkdir(exist_ok=True)
    manifest={'status':'running','started_at':datetime.now(timezone.utc).isoformat(),
        'krt_commit':KRT_COMMIT,'krt_environment':KRT_ENV,'freerouting_version':'2.5.0',
        'signal_layers':a.signal_layers,'candidates':{},'fabrication_ready':False}
    def record(): (out/'comparison.json').write_text(json.dumps(manifest,indent=2)+'\n')
    def repair_planes(raw,name):
        # Signal routing can divide In2.Cu into disconnected 3V3 islands.
        # Reconnect those against KiCad's exact fill before final grading.
        repaired=out/(name+'-plane-repair.kicad_pcb')
        run([python,a.krt/'py_router/route.py',raw,repaired,'--nets','GND','3V3_OUT',
            '--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1','-1','3','3',
            '--track-width','.15','--power-nets','GND','3V3_OUT','--power-nets-widths','.15','.15',
            '--clearance','.15','--via-size','.45','--via-drill','.2','--grid-step','.05',
            '--no-stub-layer-swap','--same-net-pad-clearance','.1','--no-fix-drc-settings',
            '--keep-input-copper','--fab-overrides',ROOT/'hardware/fab-limits.txt',
            '--escalation','off','--max-iterations','300000','--max-ripup','3'],
            out/(name+'-plane-repair.log'),env=KRT_ENV)
        copy_rules(raw,repaired)
        return repaired
    record()
    (out/'fp-lib-table').write_text((ROOT/'build/fp-lib-table').read_text().replace(
        '${KIPRJMOD}/../hardware','${KIPRJMOD}/../../hardware'))
    seed=ROOT/'build/ch32-pico-seed.kicad_pcb'
    run([a.kicad_python,'-m','hardware.critical_routes'],out/'critical.log')
    if subprocess.check_output(['git','-C',a.krt,'rev-parse','HEAD'],text=True).strip()!=KRT_COMMIT:
        raise SystemExit('KiCadRoutingTools revision differs from the reviewed pin')
    if subprocess.check_output(['git','-C',a.krt,'status','--porcelain','--untracked-files=no'],text=True).strip():
        raise SystemExit('KiCadRoutingTools has tracked modifications')
    python=a.krt/'.venv/bin/python'
    input_board=out/'input.kicad_pcb'
    from .mcu_fanout import add_fanout
    fanout=out/'fanout.kicad_pcb'
    add_fanout(seed,fanout)
    add_planes(fanout,input_board)
    seed_grade=grade(input_board)
    manifest['seed']=seed_grade;record()
    # Unfinished pin exits may end in a track or via. Only these two warnings
    # are allowed before signal routing; final grading permits neither.
    if (seed_grade['changed_critical_segments'] or seed_grade['changed_critical_vias']
        or any(kind not in {'via_dangling','track_dangling'} for kind in seed_grade['violation_types'])):
        raise SystemExit('Critical-route DRC failed')
    # Weld supply pads to their planes before signals consume the escape space.
    taps=out/'plane-taps.kicad_pcb'
    run([python,a.krt/'py_router/route.py',input_board,taps,'--nets','GND','3V3_OUT',
        '--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1','-1','3','3',
        '--track-width','.15','--power-nets','GND','3V3_OUT','--power-nets-widths','.15','.15',
        '--clearance','.15','--via-size','.45','--via-drill','.2',
        '--grid-step','.05','--no-stub-layer-swap','--same-net-pad-clearance','.1','--no-fix-drc-settings',
        '--keep-input-copper','--fab-overrides',ROOT/'hardware/fab-limits.txt',
        '--escalation','off','--max-iterations','300000','--max-ripup','3'],out/'plane-taps.log',env=KRT_ENV)
    copy_rules(input_board,taps)
    routed_input=out/'prepared.kicad_pcb'
    clean(taps,routed_input)
    prepared_grade=grade(routed_input)
    data=json.loads(routed_input.with_suffix('.drc.json').read_text())
    if (prepared_grade['via_in_paste'] or prepared_grade['foreign_tracks_on_ground_layer']
        or prepared_grade['changed_critical_segments'] or prepared_grade['changed_critical_vias']
        or any(kind not in {'via_dangling','track_dangling'} for kind in prepared_grade['violation_types'])
        or any(any(f'[{net}]' in i['description'] for net in ('GND','3V3_OUT'))
               for violation in data['unconnected_items'] for i in violation['items'])):
        raise SystemExit('Power-plane connection stage failed; inspect plane-taps reports')
    input_board=routed_input
    manifest.update(input_sha256=hashlib.sha256(input_board.read_bytes()).hexdigest(),prepared=prepared_grade)
    record()
    if a.engine in ('both','krt'):
        board=out/'krt.kicad_pcb'
        raw=out/'krt-raw.kicad_pcb'
        copper_layers=['F.Cu','In1.Cu','In2.Cu','B.Cu']
        layer_costs=[('1' if layer=='F.Cu' else '3') if layer in a.signal_layers else '-1' for layer in copper_layers]
        duration=run([python,a.krt/'py_router/route.py',input_board,raw,'--nets','*',
            '--layers',*copper_layers,'--layer-costs',*layer_costs,'--track-width','.15','--power-nets',*POWER_WIDTHS,
            '--power-nets-widths',*map(str,POWER_WIDTHS.values()),'--clearance','.15',
            '--via-size','.45','--via-drill','.2','--grid-step','.05','--no-fix-drc-settings',
            '--same-net-pad-clearance','.1','--no-stub-layer-swap',
            '--keep-input-copper','--fab-overrides',ROOT/'hardware/fab-limits.txt',
            '--escalation','off','--max-iterations','500000','--max-ripup','5',
            '--ripup-blocker-select','mincut'],out/'krt.log',env=KRT_ENV)
        copy_rules(input_board,raw)
        manifest['candidates']['krt']={**finish(repair_planes(raw,'krt'),board),'seconds':duration};record()
    if a.engine in ('both','freerouting'):
        jar=ROOT/'build/tools/freerouting-2.5.0.jar'
        if not jar.exists() or hashlib.sha256(jar.read_bytes()).hexdigest()!=JAR_SHA256:
            raise SystemExit('Missing/checksum-mismatched Freerouting 2.5.0 JAR')
        dsn=out/'input.dsn';ses=out/'freerouting.ses';board=out/'freerouting.kicad_pcb'
        raw=out/'freerouting-raw.kicad_pcb'
        run([a.kicad_python,'-m','hardware.exchange','export',input_board,dsn,'--only-locked'],out/'dsn.log')
        configure(dsn)
        layers=','.join(str(layer in a.signal_layers).lower() for layer in ['F.Cu','In1.Cu','In2.Cu','B.Cu'])
        duration=run(['java','-jar',jar,'--user_data_path='+str(out/'freerouting-profile'),
            '--usage_and_diagnostic_data.disable_analytics=true','--gui.enabled=false',
            '--router.layers.routable='+layers,'--router.automatic_neckdown=false','--router.fanout.enabled=false',
            '--router.autorouter.max_passes=30','--router.optimizer.max_threads=1',
            '-de',dsn,'-do',ses],out/'freerouting.log')
        run([a.kicad_python,'-m','hardware.exchange','import',input_board,ses,'--output',raw,'--only-locked'],out/'ses.log')
        copy_rules(input_board,raw)
        manifest['candidates']['freerouting']={**finish(repair_planes(raw,'freerouting'),board),'seconds':duration};record()
    passed=any(c['passes_connectivity_and_drc'] for c in manifest['candidates'].values())
    manifest['status']='passed' if passed else 'failed';record()
    print(json.dumps(manifest,indent=2))
    if not passed:
        raise SystemExit('No routing candidate passes yet; no fabrication release produced')


if __name__=='__main__':
    try:main()
    except (Exception,SystemExit) as error:
        path=ROOT/'build/routing/comparison.json'
        if path.exists():
            result=json.loads(path.read_text());result.update(status='failed',error=str(error))
            path.write_text(json.dumps(result,indent=2)+'\n')
        raise
