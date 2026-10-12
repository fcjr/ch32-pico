# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Fetch the portable, checksum-pinned Freerouting JAR into build/tools."""
from pathlib import Path
import hashlib
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
VERSION='2.5.0'
SHA256='f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7'
path=ROOT/f'build/tools/freerouting-{VERSION}.jar'
path.parent.mkdir(parents=True,exist_ok=True)
if not path.exists():
    data=urllib.request.urlopen(f'https://github.com/freerouting/freerouting/releases/download/v{VERSION}/{path.name}').read()
    if hashlib.sha256(data).hexdigest()!=SHA256:raise SystemExit('Downloaded router checksum mismatch')
    path.write_bytes(data)
if hashlib.sha256(path.read_bytes()).hexdigest()!=SHA256:raise SystemExit('Local router checksum mismatch')
print(f'Verified {path.name}')
