# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""KiKit four-board prototype panel; no order submission."""
import csv
import zipfile
from collections import defaultdict
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from .library import ROOT,load_library
from .circuit import COMPONENTS
from .placement import PLACEMENT
from .manufacturing import LAYERS
from .jlc_model_frames import cpl_adjustment
from .sexp import parse,children,one,Atom
from .route_geometry import fingerprint
from .usb_review import pad_centers

PANELS=5
COPIES=4
KIKIT_VERSION='1.8.1'
OPTIONS={
    'layout':'grid; rows: 1; cols: 4; space: 3mm; renameref: B{n}_{orig}; renamenet: B{n}_{orig}',
    'tabs':f'plugin; code: {ROOT / "scripts/panel_tabs.py"}.EdgeTabs',
    'cuts':'mousebites; drill: 0.5mm; spacing: 0.8mm; offset: -0.2mm; prolong: 0.5mm',
    'framing':'railstb; width: 7mm; space: 3mm',
    # Standard PCBA process-edge guidance, reviewed 2026-10-13. The 1.152 mm
    # tooling example applies to Economic; use 2 mm on these supplied rails.
    'tooling':'3hole; hoffset: 2.5mm; voffset: 3.5mm; size: 2mm',
    # Leave 3.5 mm beyond the complete 2 mm mask opening to the outer edge.
    'fiducials':'3fid; hoffset: 7mm; voffset: 4.5mm; coppersize: 1mm; opening: 2mm',
    'post':'millradius: 1mm',
}


def validate_copies(source,panel):
    original=parse(source.read_text());doc=parse(panel.read_text())
    expected=pad_centers(original);actual=pad_centers(doc)
    refs={next(p[2] for p in children(fp,'property') if p[1]=='Reference'):fp for fp in children(doc,'footprint')}
    source_refs={next(p[2] for p in children(fp,'property') if p[1]=='Reference'):fp for fp in children(original,'footprint')}
    def terminal_map(fps):
        return {(ref,str(p[1]),tuple(map(float,one(p,'at')[1:3]))):one(p,'net')[-1] if children(p,'net') else None
                for ref,fp in fps.items() for p in children(fp,'pad') if p[1]}
    expected_nets=terminal_map(source_refs);results=[]
    def artwork(node, dx=0, dy=0):
        n=copy.deepcopy(node)
        n[:]=[v for v in n if not (isinstance(v,list) and v and v[0]=='uuid')]
        for key in ('at','start','end'):
            for point in children(n,key):
                point[1:3]=[Atom(str(round(float(point[1])-dx,5))),
                            Atom(str(round(float(point[2])-dy,5)))]
        def canonical(v):
            if isinstance(v,list):return tuple(canonical(x) for x in v)
            if isinstance(v,Atom):
                try:return round(float(v),5)
                except ValueError:pass
            return v
        return canonical(n)
    source_art=[n for kind in ('gr_text','gr_line') for n in children(original,kind)
                if one(n,'layer')[1] in ('F.SilkS','B.SilkS')]
    panel_art=[n for kind in ('gr_text','gr_line') for n in children(doc,kind)
               if one(n,'layer')[1] in ('F.SilkS','B.SilkS')]
    for i in range(COPIES):
        prefix=f'B{i}_';fps={ref[len(prefix):]:fp for ref,fp in refs.items() if ref.startswith(prefix)}
        if fps.keys()!=source_refs.keys():raise ValueError(f'Panel copy {i} has missing/extra footprints')
        a=one(source_refs['J1'],'at');b=one(fps['J1'],'at')
        dx,dy=float(b[1])-float(a[1]),float(b[2])-float(a[2])
        for ref,fp in fps.items():
            if list(one(fp,'at')[3:])!=list(one(source_refs[ref],'at')[3:]):raise ValueError('Unexpected panel rotation')
        for (ref,pin),point in expected.items():
            q=actual[prefix+ref,pin]
            if abs(q[0]-dx-point[0])>1e-5 or abs(q[1]-dy-point[1])>1e-5:raise ValueError('Panel pad moved')
        nets=terminal_map(fps)
        nets={k:(v[len(prefix):] if v and v.startswith(prefix) else v) for k,v in nets.items()}
        if nets!=expected_nets:raise ValueError('Panel pad net mismatch')
        copper=['kicad_pcb']
        for kind in ('segment','via'):
            for node in children(doc,kind):
                net=one(node,'net')[-1]
                if not net.startswith(prefix):continue
                n=copy.deepcopy(node);one(n,'net')[-1]=net[len(prefix):]
                for key in ('start','end') if kind=='segment' else ('at',):
                    point=one(n,key);point[1:3]=[Atom(f'{float(point[1])-dx:.6f}'),Atom(f'{float(point[2])-dy:.6f}')]
                copper.append(n)
        if fingerprint(copper)!=fingerprint(original):raise ValueError(f'Panel copy {i} changed trace/via geometry')
        translated=[artwork(n,dx,dy) for n in panel_art]
        if any(translated.count(artwork(n))!=1 for n in source_art):
            raise ValueError(f'Panel copy {i} changed silkscreen text or logo')
        results.append({'prefix':prefix,'translation_mm':[dx,dy],'physical_components':len(fps),
                        'pad_and_copper_parity':True,'silkscreen_parity':True,
                        'silkscreen_items':len(source_art)})
    return results


