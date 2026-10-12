# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Fetch pinned PicoRVD sources for an optional external factory-flashing probe.

These are not dependencies of the onboard CH32V003 programmer; that build
uses scripts/lowcost_firmware.py. Never uses vendor firmware blobs."""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "picorvd": ("https://github.com/aappleby/picorvd.git", "4310ade17a3930dc43ce5cc59b38acc85db11e19"),
    "pico-sdk": ("https://github.com/raspberrypi/pico-sdk.git", "079c6f39023649b154152db30f1d781e884879bc"),
}


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def main() -> None:
    for name, (url, revision) in SOURCES.items():
        path = ROOT / "build" / "references" / name
        if not path.exists():
            path.mkdir(parents=True)
            run("git", "-C", str(path), "init")
            run("git", "-C", str(path), "remote", "add", "origin", url)
            run("git", "-C", str(path), "fetch", "--depth", "1", "origin", revision)
            run("git", "-C", str(path), "checkout", "--detach", revision)
        if run("git", "-C", str(path), "rev-parse", "HEAD") != revision:
            raise SystemExit(f"Unexpected revision in {path}; refusing to replace it")
        if run("git", "-C", str(path), "status", "--porcelain", "--untracked-files=no"):
            raise SystemExit(f"Modified dependency in {path}; refusing to build")
        if name == "pico-sdk":
            run("git", "-C", str(path), "submodule", "update", "--init", "--depth", "1", "lib/tinyusb")
        print(f"{name}: {revision}")


if __name__ == "__main__":
    main()
