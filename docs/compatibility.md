> **Revision C:** See the [current X035 pinout](revision-c.md). The material below describes the retained Rev A board.

# Pico compatibility contract

Target: match as much of the original RP2040 Raspberry Pi Pico as practical,
while keeping the CH32V003 as the application MCU. These are design requirements
and a proposed pin allocation, not claims of tested hardware compatibility.

## Selected low-cost implementation

The current circuit uses two CH32V003 MCUs and two inexpensive 3.3 V LDOs.
It targets USB 5 V or VSYS 4.3–5.5 V. The onboard programmer requires one
external SWIO flash; normal target programming then uses USB-C HID.
The user accepted minichlink debug printf. There is no CDC serial bridge.

The target rail switches independently during programming. Header pin 36 is
the main 3.3 V output, and pin 37 disables its regulator. Do not power this
board through pin 36. A 50 mA external header load is a prototype test goal;
current and thermal measurements must establish a usable rating.

## Functions to preserve

| Pico interface | Proposed implementation | Qualification |
| --- | --- | --- |
| 21 x 51 mm, 1 mm board | Same outline, thickness, header pitch, row spacing, and mounting holes | Placement DRC passes; cable fit is unqualified; upper screw heads do not fit beside USB-C |
| Through-hole and castellated mounting | Both in final board; all assembly on top | 40 castellations generated; underside carrier clearance needs final review |
| Ground pins 3, 8, 13, 18, 23, 28, 33, 38 | Ground in every position | Pin 33 shares a continuous ground plane |
| VBUS 40 / VSYS 39 | USB 5 V and isolated system input | LDO regulation; provisional VSYS 4.3–5.5 V, no low-voltage battery operation |
| 3V3_OUT 36 / 3V3_EN 37 | Regulated 3.3 V output; pull enable low to turn it off | 50 mA external-load test goal; validate total USB budget, startup and thermal limits |
| RUN 30 | PD7 configured as target reset | Open-drain/short-to-ground reset; preserve reset option bytes; onboard probe remains available during target reset |
| UART on GP0/GP1, pins 1/2 | PD5/PD6, USART1 TX/RX | Same TX/RX positions; CH32 firmware and peripheral numbering differ |
| I2C on GP4/GP5, pins 6/7 | PC1/PC2, I2C1 SDA/SCL | Same positions and signal direction; use appropriate pull-ups |
| SPI on GP16/17/18/19, pins 21/22/24/25 | PC7/PC0/PC5/PC6, MISO/CS/SCK/MOSI | CS is software-controlled; this does not preserve hardware NSS behavior in SPI slave mode |
| ADC0/1/2 on pins 31/32/34 | PA2/PA1/PC4, CH32 ADC channels 0/1/2 | Preserve position and channel numbers, with lower resolution |
| 3.3 V GPIO signaling | Run the target at 3.3 V | Check each attached device's thresholds, drive current, and timing |

Use the internal target oscillator so PA1 and PA2 remain available for ADC.
UART, I2C, SPI with software CS, and the three ADC inputs can use their default
CH32 mappings without competing remap settings. Firmware must still configure
each peripheral correctly. UART flow-control pins do not match Pico positions.

## Differences that cannot be eliminated by wiring

| Feature | Original Pico | Proposed CH32 board |
| --- | --- | --- |
| Header GPIO count | 26 | 16 while reserving SWIO and reset |
| Missing GPIO positions | All GP0-22 and GP26-28 present | GP9-15 and GP20-22 unconnected |
| ADC resolution | 12-bit | 10-bit; rescaling in software adds no precision |
| ADC_VREF, pin 35 | Accessible ADC supply/reference | Unconnected; target has no separate external-reference pin |
| UART / SPI / I2C controllers | Two of each | One of each; alternate Pico pin mappings are not reproduced |
| PWM | RP2040 PWM slices/channels | CH32 timer outputs; different channel sharing, remaps, and timing; no all-pin PWM equivalence |
| PIO | Eight programmable state machines | None; timing-critical PIO programs need another implementation |
| USB application interface | Native USB device/host controller | USB HID is attached to the programmer; minichlink debug printf, no CDC bridge |
| USB boot behavior | ROM BOOTSEL / UF2 drive | External factory flash of programmer; normal target uploads over HID, no UF2 workflow |
| Debug interface | Arm SWD | WCH single-wire SWIO; ordinary Arm SWD probes are not interchangeable |
| Firmware and compute | Dual-core Arm, 264 KB RAM, 2 MB board flash | Single-core RISC-V, 2 KB RAM, 16 KB flash; recompile/port applications |
| Onboard LED | Dedicated GP25 | Probe activity LED only; no target LED or dedicated GP25 |
| Board monitoring | Internal Pico VSYS/VBUS sensing paths | Not provided by this allocation; adding target sensing consumes GPIOs |
| USB connector/enclosure | Micro-USB | USB-C needs a different opening; upper mounting holes cannot take ordinary screw heads |

The unconnected **physical header pins** are 12, 14, 15, 16, 17, 19, 20, 26,
27, and 29, plus ADC_VREF at 35. These positions are marked `NC` on the back silkscreen, meaning unconnected.
Duplicating GPIOs or adding an I2C expander would not make them equivalent
native Pico GPIOs, so neither is part of this revision.

With a separate probe, the target's entire 16 KB application flash remains
available. No onboard bridge drives PD5 or PD6; both remain available to applications.
Do not connect a placeholder ADC_VREF output merely to make pin 35 look active;
external references on a carrier must not drive the target's entire supply.

The programming pads are top-side test pads, not the Pico's underside Arm
SWD connector. See [programming](programming.md) for their actual assignment.
The back marks pin 30 as `RST`, the target's PD7 reset input. Corner labels
include physical pin numbers 1, 20, 21 and 40. See the [marking review](markings.md).

## Source of truth and references

`hardware/design.py` owns the pin allocation and power requirements. Run
`just generate` to produce the full 40-pin comparison in
`build/proposed-pinout.md` and `build/proposed-pinout.csv`.

- [Raspberry Pi Pico specifications](https://www.raspberrypi.com/products/raspberry-pi-pico/)
  and [datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf).
- [WCH CH32V003 specifications](https://github.com/openwch/ch32v003) and
  [manufacturer peripheral pin tables](https://github.com/openwch/arduino_core_ch32/blob/main/variants/CH32V00x/CH32V003F4/PeripheralPins.c).

See the [mechanical fit review](mechanical.md) for the cable-clearance calculation
and mounting restrictions. These restrictions also apply to Pico carrier boards.
The [power review](power.md) records voltage-drop estimates and unassigned load limits.
