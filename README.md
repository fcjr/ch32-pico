# ch32-pico

A RISC-V development board from Left Shift Logical, built around one
CH32X035C8T6 with native USB and USB Power Delivery. It keeps the Raspberry Pi
Pico's 21 × 51 mm outline, 40 header positions, castellated edges and four
mounting holes.

![ch32-pico Rev B, front and back](docs/images/ch32-pico.png)

**Rev B is a routed prototype, not ready to order.** The schematic, board and
four-up KiKit panel pass the local electrical and layout checks. Application
firmware and physical power testing are still unfinished.

USB-C provides power and access to the chip's factory USB bootloader. The
planned firmware will negotiate 5, 9, 12, 15 or 20 V and switch that voltage to
pin 40. Each voltage must be offered by the connected supply; 12 V is optional.
Native USB serial is planned but not implemented yet.

**Pin 40 is PD OUT and can carry 20 V.** Check a Pico carrier's wiring before
connecting it. The output uses a protected load switch, controlled by the MCU.
The design targets a 5 A input contract, but the continuous output rating still
needs thermal and connector testing.

All 26 Pico GPIO positions have CH32 GPIOs. UART, I2C, SPI and three ADC inputs
occupy familiar positions, but this board cannot run Pico firmware or reproduce
every Pico peripheral mapping. Pin 30 is reset, pin 36 is fixed 3.3 V, and pin 39
accepts a 4.3–5.5 V input. Pins 35 and 37 are unconnected. Some X035 functions
also lack free external connections, including OPA1 and the clock output.
See the [complete pinout and peripheral limits](docs/revision-b.md#peripheral-access)
and [silkscreen review](docs/markings.md).

The estimated fitted BOM is **$3.91 per device** for a 20-device run, before
PCB fabrication, assembly, attrition and shipping. Five four-up panels make
20 devices. The saved JLC stock check found only two of the selected MCUs,
leaving 18 short before attrition. Stock and prices need checking again before
an order.

The board is generated from Python in `hardware/`. The [Rev B design notes](docs/revision-b.md)
cover the circuit, sources, remaining work and
[build and fabrication commands](docs/revision-b.md#generated-files).
The front/back images come from the checked KiCad board via `make render`.
Generation scripts remain in the repository for future revisions. Documents
marked Rev A describe the previous two-MCU board.

Original software and firmware changes use [MIT](LICENSES/MIT.txt). The original
board design uses [CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt), the permissive
CERN Open Hardware Licence. Both allow commercial reuse. The factory USB
bootloader is WCH vendor code, not MIT project firmware. See
[licensing](docs/licensing.md) for scope and third-party attribution.
