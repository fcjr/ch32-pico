# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Build the SWIO printf example into build/, without contacting hardware."""
from pathlib import Path
import os
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'build/target-demo';out.mkdir(parents=True,exist_ok=True)
    for name in ('Makefile','main.c','funconfig.h'):
        shutil.copy2(ROOT/'firmware/target-demo'/name,out/name)
    from license_files import copy_notices
    copy_notices(out)
    prefix=os.environ.get('RISCV_PREFIX',str(ROOT/'build/toolchains/'
        'xpack-riscv-none-elf-gcc-14.2.0-3/bin/riscv-none-elf'))
    subprocess.run(['make','-B','-C',str(out),'main.bin',f'PREFIX={prefix}',
        f'CH32FUN={ROOT}/build/references/rv003usb/ch32fun/ch32fun'],check=True)


if __name__=='__main__':main()
