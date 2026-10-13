# Onboard programmer firmware

The user accepted the minichlink debug console instead of a standard USB
serial port. See [programming instructions](../../docs/programming.md) for
factory provisioning, normal uploads and the source-built printf example.

A second CH32V003F4P6 runs the programmer. The build compiles the
MIT-licensed [rv003usb](https://github.com/cnlohr/rv003usb) programmer from
source, with the small board patch in this directory. The dependency includes
the license and copyright notices. The bitbang files also offer the NewBSD
license. No WCH-Link firmware binary is used.

Run `just firmware` or `just lowcost-firmware`. This fetches immutable source revisions, checks
tracked files for changes, copies their Git archives to a generated staging
directory, applies the patch and builds only the `.bin` target. Upstream's
default Make target flashes a device, so the script never invokes it.
Outputs and a source/compiler/hash manifest are in `build/lowcost-probe`.
`hardware/circuit.py` contains the matching circuit.

## Toolchain

The validated compiler is xPack RISC-V GCC 14.2.0-3, with rv32ec/ilp32e support.
The script accepts `RISCV_PREFIX=/absolute/path/to/riscv-none-elf`, or defaults
to the local toolchain under `build/toolchains`.

For macOS ARM64 the tested upstream archive is
[xpack-riscv-none-elf-gcc-14.2.0-3-darwin-arm64.tar.gz](https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v14.2.0-3/xpack-riscv-none-elf-gcc-14.2.0-3-darwin-arm64.tar.gz).
Its verified SHA-256 is
`e76e86b8c500f8e92b3b4ff7b0444cfbf3b218515f322929e0744ec3b9ed80a8`.
Verify the archive before extraction. Other host toolchains need their own
checksum and build verification.

## Board behavior

- USB low-speed HID: D+ on PD4, D- on PD3, 1.5k D- pull-up driven by PD5.
- PC6 senses the active-low VBUS detector. Firmware only asserts the USB
  pull-up while VBUS is present, including when powered externally through VSYS.
- PC1 and PC2 share the target SWIO net. The target has a 5.1k pull-up to its
  switched supply. Both programmer pins float before a requested power-off.
- PD2 drives the target regulator enable. A 100k pull-down keeps a blank or
  reset programmer from powering the target. Firmware enables it at startup,
  allowing standalone target operation without a USB host.
- Power-off waits 20 ms for the candidate 1k discharge resistor and nominal
  2.1uF target rail. Power-up waits 2 ms before configuring SWIO. Scope these
  timings on assembled hardware. External header signals can back-power an
  unpowered target and must be disconnected for this test.
- CH5xx support is disabled. There is no USB CDC serial bridge.

## Provisioning and qualification

A blank programmer needs an external SWIO programmer on TP1, with board ground
and 3.3 V reference. TP2 exposes programmer reset. Normal target programming
then uses USB-C and the upstream minichlink HID transport. An external probe
can also reflash or recover the onboard programmer. USB self-update of the
programmer is not implemented in this candidate.

Keep PD1 in debug mode and PD7 in reset mode. Do not copy upstream option-byte
commands without checking their reset/boot configuration. Initial provisioning
must happen before the onboard target can run.

The build fits 16 KB flash and 2 KB RAM. Static RAM accounting does not measure
worst-case stack use. Hardware tests still need to establish USB enumeration,
program/verify, reset recovery, hot-plug behavior, rail discharge, and timing
across supply and temperature. Upstream describes the programmer as
experimental. Its existing USB identity is retained for prototype host-tool
compatibility; production USB identity allocation remains unresolved.
