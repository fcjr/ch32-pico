# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Render the checked board using hash-verified, locally cached part models."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hardware.sexp import parse, children, one, dump
from hardware.route_geometry import fingerprint


def main():
    from hardware.release import require_current_layout
    require_current_layout()
    manifest = json.loads((ROOT/'docs/render-models.json').read_text())
    models = manifest['models']
    cache = ROOT/'build/render/parts.3dshapes'
    if any(not (cache/m['file']).exists() for m in models.values()):
        subprocess.run(['easyeda2kicad', '--lcsc_id',
            *dict.fromkeys(m['lcsc'] for m in models.values()),
            '--footprint', '--3d', '--use-cache', '--overwrite',
            '--output', str(ROOT/'build/render/parts')], check=True)
    for m in models.values():
        if hashlib.sha256((cache/m['file']).read_bytes()).hexdigest() != m['sha256']:
            raise ValueError(f"Model changed upstream: {m['file']}. Review before updating its pin.")
    source = ROOT/'hardware/review/ch32-pico.kicad_pcb'
    checked = json.loads((source.parent/'validation.json').read_text())
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash != checked['board_sha256']:
        raise ValueError('Board changed since validation; run just review')
    doc = parse(source.read_text())
    copper = fingerprint(doc)
    count = 0
    for fp in children(doc, 'footprint'):
        name = fp[1].split(':')[-1]
        if name not in models:
            if name not in ('Pico_Header', 'TestPad_1mm', 'TestPad_0.6mm', 'SolderJumper_Open', 'USB_Probe_Inline'):
                raise ValueError(f'Missing model mapping: {name}')
            continue
        m = models[name]
        fp[:] = [n for n in fp if not (isinstance(n,list) and n[0]=='model')]
        fp.append(parse(f'''(model "{cache/m['file']}"
            (offset (xyz 0 {m['offset_y']} 0)) (scale (xyz 1 1 1))
            (rotate (xyz 0 0 {m['rotate_z']})))'''))
        count += 1
    from hardware.circuit import COMPONENTS
    assert count == sum(c.fitted for c in COMPONENTS) and fingerprint(doc) == copper
    from scripts.render_silkscreen import apply as plot_silkscreen
    silk_strokes=plot_silkscreen(doc,source,ROOT/'build/render')
    assert fingerprint(doc)==copper
    board = ROOT/'build/render/ch32-pico.kicad_pcb'
    board.write_text(dump(doc)+'\n')
    out = ROOT/'docs/images'
    out.mkdir(exist_ok=True)
    for name, rotation, side in [('ch32-pico-front','0,0,0','top'),
                                  ('ch32-pico-back','0,0,0','bottom')]:
        subprocess.run(['kicad-cli','pcb','render','--width','1000','--height','1600',
            '--quality','high','--background','opaque','--floor','--side',side,
            '--rotate',rotation,'--zoom','0.8','--output',str(out/(name+'.png')),
            str(board)],check=True)
    from PIL import Image, ImageDraw, ImageFont
    front = Image.open(out/'ch32-pico-front.png').convert('RGB')
    back = Image.open(out/'ch32-pico-back.png').convert('RGB')
    caption_height = 80
    combined = Image.new('RGB', (front.width + back.width, front.height + caption_height), '#f5f5f5')
    combined.paste(front, (0, caption_height))
    combined.paste(back, (front.width, caption_height))
    draw = ImageDraw.Draw(combined)
    font = ImageFont.load_default(size=30)
    from hardware.design import BOARD_REVISION
    for x, side in ((front.width//2, 'Front'), (front.width+back.width//2, 'Back')):
        draw.text((x, caption_height//2), f'{side} | ch32-pico Rev {BOARD_REVISION}',
                  fill='#242424', font=font, anchor='mm')
    combined.save(out/'ch32-pico.png', optimize=True)
    (out/'render.json').write_text(json.dumps({
        'source_board_sha256':source_hash, 'models_manifest':'../render-models.json',
        'fitted_models':count, 'tool':subprocess.check_output(['kicad-cli','version'],text=True).strip(),
        'purpose':'CAD illustration, not proof of physical or assembly fit',
        'silkscreen':'KiCad SVG strokes in disposable render copy', 'silkscreen_strokes':silk_strokes,
    },indent=2)+'\n')


if __name__ == '__main__':
    main()