def assembly_files(board,out,copies):
    library=load_library();fitted={c.ref:c for c in COMPONENTS if c.fitted}
    expected={copy['prefix']+ref:(c,copy) for copy in copies for ref,c in fitted.items()}
    positions=out/'kicad-positions.csv'
    subprocess.run(['kicad-cli','pcb','export','pos','--format','csv','--units','mm','--side','both',
        '-o',str(positions),str(board)],check=True)
    rows={}
    with positions.open() as f:
        for row in csv.DictReader(f):
            ref=row['Ref']
            if ref not in expected:continue
            c,copy=expected[ref];x,y,angle=PLACEMENT[c.ref];dx,dy=copy['translation_mm']
            if abs(float(row['PosX'])-x-dx)>1e-5 or abs(float(row['PosY'])+y+dy)>1e-5:
                raise ValueError('Panel CPL position mismatch')
            if (float(row['Rot'])-angle)%360!=0 or row['Side']!='top':raise ValueError('Panel CPL orientation mismatch')
            if ref in rows:raise ValueError('Duplicate panel CPL reference')
            rows[ref]=row
    if rows.keys()!=expected.keys():raise ValueError('Panel CPL missing fitted parts')
    with (out/'cpl.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Designator','Mid X','Mid Y','Rotation','Layer'])
        for ref,(c,_) in sorted(expected.items()):
            row=rows[ref];_,_,angle=PLACEMENT[c.ref]
            rotation,dx,dy=cpl_adjustment(c.part,angle)
            w.writerow([ref,f"{float(row['PosX'])+dx:.6f}",f"{float(row['PosY'])+dy:.6f}",
                f"{rotation:.6f}",'top'])
    groups=defaultdict(list)
    for ref,(c,_) in expected.items():groups[c.part,c.value].append(ref)
    with (out/'bom.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Comment','Designator','Footprint','LCSC Part #','Quantity','Manufacturer','MPN'])
        for (code,value),refs in sorted(groups.items()):
            p=library[code];w.writerow([value or p.mpn,','.join(sorted(refs)),p.footprint,code,len(refs),p.manufacturer,p.mpn])
    return {'fitted_parts_per_panel':len(rows),'bom_rows':len(groups),'cpl_rows':len(rows),
            'rotation_status':'JLC model-frame deltas applied (U1/D2 rotation, J2 anchor); angles normalized 0-360; JLC preview confirmation pending'}


