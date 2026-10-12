# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Export a locally checked JLC manufacturing preview from the saved board.

Files are suitable for engineering review, not a production release. This
command never uploads an order or treats unreviewed placement angles as proven.
"""
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .circuit import COMPONENTS
from .design import BOARD_REVISION
from .fabrication import copy_rules
from .library import ROOT, load_library, validate_library
from .placement import PLACEMENT
from .power_review import report as power_report
from .routing import grade
from .verify import verify_contract, verify_netlist

LAYERS='F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refkey(ref):
    match=re.fullmatch(r'([A-Za-z]+)(\d+)',ref)
    if not match:raise ValueError(f'Unexpected physical reference {ref}')
    return match[1],int(match[2])


def assembly_files(positions, directory):
    library=load_library();validate_library(COMPONENTS,library)
    fitted={c.ref:c for c in COMPONENTS if c.fitted}
    rows={}
    with positions.open(newline='') as source:
        for row in csv.DictReader(source):
            ref=row['Ref']
            if ref not in fitted:continue
            if ref in rows:raise ValueError(f'Duplicate placement {ref}')
            x,y,angle=PLACEMENT[ref]
            if (not math.isclose(float(row['PosX']),x,abs_tol=1e-6)
                or not math.isclose(float(row['PosY']),-y,abs_tol=1e-6)
                or (float(row['Rot'])-angle)%360!=0 or row['Side']!='top'):
                raise ValueError(f'Unexpected position/orientation/side for {ref}')
            rows[ref]=row
    if rows.keys()!=fitted.keys():
        raise ValueError(f'Placement coverage mismatch: {rows.keys() ^ fitted.keys()}')
    groups=defaultdict(list)
    for c in fitted.values():groups[c.part,c.value].append(c.ref)
    with (directory/'bom.csv').open('w',newline='') as output:
        writer=csv.writer(output)
        writer.writerow(['Comment','Designator','Footprint','LCSC Part #','Quantity','Manufacturer','MPN'])
        for (code,value),refs in sorted(groups.items()):
            p=library[code]
            writer.writerow([value or p.mpn,','.join(sorted(refs,key=refkey)),p.footprint,
                code,len(refs),p.manufacturer,p.mpn])
    with (directory/'cpl.csv').open('w',newline='') as output:
        writer=csv.writer(output)
        writer.writerow(['Designator','Mid X','Mid Y','Rotation','Layer'])
        for ref,row in sorted(rows.items(),key=lambda item:refkey(item[0])):
            writer.writerow([ref,row['PosX'],row['PosY'],f"{float(row['Rot'])%360:.6f}",'top'])
    return {'fitted_parts':len(fitted),'bom_rows':len(groups),'cpl_rows':len(rows),
        'coordinate_units':'mm','origin':'KiCad absolute; X right, Y up; board occupies negative Y',
        'rotation_status':'KiCad footprint angles; JLC part orientation review pending'}


def export(directory):
    from .release import require_current_layout
    require_current_layout()
    review=ROOT/'hardware/review'
    saved=json.loads((review/'validation.json').read_text())
    original=review/'ch32-pico.kicad_pcb'
    if sha(original)!=saved['board_sha256']:raise ValueError('Saved board hash changed; run make review')
    verify_contract();verify_netlist(ROOT/'build/ch32-pico.net.xml')
    erc=json.loads((ROOT/'build/electrical-erc.json').read_text())
    if any(s['violations'] for s in erc['sheets']):raise ValueError('Schematic ERC failed')
    board=directory/'ch32-pico.kicad_pcb'
    shutil.copyfile(original,board);copy_rules(original,board)
    # The grade uses the current source seed, so stale saved critical routes fail.
    (directory/'fp-lib-table').write_text((review/'fp-lib-table').read_text().replace(
        '${KIPRJMOD}/../lib',str(ROOT/'hardware/lib')))
    checked=grade(board)
    if not checked['passes_connectivity_and_drc']:raise ValueError('Manufacturing preview board failed checks')
    gerbers=directory/'gerbers';gerbers.mkdir()
    def command(*args):subprocess.run(['kicad-cli',*map(str,args)],check=True)
    command('pcb','export','gerbers','--layers',LAYERS,'--subtract-soldermask',
        '--check-zones','-o',str(gerbers)+'/',board)
    command('pcb','export','drill','--format','excellon','--excellon-separate-th',
        '--excellon-units','mm','--drill-origin','absolute','--excellon-oval-format','route',
        '--generate-map','--map-format','svg','-o',str(gerbers)+'/',board)
    positions=directory/'kicad-positions.csv'
    command('pcb','export','pos','--format','csv','--units','mm','--side','both','-o',positions,board)
    assembly=assembly_files(positions,directory)
    # Archive only fabrication files. Keep review maps and reports beside it.
    with zipfile.ZipFile(directory/'ch32-pico-gerbers-PREVIEW.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(gerbers.iterdir()):
            if path.suffix=='.svg':continue
            info=zipfile.ZipInfo(path.name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,path.read_bytes())
    (directory/'README.txt').write_text(
        f'ch32-pico Rev {BOARD_REVISION} - MANUFACTURING PREVIEW, NOT RELEASED\n\n'
        '4 layers, 21 x 51 mm, 1.0 mm FR-4, ENIG.\n'
        'JLC04101H-3313, outer 1 oz / inner 0.5 oz.\n'
        'Castellated holes required. All vias 0.45/0.20 mm; confirm standard multilayer via pricing.\n'
        'Standard PCBA required: Economic PCBA does not support castellated holes.\n'
        'For assembly use the 93 x 71 mm four-copy panel, quantity five panels.\n'
        f'No filled/capped via-in-pad. Top-side assembly, {assembly["fitted_parts"]} fitted components.\n'
        'Retain upper mounting holes, but ordinary screw heads do not fit beside USB.\n'
        'CPL uses KiCad angles; verify every polarized part and IC in JLC preview.\n'
        'BOM/CPL reference coverage is checked. Stock and attrition are not reserved.\n'
        'Open engineering reviews are recorded in manifest.json. No order was uploaded.\n')
    from scripts.license_files import copy_notices
    copy_notices(directory)
    inputs=[p for folder in ('hardware','scripts','firmware') for p in (ROOT/folder).rglob('*')
        if p.is_file() and '__pycache__' not in p.parts and 'review' not in p.parts]
    inputs += [ROOT/'LICENSE', ROOT/'docs/licensing.md', *[p for p in (ROOT/'LICENSES').rglob('*') if p.is_file()]]
    manifest={'status':'manufacturing preview; not released for ordering','fabrication_ready':False,'board_revision':BOARD_REVISION,
        'created_at':datetime.now(timezone.utc).isoformat(),
        'kicad_version':subprocess.check_output(['kicad-cli','version'],text=True).strip(),
        'saved_board_sha256':sha(original),'export_board_sha256':sha(board),
        'checks':checked,'assembly':assembly,'open_reviews':saved['open_reviews'],
        'usb_mechanical_fit':saved['usb_mechanical_fit'],'power_estimates':power_report(),
        'jlc_stackup':json.loads((ROOT/'hardware/jlc-stackup.json').read_text()),
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)},
        'file_sha256':{str(p.relative_to(directory)):sha(p) for p in sorted(directory.rglob('*')) if p.is_file()}}
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


def main():
    parent=ROOT/'build';parent.mkdir(exist_ok=True)
    output=parent/'manufacturing-preview'
    # A failed export leaves the previous preview intact.
    with tempfile.TemporaryDirectory(prefix='manufacturing-',dir=parent) as temporary:
        directory=Path(temporary);export(directory)
        if output.exists():shutil.rmtree(output)
        shutil.copytree(directory,output)
    print(f'Manufacturing preview: {output}; no order submitted')


if __name__=='__main__':main()
