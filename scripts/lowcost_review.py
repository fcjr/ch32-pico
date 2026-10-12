# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Export the candidate net model and priced BOM without overwriting routed outputs."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import subprocess
from hardware.lowcost import COMPONENTS_LOWCOST,verify
from hardware.library import ROOT,load_library
from hardware.cost_review import report


def main():
    checks=verify()
    cost=report(components=COMPONENTS_LOWCOST)
    cost['status']='current circuit; not a factory quote'
    out=ROOT/'build/lowcost-review';out.mkdir(exist_ok=True)
    lib=load_library()
    (out/'circuit.json').write_text(json.dumps({c.ref:{'lcsc':lib[c.part].code,
        'mpn':lib[c.part].mpn,'fitted':c.fitted,'nets':c.nets,'note':c.note}
        for c in COMPONENTS_LOWCOST},indent=2)+'\n')
    (out/'cost.json').write_text(json.dumps(cost,indent=2)+'\n')
    (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    from hardware.schematic import generate
    from hardware.verify import verify_netlist
    sections={'power':'USB/5 V input and two 3.3 V LDOs',
              'usb':'USB-C low-speed HID, ESD and VBUS detection',
              'probe':'Open-source CH32V003 SWIO programmer',
              'target':'CH32V003 target and switched supply',
              'header':'Pico header positions and programming pads'}
    generate(components=COMPONENTS_LOWCOST,sections=sections,out=out,
             subtitle='CH32V003 target + open CH32V003 programmer',source='hardware/lowcost.py')
    subprocess.run(['kicad-cli','sch','erc','--exit-code-violations','--severity-all',
                    '--format','json','-o',str(out/'erc.json'),str(out/'ch32-pico.kicad_sch')],check=True)
    subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml',
                    '-o',str(out/'netlist.xml'),str(out/'ch32-pico.kicad_sch')],check=True)
    checks.update(verify_netlist(out/'netlist.xml',COMPONENTS_LOWCOST))
    (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps({**checks,'parts_per_board_usd':cost['parts_per_board_usd'],
        'parts_for_20_boards_usd':cost['parts_only_usd']},indent=2))


if __name__=='__main__':main()
