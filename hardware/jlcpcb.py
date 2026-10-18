# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Bundle checked JLCPCB fabrication files, without submitting an order or reserving parts."""
import hashlib
import json
import shutil
import tempfile
import zipfile
from .library import ROOT
from .circuit import COMPONENTS
from .design import BOARD_REVISION, MCU_PART
from .order_review import report as order_report
from .assembly_review import report as assembly_report, svg_guide


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    from .release import require_current_layout
    require_current_layout()
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
    from .panel import validate_gerber_inventory
    inventory=validate_gerber_inventory(source/'gerbers')
    with zipfile.ZipFile(source/'ch32-pico-panel-gerbers-PREVIEW.zip') as archive:
        if sorted(archive.namelist())!=inventory['files']:
            raise ValueError('Gerber archive contains stale or missing layers')
    parent = ROOT / 'build'
    destination = parent / 'jlcpcb'
    with tempfile.TemporaryDirectory(prefix='jlcpcb-', dir=parent) as temporary:
        out = ROOT / temporary
        files = {'gerbers.zip': 'ch32-pico-panel-gerbers-PREVIEW.zip',
                 'bom.csv': 'bom.csv', 'cpl.csv': 'cpl.csv'}
        for name, original in files.items():
            shutil.copyfile(source / original, out / name)
            if sha(out / name) != panel['file_sha256'][original]:
                raise ValueError(f'Fabrication file differs from checked panel: {name}')
        (out / 'assembly-orientation.json').write_text(json.dumps(assembly, indent=2) + '\n')
        (out / 'assembly-orientation.svg').write_text(svg_guide(assembly, board))
        (out / 'order-review.json').write_text(json.dumps(order, indent=2) + '\n')
        shutil.copyfile(ROOT / 'docs/factory-notes.txt', out / 'factory-notes.txt')
        (out / 'README.txt').write_text(
            f'ch32-pico Rev {BOARD_REVISION}: JLCPCB fabrication files; prototype, NOT an order release\n\n'
            'Extract this package first. Upload gerbers.zip to the PCB form.\n'
            'Use bom.csv and cpl.csv at the assembly upload step. Do not upload\n'
            'this entire fabrication bundle as a Gerber archive.\n\n'
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
            f'{assembly["panel_cpl_rows_checked"]} fitted placements per panel, '
            f'{assembly["panel_cpl_rows_checked"] * order["panels"]} across the batch.\n\n'
            'Review pin 1, polarity, USB mouth and centroids in JLC models using\n'
            'assembly-orientation.svg and its JSON coordinates. CPL angles apply\n'
            'reviewed JLC model-frame deltas (U1/D2 rotation, J2 anchor) and are\n'
            'normalized 0-360; confirm U1, D2, J2 and U4 in the JLC placement preview.\n'
            f'{order["total_boards"]} {MCU_PART} MCUs are fitted; stock is unallocated.\n'
            f'{supply_notice}'
            'Confirm all charged quantities and attrition in the factory quote.\n\n'
            'Read factory-notes.txt for stencil, silicon-lot, rail and polarity requirements.\n'
            'Enable Confirm Production file and Confirm Parts Placement in the quote.\n'
            'Include D5 hidden-joint X-ray inspection in the complete price.\n\n'
            'Confirm rail/tab handling, hybrid USB assembly, actual stackup,\n'
            'via pricing, castellations and the complete delivered price.\n'
            'The quote form may reset settings when other choices change.\n'
            'Physical USB, PD power, cable fit and native USB firmware qualification remain.\n'
            'Pin 40 is unswitched USB VBUS; no continuous current rating is qualified.\n'
            'Prototype qualification remains open: heat, loaded startup, transients, biased capacitance and low-input shutdown.\n'
            'No purchase, stock reservation or upload is performed by this build.\n')
        from scripts.license_files import copy_notices
        copy_notices(out)
        manifest = {
            'status': 'fabrication files checked locally; factory review and order release pending',
            'board_revision': BOARD_REVISION,
            'build_tool_sha256': {name:sha(ROOT/name) for name in
                ('justfile','pyproject.toml','uv.lock','.python-version',
                 'scripts/kikit-requirements.in','scripts/kikit-requirements.txt')},
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
    archive_path = parent / 'ch32-pico-jlcpcb.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(destination.rglob('*')):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(str(path.relative_to(destination)), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    print(f'JLCPCB fabrication files: {archive_path}; no upload or purchase')


if __name__ == '__main__':
    main()
