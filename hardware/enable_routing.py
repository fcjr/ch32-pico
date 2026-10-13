# SPDX-License-Identifier: MIT
"""Reproduce Rev D as a routed delta against the reviewed Rev C checkpoint.

The base lives in Git history. All existing copper is fixed during routing;
Freerouting is tried first, then the pinned native router on EN only if needed.
Independent KiCad checks and a geometry comparison must accept the result.
Native processes finish normally; no timeout or forced termination is used.
"""
import hashlib
import json
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from .library import ROOT
from .sexp import parse, children, one, dump
from .fabrication import copy_rules
from .route_geometry import fingerprint
from .routing import KICAD_PYTHON, JAR_SHA256, KRT_COMMIT, KRT_ENV, run, grade
from .dsn_rules import configure
from .verify_placement import verify_board

BASE_COMMIT = 'bc6a81c30042df2f5b68877804356c6cafcf8f97'
BASE_SHA256 = '602be0ada4b9b8e9348ec9adfb7246414cd58fc729e9fd606f33f0d4b5423429'


def add_enable(doc):
    changed = []
    for fp in children(doc, 'footprint'):
        ref = next(p[2] for p in children(fp, 'property') if p[1] == 'Reference')
        for pad in children(fp, 'pad'):
            if (ref, pad[1]) not in {('J1', '37'), ('U4', '2')}:
                continue
            if children(pad, 'net'):
                raise ValueError('Expected the Rev C unconnected EN terminals')
            pad.append(parse('(net "3V3_EN")'))
            changed.append((ref, pad[1]))
    if sorted(changed) != [('J1', '37'), ('J1', '37'), ('U4', '2')]:
        raise ValueError('Expected header hole, castellation and regulator EN')
    from .markings import apply as markings
    from .branding import apply as branding
    markings(doc)
    branding(doc)


def old_copper(doc):
    doc = deepcopy(doc)
    doc[:] = [n for n in doc if not (isinstance(n, list) and n[0] in ('segment', 'via')
              and one(n, 'net')[-1] == '3V3_EN')]
    return fingerprint(doc)


def main():
    from .design import BOARD_REVISION
    if BOARD_REVISION != 'D':
        raise ValueError('This migration applies to Rev D only')
    out = ROOT / 'build/routing'
    out.mkdir(exist_ok=True)
    base = subprocess.check_output(['git', 'show', f'{BASE_COMMIT}:hardware/review/ch32-pico.kicad_pcb'], cwd=ROOT)
    if hashlib.sha256(base).hexdigest() != BASE_SHA256:
        raise ValueError('Rev C checkpoint hash mismatch')
    doc = parse(base.decode())
    baseline = fingerprint(doc)
    add_enable(doc)
    source = out / 'enable-input.kicad_pcb'
    source.write_text(dump(doc) + '\n')
    copy_rules(ROOT / 'build/ch32-pico-placed.kicad_pcb', source)
    (out / 'fp-lib-table').write_text((ROOT / 'build/fp-lib-table').read_text().replace(
        '${KIPRJMOD}/../hardware', '${KIPRJMOD}/../../hardware'))
    verify_board(source)
    initial = grade(source)
    if initial['violations'] or not initial['unconnected']:
        raise ValueError('Expected only unrouted EN before routing')
    if any(any('[3V3_EN]' not in item['description'] for item in issue['items'])
           for issue in json.loads(source.with_suffix('.drc.json').read_text())['unconnected_items']):
        raise ValueError('Unexpected non-EN open connection')
    jar = ROOT / 'build/tools/freerouting-2.5.0.jar'
    if hashlib.sha256(jar.read_bytes()).hexdigest() != JAR_SHA256:
        raise ValueError('Freerouting checksum mismatch')
    dsn, ses = out / 'enable.dsn', out / 'enable.ses'
    target = out / 'freerouting-enable.kicad_pcb'
    run([KICAD_PYTHON, '-m', 'hardware.exchange', 'export', source, dsn], out / 'enable-export.log')
    configure(dsn)
    duration = run(['java', '-jar', jar, '--user_data_path=' + str(out / 'freerouting-profile'),
        '--usage_and_diagnostic_data.disable_analytics=true', '--gui.enabled=false',
        '--router.layers.routable=true,false,true,true', '--router.automatic_neckdown=false',
        '--router.fanout.enabled=false', '--router.autorouter.max_passes=30',
        '--router.optimizer.max_threads=1', '-de', dsn, '-do', ses], out / 'enable-freerouting.log')
    run([KICAD_PYTHON, '-m', 'hardware.exchange', 'import', source, ses, '--output', target], out / 'enable-import.log')
    copy_rules(source, target)
    result = grade(target)
    if old_copper(parse(target.read_text())) != baseline:
        raise ValueError('Router changed pre-existing Rev C copper')
    result.update(seconds=duration, preexisting_copper_preserved=True)
    candidates = {'freerouting-enable': result}
    if not result['passes_connectivity_and_drc']:
        krt = Path.home() / 'git/KiCadRoutingTools'
        if subprocess.check_output(['git', '-C', krt, 'rev-parse', 'HEAD'], text=True).strip() != KRT_COMMIT:
            raise ValueError('KiCadRoutingTools revision differs from the reviewed pin')
        if subprocess.check_output(['git', '-C', krt, 'status', '--porcelain', '--untracked-files=no'], text=True).strip():
            raise ValueError('KiCadRoutingTools has tracked modifications')
        target = out / 'krt-enable.kicad_pcb'
        duration = run([krt / '.venv/bin/python', krt / 'py_router/route.py', source, target,
            '--nets', '3V3_EN', '--layers', 'F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu',
            '--layer-costs', '1', '-1', '3', '3', '--track-width', '.15',
            '--clearance', '.15', '--via-size', '.45', '--via-drill', '.2',
            '--grid-step', '.05', '--no-fix-drc-settings', '--same-net-pad-clearance', '.1',
            '--no-stub-layer-swap', '--keep-input-copper',
            '--fab-overrides', ROOT / 'hardware/fab-limits.txt',
            '--escalation', 'off', '--max-iterations', '500000', '--max-ripup', '0'],
            out / 'enable-krt.log', env=KRT_ENV)
        copy_rules(source, target)
        result = grade(target)
        if old_copper(parse(target.read_text())) != baseline:
            raise ValueError('KRT changed pre-existing Rev C copper')
        result.update(seconds=duration, preexisting_copper_preserved=True)
        candidates['krt-enable'] = result
    manifest = {'status': 'passed' if result['passes_connectivity_and_drc'] else 'failed',
        'started_at': datetime.now(timezone.utc).isoformat(), 'freerouting_version': '2.5.0',
        'base_commit': BASE_COMMIT, 'base_board_sha256': BASE_SHA256,
        'operation': 'Add EN route only; all previous copper fixed',
        'krt_commit': KRT_COMMIT, 'candidates': candidates, 'fabrication_ready': False}
    (out / 'comparison.json').write_text(json.dumps(manifest, indent=2) + '\n')
    if not result['passes_connectivity_and_drc']:
        raise ValueError('EN route failed independent checks')
    print('Rev D EN route passed; all pre-existing copper preserved')


if __name__ == '__main__':
    main()
