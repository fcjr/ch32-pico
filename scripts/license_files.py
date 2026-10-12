# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Keep original and upstream license notices with distributed outputs."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def copy_notices(destination):
    shutil.copy2(ROOT/'LICENSE', destination/'LICENSE')
    shutil.copytree(ROOT/'LICENSES', destination/'LICENSES', dirs_exist_ok=True)
    docs = destination/'docs'
    docs.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'docs/licensing.md', docs/'licensing.md')
