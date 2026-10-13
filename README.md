# ch32-pico

A tiny RISC-V board with USB-C programming, 33 accessible GPIOs and hardware
for programmable USB Power Delivery. Built by Left Shift Logical around the
CH32X035, in a familiar 21 × 51 mm Pico-sized board.

![ch32-pico Rev D, front and back](docs/images/ch32-pico.png)

- Program through USB-C using the chip's factory USB bootloader. No separate
  programmer is needed to load your application.
- Put your USB-C supply to work. The integrated PD peripheral and protected
  output switch provide the hardware for firmware-selectable 5, 9, 12, 15 or
  20 V, when offered by your supply.
- Connect sensors, displays and controls through 26 header GPIOs, with UART,
  I2C, SPI, PWM and three ADC inputs. Seven underside GPIO pads expose more
  of the chip, including op-amp connections and one-wire PIOC.
- Fit a breadboard with headers, or solder the castellated edges straight
  onto your own carrier. USB-C sits at the board edge for easy cable access.
- Make it yours. The hardware is open, the project software is MIT-licensed,
  and the Python design sources are included so you can generate revisions.

**Pin 40 is off by default.** Firmware must enable the protected PD output;
once enabled, it can carry the negotiated **5–20 V**. Check your carrier's
wiring before using it. The output discharges through a resistor when switched
off, so attached capacitors can retain voltage briefly.

The outline and 40 header positions match the Pico, with CH32-specific GPIO
labels. Check the [pinout](docs/revision-d.md#peripheral-access) before connecting
a Pico accessory. This board runs CH32 firmware; pin 35 is unconnected.
Pin 37, labeled `EN`, controls the 3.3 V regulator: ground it to disable, then release to enable. See the
[shutdown notes](docs/revision-d.md#shutdown-control) for driver requirements.

**Rev D is a prototype in development.** The board and panel pass local design
checks. USB-PD application firmware, USB serial and assembled-board testing,
including shutdown and restart, are still ahead; the continuous output-current rating is not yet qualified.

Explore the [design and pinout](docs/revision-d.md),
[build the hardware files](docs/revision-d.md#generated-files), or read the
[parts and factory review](docs/factory-review.md) for manufacturing status
and costs. The front and back renders above come from the checked KiCad board.

Software: [MIT](LICENSES/MIT.txt). Hardware:
[CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt). Both allow commercial reuse.
See [licensing](docs/licensing.md) for scope, third-party attribution and the
WCH factory bootloader.
