# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Offline, dated order planning. Never buys, reserves or assumes a JLC quote."""
import hashlib
import json
from collections import Counter
from .circuit import COMPONENTS
from .design import MCU_PART
from .cost_review import report as cost_report
from .library import ROOT, load_library
from .sexp import parse, children, one


def unit_price(part, quantity):
    tiers = [tier for tier in part['price_tiers_usd']
             if tier['minimum'] <= quantity
             and (tier['maximum'] < 0 or quantity <= tier['maximum'])]
    if len(tiers) != 1:
        raise ValueError(f'No unique price tier for {part["mpn"]} at {quantity}')
    return tiers[0]['unit_usd']


def prepurchase_candidate(part, required):
    """Compare actual total spend, including tier breaks above the minimum.

    Only a planning comparison: an empty-stock price is not an offer to supply.
    Ordinary assembly quantities must not inherit this pre-purchase MOQ.
    """
    minimum = max(required, part.get('minimum_prepurchase') or 0)
    options = {minimum} | {t['minimum'] for t in part['price_tiers_usd'] if t['minimum'] >= minimum}
    choices = [{'quantity': q, 'unit_usd': unit_price(part, q),
                'total_usd': round(q * unit_price(part, q), 4)} for q in options]
    return min(choices, key=lambda row: (row['total_usd'], row['quantity']))


def checked_board():
    board = ROOT / 'hardware/review/ch32-pico.kicad_pcb'
    saved = json.loads(board.with_name('validation.json').read_text())
    if hashlib.sha256(board.read_bytes()).hexdigest() != saved['board_sha256']:
        raise ValueError('Saved board changed since review')
    if not saved['checks']['passes_connectivity_and_drc']:
        raise ValueError('Saved board failed review')
    return board


