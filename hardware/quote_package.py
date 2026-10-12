# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Bundle verified quote inputs, without submitting an order or reserving parts."""
import hashlib
import json
import shutil
import tempfile
import zipfile
from .library import ROOT
from .order_review import report as order_report
from .assembly_review import report as assembly_report, svg_guide


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # These checks reject stale panel/source hashes, changed fabrication files,
    # missing fitted references and changed CPL coordinates or rotations.
    order = order_report()
    assembly, board = assembly_report()
    if order['panel_sha256'] != assembly['panel_sha256']:
        raise ValueError('Cost and assembly reviews refer to different panels')
    shortages = [row for row in order['rows'] if row['stock_shortfall']]
    supply_notice = ''.join(
        f"Supply shortfall: {row['lcsc']} {row['mpn']}, "
        f"{row['stock_shortfall']} pieces below the provisional requirement.\n"
        for row in shortages)
    if shortages:
        supply_notice += 'Source exact parts or validate replacements before release.\n'
    source = ROOT / 'build/panel-preview'
    panel = json.loads((source / 'manifest.json').read_text())
    parent = ROOT / 'build'
    destination = parent / 'quote-package'
    with tempfile.TemporaryDirectory(prefix='quote-package-', dir=parent) as temporary:
        out = ROOT / temporary
        files = {'gerbers.zip': 'ch32-pico-panel-gerbers-PREVIEW.zip',
                 'bom.csv': 'bom.csv', 'cpl.csv': 'cpl.csv'}
        for name, original in files.items():
            shutil.copyfile(source / original, out / name)
            if sha(out / name) != panel['file_sha256'][original]:
                raise ValueError(f'Quote file differs from checked panel: {name}')
        (out / 'assembly-orientation.json').write_text(json.dumps(assembly, indent=2) + '\n')
        (out / 'assembly-orientation.svg').write_text(svg_guide(assembly, board))
        (out / 'order-review.json').write_text(json.dumps(order, indent=2) + '\n')
        (out / 'README.txt').write_text(
            'ch32-pico: quote review package, NOT an order release\n\n'
            'Extract this package first. Upload gerbers.zip to the PCB form.\n'
            'Use bom.csv and cpl.csv at the assembly upload step. Do not upload\n'
            'this entire review package as a Gerber archive.\n\n'
            'Quantity: FIVE customer-supplied panels, each FOUR identical boards.\n'
            'Panel: 93 x 71 mm; one design; four columns, one row.\n'
            'Do not request an additional panelization.\n'
            'PCB: four layers, 1.0 mm, green, white silkscreen, ENIG 1 microinch.\n'
            'Copper: outer 1 oz, inner 0.5 oz; stackup JLC04101H-3313.\n'
            'Castellations: required on both long edges of EVERY board copy.\n'
            'All vias: 0.45 mm copper diameter, 0.20 mm drill.\n'
            'Confirm standard multilayer via pricing for those actual sizes.\n'
            'No filled/capped via-in-pad; no controlled-impedance certification.\n'
            'Assembly: Standard PCBA, top side, all five panels.\n'
            '132 fitted placements per panel, 660 across the batch.\n\n'
            'Review pin 1, polarity, USB mouth and centroids in JLC models using\n'
            'assembly-orientation.svg and its JSON coordinates. CPL angles are\n'
            'KiCad angles; JLC model offsets remain unverified.\n'
            'Forty C5187096 MCUs are fitted. Confirm allocation; public price\n'
            'tiers favor requesting 50, but stock is unallocated.\n'
            f'{supply_notice}'
            'Confirm all charged quantities and attrition in the factory quote.\n\n'
            'Confirm rail/tab handling, hybrid USB assembly, actual stackup,\n'
            'via pricing, castellations and the complete delivered price.\n'
            'The quote form may reset settings when other choices change.\n'
            'Physical USB, power, cable-fit and programmer qualification remain.\n'
            'No purchase, stock reservation or upload is performed by this build.\n')
        from scripts.license_files import copy_notices
        copy_notices(out)
        manifest = {
            'status': 'quote inputs checked locally; factory review and order release pending',
            'source_board_sha256': order['source_board_sha256'],
            'panel_sha256': order['panel_sha256'],
            'panels': order['panels'], 'boards_per_panel': order['boards_per_panel'],
            'assembly_rotations_verified': False, 'mcu_allocation_confirmed': False,
            'all_parts_allocated': False,
            'public_stock_shortfalls': shortages,
            'file_sha256': {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*')) if p.is_file()},
        }
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(out, destination)
    archive_path = parent / 'ch32-pico-QUOTE-REVIEW.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(destination.rglob('*')):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(str(path.relative_to(destination)), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    print(f'Quote review package: {archive_path}; no upload or purchase')


if __name__ == '__main__':
    main()
