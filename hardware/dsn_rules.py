# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Apply the same routing rules to KiCad's DSN export as the native router."""
from pathlib import Path
from .sexp import parse,one,dump,Atom
from .design import MECHANICAL

# Short plane taps must fit 0402 and fine-pitch component pads. The scripted regulator
# paths remain wider. VBUS/VSYS current and drop still need release review.
# High-current VBUS/PD_OUT trunks are locked in the revision-specific critical_routes module; these
# widths apply only to sense/control-supply branches added by the router.
POWER_WIDTHS={'GND':.15,'3V3_OUT':.15,'VSYS':.25,'VBUS':.25,'PD_OUT':.25,'VIN_SYS':.35}


def configure(path):
    path=Path(path)
    doc=parse(path.read_text().replace('(string_quote ")','(string_quote QUOTE)'))
    one(one(one(doc,'structure'),'rule'),'width')[1]=Atom('150')
    # Specctra's ordinary 0.15 mm clearance also controls the routing outline.
    # Inset this rectangular ROUTING boundary by 0.325 mm to meet the
    # PCB's 0.30 mm edge rule even when the router grants no extra edge gap. SES imports copper only; Edge.Cuts stays intact.
    boundary=one(one(one(doc,'structure'),'boundary'),'path')
    xmax=MECHANICAL.width*1000-325;ymin=-MECHANICAL.length*1000+325
    boundary[:]=parse(f'(path pcb 0 {xmax:g} {ymin:g} 325 {ymin:g} 325 -325 {xmax:g} -325 {xmax:g} {ymin:g})')
    network=one(doc,'network');default=one(network,'class')
    default[:]=[x for x in default if isinstance(x,list) or x not in POWER_WIDTHS]
    one(one(default,'rule'),'width')[1]=Atom('150')
    for net,width in POWER_WIDTHS.items():
        network.append(parse(f'(class power_{net} {net} (circuit (use_via "Via[0-3]_450:200_um")) '
            f'(rule (width {width*1000:g}) (clearance 150)))'))
    path.write_text(dump(doc).replace('(string_quote QUOTE)','(string_quote ")')+'\n')


if __name__=='__main__':
    import sys
    configure(sys.argv[1])