def report(*, panels=None):
    if panels is not None and (type(panels) is not int or panels < 1):
        raise ValueError('Panel count must be a positive integer')
    source = json.loads((ROOT / 'hardware/procurement-observation.json').read_text())
    policy = json.loads((ROOT / 'hardware/jlc-assembly-policy.json').read_text())
    panel_path = ROOT / 'build/panel-preview'
    panel = json.loads((panel_path / 'manifest.json').read_text())
    board = checked_board()
    if not panel['passes'] or panel['source_board_sha256'] != hashlib.sha256(board.read_bytes()).hexdigest():
        raise ValueError('Panel is failed or stale')
    if panel['panel_sha256'] != hashlib.sha256((panel_path / 'ch32-pico-panel.kicad_pcb').read_bytes()).hexdigest():
        raise ValueError('Panel changed since validation')
    for filename, digest in panel['file_sha256'].items():
        if hashlib.sha256((panel_path / filename).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Panel artifact changed: {filename}')
    from .factory_checks import panel_tooling
    tooling = panel_tooling(parse((panel_path / 'ch32-pico-panel.kicad_pcb').read_text()))
    dimensions = panel['measured_outline_mm']
    if not all(lo <= v <= hi for lo, v, hi in zip(policy['standard_panel_minimum_mm'], dimensions,
                                                policy['standard_panel_maximum_mm'])):
        raise ValueError('Standard PCBA panel dimensions unsupported')
    panel_count = panel['panels'] if panels is None else panels
    boards = panel_count * panel['boards_per_panel']
    fitted = {c.ref: c for c in COMPONENTS if c.fitted}
    library = load_library()
    counts = Counter(c.part for c in fitted.values())
    rows = []
    for code, count in sorted(counts.items()):
        part = source['parts'][code]
        if not part.get('exact_mpn_match') or part.get('mpn') != library[code].mpn:
            raise ValueError(f'Unverified procurement record: {code}')
        used = count * boards
        loss, minimum = part['reported_attrition'], part['reported_assembly_minimum']
        if not isinstance(loss, int) or not isinstance(minimum, int) or min(loss, minimum) < 0:
            raise ValueError(f'Unknown attrition fields: {code}')
        # Public lossNumber is a displayed count, not a confirmed order formula.
        # This scenario adds it once per C-code for the entire batch. It is
        # explicitly provisional; never silently mark order attrition verified.
        planned = max(used + loss, minimum)
        rows.append({'lcsc': code, 'mpn': part['mpn'], 'fitted_quantity': used,
                     'references_per_board': sorted(c.ref for c in fitted.values() if c.part == code),
                     'displayed_loss_count': loss, 'displayed_assembly_minimum': minimum,
                     'provisional_quantity': planned,
                     'provisional_cost_usd': round(planned * unit_price(part, planned), 4),
                     'public_stock': part['jlc_reported_stock'],
                     'stock_shortfall': max(0, planned - part['jlc_reported_stock'])})
    # Count physical lands, not symbol pins: USB merged power lands and switch
    # terminals make electrical pin counts different from solder-joint counts.
    smd = pth = 0
    for fp in children(parse(board.read_text()), 'footprint'):
        ref = next(p[2] for p in children(fp, 'property') if p[1] == 'Reference')
        if ref not in fitted:
            continue
        # L-shaped terminals can contain several overlapping copper pads.
        # Paste-only apertures are stencil geometry, not extra solder joints.
        terminals={(pad[1],pad[2]) for pad in children(fp,'pad') if pad[1]}
        smd += sum(kind=='smd' for _,kind in terminals)
        pth += sum(kind=='thru_hole' for _,kind in terminals)
    fees = {
        'single_side_setup': policy['standard_single_side_setup_usd'],
        'single_side_stencil': policy['standard_single_side_stencil_usd'],
        'feeders_all_part_types': round(len(counts) * policy['standard_feeder_per_part_type_usd'], 4),
        'smt_lands_scenario': round(smd * boards * policy['smt_per_joint_usd'], 4),
    }
    parts = round(sum(row['provisional_cost_usd'] for row in rows), 4)
    partial = round(parts + sum(fees.values()), 4)
    return {
        'status': 'offline planning scenario; not a quote or order release',
        'observed_utc': source['observed_utc'], 'policy': policy,
        'panels': panel_count, 'boards_per_panel': panel['boards_per_panel'], 'total_boards': boards,
        'panel_size_mm': dimensions, 'assembly_service': 'Standard', 'economic_eligible': False,
        'factory_tooling_review': tooling,
        'reason': 'Pico castellations retained; JLC Economic PCBA excludes castellated holes.',
        'source_board_sha256': panel['source_board_sha256'], 'panel_sha256': panel['panel_sha256'],
        'parts_fitted_only_usd': cost_report(panels=panel_count,
            boards_per_panel=panel['boards_per_panel'], source=source)['parts_only_usd'],
        'parts_with_provisional_attrition_usd': parts, 'assembly_fee_scenario_usd': fees,
        'partial_batch_scenario_usd': partial, 'partial_per_board_scenario_usd': round(partial / boards, 4),
        'physical_smd_lands_per_board': smd, 'physical_pth_lands_per_board': pth,
        'conditional_manual_usb_scenario_usd': round(pth * boards * policy['manual_per_joint_usd']
                                                  + policy['manual_labor_per_order_usd'], 4),
        'conditional_fixtures_usd': policy['conditional_two_rigid_fixtures_usd'],
        'not_in_partial_total': ['PCB fabrication including castellations and ENIG',
            'Actual JLC joint counting, USB insertion/shell soldering and fixtures',
            'Required X-ray inspection of D5 hidden joints, packing, handling/panel/storage/review fees, shipping and tax',
            'Actual sourcing quote, purchase minimums and order-specific attrition'],
        'attrition_assumption': 'max(fitted quantity + displayed loss count, displayed assembly minimum), per C-code per batch',
        'attrition_verified_for_order': False, 'assembly_rotations_verified': False,
        'mcu_prepurchase_candidate': prepurchase_candidate(source['parts'][MCU_PART],
            next(r['provisional_quantity'] for r in rows if r['lcsc'] == MCU_PART)),
        'mcu_allocation_confirmed': False, 'rows': rows,
        'public_stock_sufficient_for_batch': not any(row['stock_shortfall'] for row in rows),
        'parts_with_shortfalls': [row['lcsc'] for row in rows if row['stock_shortfall']],
    }


def main():
    from .release import require_current_layout
    require_current_layout()
    result = report()
    out = ROOT / 'build/order-review'; out.mkdir(exist_ok=True)
    (out / 'order-review.json').write_text(json.dumps(result, indent=2) + '\n')
    scenarios = [report(panels=n) for n in (5, 25)]
    (out / 'batch-scenarios.json').write_text(json.dumps({
        'status': '20/100-board planning comparison; no order or quantity change',
        'scenarios': scenarios}, indent=2) + '\n')
    print(f"Standard PCBA required; {result['total_boards']} boards")
    print(f"Partial planning scenario: ${result['partial_batch_scenario_usd']:.2f}/batch; "
          f"${result['partial_per_board_scenario_usd']:.2f}/board BEFORE PCB and other exclusions")
    print('MCU pre-purchase candidate (availability unconfirmed):', result['mcu_prepurchase_candidate'])


if __name__ == '__main__':
    main()