def main():
    from .release import require_current_layout
    require_current_layout()
    source=ROOT/'hardware/review/ch32-pico.kicad_pcb';out=ROOT/'build/panel-preview';out.mkdir(exist_ok=True)
    saved=json.loads((source.parent/'validation.json').read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest()!=saved['board_sha256']:
        raise ValueError('Saved source board hash changed')
    if not saved['checks']['passes_connectivity_and_drc']:raise ValueError('Source checkpoint failed')
    board=out/'ch32-pico-panel.kicad_pcb';python=ROOT/'build/kikit-venv/bin/python'
    version=subprocess.check_output([python,'-c','from importlib.metadata import version;print(version("kikit"))'],text=True).strip()
    if version!=KIKIT_VERSION:raise ValueError('KiKit version differs from pin')
    cmd=[python,ROOT/'scripts/kikit_cli.py','panelize']
    for key,value in OPTIONS.items():cmd.extend(['--'+key,value])
    cmd.extend([source,board])
    with (out/'kikit.log').open('w') as log:subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,check=True)
    # KiKit 1.8.1 replaces an unassigned Default netclass with KiCad's default
    # 0.20 mm. Restore the source's explicit 0.15 mm netclass for these copies.
    project=board.with_suffix('.kicad_pro');settings=json.loads(project.read_text())
    settings['net_settings']=json.loads(source.with_suffix('.kicad_pro').read_text())['net_settings']
    project.write_text(json.dumps(settings,indent=2)+'\n')
    (out/'fp-lib-table').write_text((source.parent/'fp-lib-table').read_text().replace(
        '${KIPRJMOD}/../lib',str(ROOT/'hardware/lib')))
    copies=validate_copies(source,board)
    drc=out/'drc.json'
    subprocess.run(['kicad-cli','pcb','drc','--refill-zones','--save-board','--format','json','-o',str(drc),str(board)],check=True)
    copies=validate_copies(source,board)
    fit=out/'usb-fit.json'
    subprocess.run([str(python),str(ROOT/'scripts/panel_fit.py'),str(board),str(fit)],check=True)
    doc=parse(board.read_text());points=[]
    for kind in ('gr_line','gr_arc'):
        for node in children(doc,kind):
            if one(node,'layer')[1]!='Edge.Cuts':continue
            for key in ('start','mid','end'):
                if children(node,key):points.append(tuple(map(float,one(node,key)[1:3])))
    dimensions=[max(p[i] for p in points)-min(p[i] for p in points) for i in (0,1)]
    if any(abs(a-b)>.01 for a,b in zip(dimensions,(93,71))):raise ValueError('Unexpected panel dimensions')
    if not all(70<=d<=250 for d in dimensions):raise ValueError('Panel outside Standard PCBA size limits')
    data=json.loads(drc.read_text());passed=not(data['violations'] or data['unconnected_items'])
    from .factory_checks import panel_tooling
    tooling_review=panel_tooling(doc)
    from .design import BOARD_REVISION
    report={'board_revision':BOARD_REVISION,'status':'panel preview; not released for ordering','kikit_version':version,'options':OPTIONS,
        'panels':PANELS,'boards_per_panel':COPIES,'total_boards':PANELS*COPIES,
        'nominal_size_mm':[93,71],'measured_outline_mm':dimensions,'source_board_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'panel_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),'copies':copies,
        'usb_overhang_fit':json.loads(fit.read_text()),
        'factory_tooling':tooling_review,
        'drc_violations':len(data['violations']),'unconnected':len(data['unconnected_items']),'passes':passed,
        'assembly_service':'Standard','economic_eligible':False,
        'economic_exclusion':'Castellated holes are unsupported by Economic PCBA.',
        'capabilities_source':'https://jlcpcb.com/capabilities/pcb-assembly-capabilities',
        'prototype_price_tier_confirmed':False,'assembly_rotations_verified':False,
        'notes':['Five panels means twenty complete boards and twenty BOMs before attrition.',
                 'Tabs only at short ends; castellated sides remain fully milled.',
                 'Top tab is offset left of USB-C; the final milled outline is checked against all four overhangs.',
                 'Mousebite break edges require flush trimming to restore the Pico envelope.',
                 'JLC must confirm tab strength, panel handling, castellations and final quote.']}
    if passed:
        report['assembly']=assembly_files(board,out,copies)
        gerbers=out/'gerbers';gerbers.mkdir(exist_ok=True)
        subprocess.run(['kicad-cli','pcb','export','gerbers','--layers',LAYERS,'--subtract-soldermask',
            '--check-zones','-o',str(gerbers)+'/',str(board)],check=True)
        subprocess.run(['kicad-cli','pcb','export','drill','--format','excellon','--excellon-separate-th',
            '--excellon-units','mm','--drill-origin','absolute','--excellon-oval-format','route',
            '-o',str(gerbers)+'/',str(board)],check=True)
        with zipfile.ZipFile(out/'ch32-pico-panel-gerbers-PREVIEW.zip','w',zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(gerbers.iterdir()):archive.write(path,path.name)
        report['file_sha256']={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in out.rglob('*') if p.is_file() and (p.suffix in ('.csv','.zip','.drl','.gbrjob') or p.parent==gerbers)}
    from scripts.license_files import copy_notices
    copy_notices(out)
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    subprocess.run(['kicad-cli','pcb','export','svg','--mode-single','--layers','F.Cu,F.SilkS,Edge.Cuts',
        '--fit-page-to-board','--exclude-drawing-sheet','-o',str(out/'front.svg'),str(board)],check=True)
    print(json.dumps(report,indent=2))
    if not passed:raise SystemExit('Panel DRC failed; preview retained for inspection')


if __name__=='__main__':main()
