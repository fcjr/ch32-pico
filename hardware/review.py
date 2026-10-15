# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Save a checked routing checkpoint for review; never create an order ZIP."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime,timezone
from .library import ROOT
from .routing import grade
from .fabrication import copy_rules
from .verify import verify_contract,verify_netlist
from .mechanical_checks import usb_fit
from .sexp import parse


def main():
    run=ROOT/'build/routing'
    comparison=json.loads((run/'comparison.json').read_text())
    passing=[name for name,result in comparison['candidates'].items() if result['passes_connectivity_and_drc']]
    if not passing:raise SystemExit('No passing route to save')
    # Regrade passing candidates against the current source, then prefer fewer
    # vias and shorter copper. All electrical gates take priority over cost.
    from .branding import update as update_branding
    from .markings import update as update_markings
    for name in passing:
        update_markings(run/(name+'.kicad_pcb'))
        update_branding(run/(name+'.kicad_pcb'))
    candidates={name:grade(run/(name+'.kicad_pcb')) for name in passing}
    passing=[name for name,result in candidates.items() if result['passes_connectivity_and_drc']]
    if not passing:raise SystemExit('Previously passing routes no longer match source')
    engine=min(passing,key=lambda name:(candidates[name]['via_count'],candidates[name]['trace_length_mm'],name))
    source=run/(engine+'.kicad_pcb')
    verify_contract();verify_netlist(ROOT/'build/ch32-pico.net.xml')
    erc=json.loads((ROOT/'build/electrical-erc.json').read_text())
    if any(sheet['violations'] for sheet in erc['sheets']):raise SystemExit('ERC is not clean')
    checked=grade(source)
    if not checked['passes_connectivity_and_drc']:raise SystemExit('Selected route no longer passes')
    directory=ROOT/'hardware/review';directory.mkdir(exist_ok=True)
    board=directory/'ch32-pico.kicad_pcb'
    shutil.copyfile(source,board);copy_rules(source,board)
    (directory/'fp-lib-table').write_text((run/'fp-lib-table').read_text().replace(
        '${KIPRJMOD}/../../hardware/lib','${KIPRJMOD}/../lib'))
    saved=grade(board)
    if not saved['passes_connectivity_and_drc']:raise SystemExit('Saved checkpoint failed its checks')
    report={'status':'routing checked; not released for ordering','saved_at':datetime.now(timezone.utc).isoformat(),
        'engine':engine,'selection':'passing DRC/connectivity, then minimum vias and trace length',
        'checks':saved,'board_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),
        'comparison':comparison,'usb_mechanical_fit':usb_fit(parse(board.read_text())), 'open_reviews':[
            'Cost-reduced MX26631 protection stage, 3 A input target and top-side-only assembly require assembled-board qualification; 3.64 A nominal eFuse threshold is not a continuous current rating',
            'Inductive loads require an external driver and local suppression; 5 V 24BYJ48 example is not rated for higher PD voltages',
            'Biased capacitance, input inrush, loaded startup and 5 V cable-loss shutdown require measurements; nominal startup threshold is 4.76 V',
            'Current PCB/assembly quote, MCU stock and 20-device allocation (docs/revision-e.md)',
            'Measured USB performance; nonuniform connector/package fanouts (docs/usb-routing.md)',
            'Physical USB cable, overhang and locating-peg fit (docs/revision-e.md)',
            'Pin 37 shutdown/restart, released EN voltage, back-power and loaded PD shutdown timing',
            'Power copper/contact temperature, current-limit tolerance, discharge, backfeed and fixed 3.3 V load budget; reserve at least 100 mA from the negotiated input current',
            'Native USB ISP/recovery, open PD/CDC firmware integration, reset/detach handling and watchdog',
            'JLC IC/diode polarity and stencil review, provisional 0.125 mm stencil with 78 percent exposed-pad paste coverage; supplier process approval pending, order quantity/attrition']}
    (directory/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    for name,layers,extra in [('front','F.Cu,F.SilkS,Edge.Cuts',[]),
                              ('back','B.Cu,B.SilkS,Edge.Cuts',['--mirror']),
                              ('ground','In1.Cu,Edge.Cuts',[]),
                              ('power','In2.Cu,Edge.Cuts',[])]:
        subprocess.run(['kicad-cli','pcb','export','svg','--mode-single','--layers',layers,
            '--fit-page-to-board','--exclude-drawing-sheet',*extra,'-o',str(directory/(name+'.svg')),str(board)],check=True)
        svg=directory/(name+'.svg')
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    print(f'Saved review checkpoint to {directory}; no fabrication release created')


if __name__=='__main__':main()
