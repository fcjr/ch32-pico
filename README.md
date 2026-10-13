# ch32-pico

A tiny RISC-V board with USB-C programming, 33 accessible GPIOs and hardware
for programmable USB Power Delivery. Built by Left Shift Logical around the
CH32X035, in a familiar 21 × 51 mm Pico-sized board.

![ch32-pico Rev E, front and back](docs/images/ch32-pico.png)

- Program through USB-C using the chip's factory USB bootloader. No separate
  programmer is needed to load your application.
- Put your USB-C supply to work. The integrated PD peripheral and protected
  output switch provide the hardware for firmware-selectable 5, 9, 12, 15 or
  20 V, when offered by your supply.
- Connect sensors, displays and controls through 26 header GPIOs, with UART,
  I2C, SPI, PWM and three ADC inputs. Six underside GPIO pads expose more
  of the chip, including op-amp connections. Bridge SJ1 for PC7 and one-wire
  PIOC on pin 35; a separate FAULT pad exposes the PD switch status.
- Probe what the board is doing. Labeled contacts expose current and voltage
  sensing, raw USB VBUS, CC1/CC2, PD enable, LED control and USB data.
- Fit a breadboard with headers, or solder the castellated edges straight
  onto your own carrier. USB-C sits at the board edge for easy cable access.
- Make it yours. The hardware is open, the project software is MIT-licensed,
  and the Python design sources are included so you can generate revisions.

**Pin 40 is off by default.** Firmware must enable the protected PD output;
once enabled, it can carry the negotiated **5–20 V**. Check your carrier's
wiring before using it. The output discharges through a resistor when switched
off, so attached capacitors can retain voltage briefly.

The outline and 40 header positions match the Pico, with CH32-specific GPIO
labels. Check the [pinout](docs/revision-e.md#peripheral-access) before connecting
a Pico accessory. This board runs CH32 firmware. Pin 35, marked `PC7*`, is
isolated by default; bridge the normally open `SJ1` pads to connect PC7.
Pin 37, labeled `EN`, controls the 3.3 V regulator: ground it to disable, then
release to enable. See the
[shutdown notes](docs/revision-e.md#shutdown-control) for driver requirements.

**Rev E is a prototype in development.** The board and panel pass local design
checks. USB-PD application firmware, USB serial and assembled-board testing,
including shutdown and restart, are still ahead; the continuous output-current
rating is not yet qualified.
The eFuse is set to about 2.93 A nominal; this is a fault threshold, not a
continuous rating. See the [power-path correction](docs/revision-e.md#power-path-correction).

Explore the [design and pinout](docs/revision-e.md),
[build the hardware files](docs/revision-e.md#generated-files), or read the
[parts and factory review](docs/factory-review.md) for manufacturing status
and costs. The front and back renders above come from the checked KiCad board.

## Build the JLCPCB fabrication files

Install `uv`, `just` and KiCad 10 with `kicad-cli` on your PATH, then run:

```sh
just jlcpcb
```

This checks the design and generates a four-board panel for a five-panel,
20-device prototype batch. Python dependencies install from the committed
locks. Upload these files together:

| File | JLCPCB upload |
|---|---|
| `build/jlcpcb/gerbers.zip` | PCB fabrication |
| `build/jlcpcb/bom.csv` | Assembly BOM |
| `build/jlcpcb/cpl.csv` | Assembly placement |

`build/jlcpcb/factory-notes.txt` contains the board and assembly requirements.
`build/ch32-pico-jlcpcb.zip` bundles all files and review reports; extract it
first, then upload the inner `gerbers.zip` to JLCPCB.

Generated fabrication files live in the Git-ignored `build/` directory. The
repo tracks the design, checked PCB, tool locks, renders and generation code.
See [build instructions](docs/build.md) for KiCad Python setup, routing and
revision commands, and [manufacturing notes](docs/manufacturing.md) for the
prototype's pending factory checks. The command does not submit an order.

Software: [MIT](LICENSES/MIT.txt). Hardware:
[CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt). Both allow commercial reuse.
See [licensing](docs/licensing.md) for scope, third-party attribution and the
WCH factory bootloader.
