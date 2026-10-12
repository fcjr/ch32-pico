# Programming and USB debug console

The low-cost design has two CH32V003 chips. U2 is the onboard USB programmer;
U1 runs the application. The user selected HID programming and the minichlink
debug console to keep the BOM low. This is not a USB CDC serial port and does
not appear in Arduino Serial Monitor.

## First flash of each assembled board

Build U2's source firmware with `make lowcost-firmware`. The outputs are
`build/lowcost-probe/probe.bin` and `probe.elf`. A blank U2 cannot enumerate
over USB, so use an external **CH32V003 SWIO** programmer for this step.
An ordinary Arm SWD-only probe is not sufficient.

The factory fixture contacts TP1, U2 PD1/SWIO, and TP4, ground. TP7 is the
board's 3.3 V rail for measurement or a probe's high-impedance voltage-sense
input. TP2 exposes U2 reset if needed. TP5 is U1's SWIO and must not be
confused with TP1.

Power the board through USB 5 V or VSYS. Do not connect another programmer's
3.3 V **power output** to TP7 while the board is powered. The candidate LDO
circuit is not designed for power input through 3V3_OUT. Use 3.3 V SWIO logic,
a common ground, and the external programmer's specified SWIO pull-up.

For a fully open-source external fixture, a Raspberry Pi Pico running
[PicoRVD](https://github.com/aappleby/picorvd) supports this target.
`python3 scripts/dependencies.py` fetches its pinned source and Pico SDK for
an optional external factory probe. These are separate from the onboard firmware. Its default
SWIO is GP28 with a 1k pull-up to 3.3 V. Use its GDB interface to load
`probe.elf`, following the pinned external probe's instructions. PicoRVD and
the onboard rv003usb programmer use different host protocols.

Keep U2 PD1 in debug mode and PD7 in reset mode. Do not apply unrelated
bootloader/option-byte commands. After flashing and verifying U2, disconnect
the external probe and power-cycle the board. U2 should enable the target
supply and enumerate as an HID programmer. This sequence still requires
qualification on the first assembled prototype.

## Normal application uploads

The pinned host source is `build/references/rv003usb/ch32fun/minichlink`.
Build its `minichlink` target with a C compiler and libusb development files.
This has compiled on the development Mac. Linux may also need the upstream
udev rules; installing system permissions is a separate operation.

With the assembled board plugged into USB-C, these are the upstream commands:

```sh
minichlink -C funprog -w application.bin flash -b
minichlink -C funprog -T
```

The first command writes the application MCU and reboots it. The second starts
the debug console and can reboot the target as it attaches. Select the intended
programmer and avoid leaving multiple indistinguishable prototype programmers
connected. These commands are documented, not automatically executed by builds.

Application code must enable ch32fun's `FUNCONF_USE_DEBUGPRINTF` and use
`printf`. `firmware/target-demo` contains a minimal example that prints a
counter without driving any header GPIO. Run `make target-demo` after fetching
the pinned programmer sources and compiler. It writes the binary and ELF to
`build/target-demo`, without flashing any hardware. It uses a finite debug-print timeout
so a disconnected console does not block forever. Its text travels over PD1
to U2, then over USB HID to minichlink. It does not consume the header UART.

For a conventional UART terminal, an external 3.3 V USB-to-UART adapter can use
header pin 1, PD5/TX, pin 2, PD6/RX, and ground. This is independent of the
onboard USB debug console.

## Recovery

Application firmware uploads normally need only USB-C. U2 firmware updates
and recovery still use the external SWIO pads. A USB self-update bootloader
for U2 is not included. Prototype tests must cover write/readback comparison,
target power cycling, console output, unplug/replug and external-VSYS use.
