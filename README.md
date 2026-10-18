# ch32-pico

A tiny RISC-V board with USB-C programming, 37 accessible GPIOs and hardware
for programmable USB Power Delivery. Built by Left Shift Logical around the
CH32X035, in a familiar 21 × 51 mm Pico-sized board.

**Prototype layout complete.** The fitted parts estimate is about $3.21 per
board at a quantity of 20. Power components sit by USB-C, the two buttons sit
together at the bottom, and the layout uses four copper layers with front-side
assembly. PCB, assembly, attrition and shipping costs are additional. The
renders below show the checked four-layer layout.

![ch32-pico Rev A, front and back](docs/images/ch32-pico.png)

- Program through USB-C using the chip's factory USB bootloader. No separate
  programmer is needed to load your application.
- Put your USB-C supply to work. The integrated PD peripheral lets firmware
  request 5, 9, 12, 15 or 20 V on pin 40, when offered by your supply.
- Connect sensors, displays and controls through 26 header GPIOs, with UART,
  I2C, SPI, PWM and three ADC inputs. Ten underside GPIO pads expose more
  of the chip, including op-amp connections and two more ADC inputs. Bridge
  SJ1 for PC7 and one-wire PIOC on pin 35.
- Probe what the board is doing. Labeled contacts expose VBUS and its sense
  voltage, CC1/CC2, LED control and USB data.
- Fit a breadboard with headers, or solder the castellated edges straight
  onto your own carrier. USB-C sits at the board edge for easy cable access.
- Make it yours. The hardware is open, the project software is MIT-licensed,
  and the Python design sources are included so you can generate revisions.

**Pin 40 is USB VBUS, like the Pico's.** It is 5 V by default, and carries up to
**20 V** once firmware negotiates a higher contract. Check your carrier tolerates
every voltage your firmware may request. As on the Pico, there is no switch,
current limit or reverse blocking on pin 40: the USB source's own protection
handles shorts, and pin 40 must not be powered while USB is connected. A TVS
clamp at the connector protects the board's regulator from hot-plug spikes.

The outline and 40 header positions match the Pico, with CH32-specific GPIO
labels. Check the [pinout](docs/design.md#header-allocation) before connecting
a Pico accessory. This board runs CH32 firmware. Pin 35, marked `PC7*`, is
isolated by default; bridge the normally open `SJ1` pads to connect PC7.
Pin 37, labeled `EN`, controls the 3.3 V regulator: ground it to disable, then
release to enable. See the
[shutdown notes](docs/design.md#shutdown-control) for driver requirements.

**Rev A is a prototype in development.** The schematic and routed board pass
electrical and layout checks, with all 102 regression tests passing. USB-PD
application firmware, USB serial and assembled-board testing, including
shutdown and restart, are still ahead; the continuous output-current rating
is not yet qualified. The hardware target is 3 A, with the board supply
subtracted from the negotiated current. See
[pin 40 power](docs/design.md#pin-40-is-usb-vbus).

Explore the [design and pinout](docs/design.md),
[build the hardware files](docs/design.md#generated-files), or read the
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
See [build instructions](docs/build.md) for KiCad Python setup and routing
commands, and [manufacturing notes](docs/manufacturing.md) for the prototype's
pending factory checks. The command does not submit an order.

Software: [MIT](LICENSES/MIT.txt). Hardware:
[CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt). Both allow commercial reuse.
See [licensing](docs/licensing.md) for scope, third-party attribution and the
WCH factory bootloader.
