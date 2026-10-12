# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Build the cost-down probe from pinned open-source inputs; never flash a device."""
from pathlib import Path
import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
REVISION = "5524a833c656a6007fca9f6c947fd49ddcc16eb6"
FUN_REVISION = "1e4887e11d4bfa739ed5604524b69f5be9f9275b"
URL = "https://github.com/cnlohr/rv003usb.git"


def run(*args, **kwargs):
    return subprocess.check_output(args, text=True, **kwargs).strip()


def archive(source, destination):
    data = subprocess.check_output(["git", "-C", str(source), "archive", "HEAD"])
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as contents:
        contents.extractall(destination, filter="data")


def main():
    from hardware.design import BOARD_REVISION
    if BOARD_REVISION != 'A':
        raise SystemExit('This is the retained Rev A firmware generator. Rev B requires the X035 application/PD firmware.')
    source = ROOT / "build/references/rv003usb"
    if not source.exists():
        source.mkdir(parents=True)
        run("git", "-C", str(source), "init")
        run("git", "-C", str(source), "remote", "add", "origin", URL)
        run("git", "-C", str(source), "fetch", "--depth", "1", "origin", REVISION)
        run("git", "-C", str(source), "checkout", "--detach", REVISION)
    if run("git", "-C", str(source), "rev-parse", "HEAD") != REVISION:
        raise SystemExit("Unexpected rv003usb revision; refusing to replace checkout")
    run("git", "-C", str(source), "submodule", "update", "--init", "--depth", "1")
    for path, expected in ((source, REVISION), (source / "ch32fun", FUN_REVISION)):
        if run("git", "-C", str(path), "rev-parse", "HEAD") != expected:
            raise SystemExit(f"Unexpected revision: {path}")
        if run("git", "-C", str(path), "status", "--porcelain", "--untracked-files=no"):
            raise SystemExit(f"Modified dependency: {path}")
    prefix = os.environ.get("RISCV_PREFIX", str(ROOT / "build/toolchains/"
        "xpack-riscv-none-elf-gcc-14.2.0-3/bin/riscv-none-elf"))
    compiler = shutil.which(prefix + "-gcc")
    if not compiler:
        raise SystemExit("Set RISCV_PREFIX to a RISC-V compiler with rv32ec/ilp32e support")
    stage = ROOT / "build/lowcost-source"
    if stage.exists():
        shutil.rmtree(stage)  # Generated staging directory only; dependencies are untouched.
    archive(source, stage)
    archive(source / "ch32fun", stage / "ch32fun")
    patch = ROOT / "firmware/lowcost/board.patch"
    run("git", "apply", "--check", str(patch), cwd=stage)
    run("git", "apply", str(patch), cwd=stage)
    target = stage / "rvswdio_programmer"
    # Upstream's default target flashes hardware. Request only the binary.
    subprocess.run(["make", "-C", str(target), "rvswdio_programmer.bin", f"PREFIX={prefix}"], check=True)
    elf = target / "rvswdio_programmer.elf"
    size = run(prefix + "-size", str(elf)).splitlines()[-1].split()
    text_size, data_size, bss_size = map(int, size[:3])
    flash, ram = text_size + data_size, data_size + bss_size
    if flash > 16384 or ram > 2048:
        raise SystemExit(f"Probe exceeds CH32V003 memory: flash={flash}, static RAM={ram}")
    output = ROOT / "build/lowcost-probe"
    output.mkdir(exist_ok=True)
    for path,name in ((stage/'LICENSE','LICENSE-rv003usb'),
                      (stage/'ch32fun/LICENSE','LICENSE-ch32fun'),
                      (stage/'ch32fun/misc/LIBGCC_LICENSE','LICENSE-libgcc')):
        shutil.copy2(path,output/name)
    from license_files import copy_notices
    copy_notices(output)
    for suffix in ("bin", "elf", "hex"):
        p = target / f"rvswdio_programmer.{suffix}"
        if p.exists():
            shutil.copy2(p, output / f"probe.{suffix}")
    manifest = {
        "status": "compiled candidate; hardware USB and target programming unqualified",
        "rv003usb_revision": REVISION, "ch32fun_revision": FUN_REVISION,
        "patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
        "compiler": run(prefix + "-gcc", "--version").splitlines()[0],
        "flash_bytes": flash, "static_ram_bytes": ram,
        "ram_remaining_for_stack_bytes": 2048 - ram,
        "binary_sha256": hashlib.sha256((output / "probe.bin").read_bytes()).hexdigest(),
        "flashed": False,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
