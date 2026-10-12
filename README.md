# ch32-pico

A small RISC-V development board from Left Shift Logical, built around the
CH32V003 with USB-C power and an onboard open-source programmer. It fits the
Raspberry Pi Pico's board outline and header layout, including castellated
edges and all four mounting holes.

![ch32-pico front and back PCB renders](docs/images/ch32-pico.png)

Front and back views of the current PCB design.

## The board

- CH32V003F4P6 target with 16 KB flash, 2 KB RAM and 16 GPIOs.
- UART, I2C, SPI and ADC signals at useful Pico header positions.
- USB-C for power, target programming and a minichlink debug console.
- A second CH32V003 runs the open-source rv003usb programmer firmware.
- 21 × 51 mm PCB with castellated edges for soldering onto a carrier board.

This is an untested hardware prototype. The saved layout passes electrical
and routing checks; USB operation, power limits and physical fit still need
assembled-board testing.

## Pico compatibility

The power and ground pins retain their Pico positions. GPIO labels describe
the CH32 signals. Ten Pico GPIO positions and ADC_VREF are unconnected, and
RP2040 programs need porting to the CH32's RISC-V architecture and smaller
memory. There is no PIO, UF2 bootloader or native target USB.

Power comes from USB 5 V or VSYS, with a provisional VSYS range of 4.3–5.5 V.
The 3V3 pin is an output. The USB-C socket leaves the four mounting holes in
place, but ordinary M2 screw heads do not fit beside the two upper holes.
Check the [pinout](docs/compatibility.md), [power notes](docs/power.md) and
[mechanical fit](docs/mechanical.md) before using a Pico carrier or enclosure.

## Programming

A blank board needs one external SWIO flash to install the onboard programmer.
After that, plug in USB-C to upload target firmware with minichlink:

```sh
minichlink -C funprog -w application.bin flash -b
minichlink -C funprog -T
```

The console carries debug printf over USB HID. It does not appear as a USB
serial port; hardware UART is available on header pins 1 and 2.
The [programming guide](docs/programming.md) covers first-time provisioning,
recovery and the included printf example.

## Working on the design

The schematic, placement, routing checks and fabrication exports are driven
by Python. Start with the [build guide](docs/build.md). The saved
[KiCad board](hardware/review/ch32-pico.kicad_pcb) and its
[validation report](hardware/review/validation.json) are in `hardware/review/`.

Fabrication files, ordering instructions and pricing are documented in the
[manufacturing guide](docs/manufacturing.md), [panelization notes](docs/panelization.md)
and [order review](docs/order-review.md).

## License

Original software and firmware changes use [MIT](LICENSES/MIT.txt).
The original board design uses [CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt),
the permissive CERN Open Hardware Licence. Both allow commercial reuse.
See [licensing](docs/licensing.md) for the scope, attribution and third-party materials.
