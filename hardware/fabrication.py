# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Keep generated KiCad project and custom fabrication rules together."""
import shutil


def copy_rules(source,destination):
    for suffix in ('.kicad_pro','.kicad_dru'):
        src=source.with_suffix(suffix)
        if not src.exists():raise FileNotFoundError(f'Missing fabrication rules: {src}')
        shutil.copyfile(src,destination.with_suffix(suffix))
