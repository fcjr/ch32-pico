> **Historical Rev B reference.** [Rev C](revision-c.md) supersedes this layout. The Rev B board and renders are preserved in [commit 479ceb9](https://github.com/fcjr/ch32-pico/tree/479ceb9).

# Revision B: CH32X035 + USB PD

This revision has a checked schematic, routed board, front/back CAD render and
four-up KiKit manufacturing previews. It is not released for ordering. PD/USB
application firmware and physical qualification remain unfinished. Rev A files
and prices do not describe this revision.

## Selected architecture

One CH32X035C8T6 (LQFP48, 7 × 7 mm body, 9 × 9 mm lead span) replaces both
CH32V003s. Its native USB port handles application USB and factory USB ISP;
its CC1/CC2 peripheral handles PD. No external PD controller or adjustable
DC/DC converter is used. The selected package retains all 26 Pico GPIO
positions and a separate hardware reset without sharing the USB, PD or SDI pins.

USB VBUS goes through a TPS259470L protected load switch to Pico header **pin
40, PD OUT**. This is the actual negotiated rail, less switch/copper voltage
drop. A separate AP63203 fixed buck supplies 3.3 V to the MCU and pin 36.
Two diodes isolate the 4.3–5.5 V VSYS input at pin 39 from the negotiated rail.

The power-path design goal is a **20 V, 5 A input contract (100 W)**. The
X035 does not carry load current. Available output current is the source's
advertised current minus board consumption, bounded by the qualified PCB,
switch and external connection. A 5 A source contract requires the source to
have established a 5 A capable cable, normally an electronically marked cable.
A generic 2.54 mm header/contact is not assumed to carry 5 A. Prototype
thermal and fault testing must establish the released continuous-current rating.

**Pin 40 is no longer a fixed 5 V supply or an input.** A Pico carrier using
that pin as 5 V power can be damaged by 9–20 V. Pin 40 is marked PDOUT, with
an additional front-side 5–20V legend. The physical outline, castellations,
40 header positions and four mounting holes remain unchanged.

The selectable fixed-PDO targets are 5, 9, 12, 15 and 20 V, but a requested
voltage is available only when the source advertises it. **12 V is optional**;
a firmware request must fail if absent, rather than substitute a higher voltage.
No PPS interpolation or EPR voltages above 20 V are planned.

## Compatibility limits

Pins **35 (ADC_VREF)** and **37 (3V3_EN)** are unconnected. The MCU lacks a
separate external ADC reference pin. Leaving 37 unconnected is a board-design
choice: it avoids exposing the high-voltage regulator enable network at a Pico
logic pin. RUN at pin 30 maps to PA21 hardware reset; preserve its option-byte
configuration. All ground positions, the 3.3 V output and VSYS location remain.

The CH32 has different GPIO names, alternate-function assignments and resources.
It cannot run RP2040 binaries, PIO programs or Pico UF2 firmware. The mapping
preserves one default UART, I2C, SPI and three ADC inputs at familiar positions;
it does not reproduce every RP2040 peripheral mapping or PWM capability.

## Header allocation

Top/component view, USB at the top. Pin numbers follow the original Pico.
The table is generated from `hardware/design.py`.

| Pico pin | Pico function | Rev B signal | X035 package pin | Function |
|---:|---|---|---:|---|
| 1 | GP0 | PB10 | 30 | USART1 TX, default mapping |
| 2 | GP1 | PB11 | 31 | USART1 RX, default mapping |
| 3 | GND | GND | — | Ground |
| 4 | GP2 | PA8 | 40 | GPIO |
| 5 | GP3 | PA9 | 41 | GPIO |
| 6 | GP4 | PA11 | 43 | I2C SDA, default mapping |
| 7 | GP5 | PA10 | 42 | I2C SCL, default mapping |
| 8 | GND | GND | — | Ground |
| 9 | GP6 | PA12 | 44 | GPIO |
| 10 | GP7 | PA13 | 45 | GPIO |
| 11 | GP8 | PA14 | 46 | GPIO |
| 12 | GP9 | PA15 | 1 | GPIO; USART2 TX remap 2 |
| 13 | GND | GND | — | Ground |
| 14 | GP10 | PA16 | 2 | GPIO; USART2 RX remap 2 |
| 15 | GP11 | PA17 | 3 | GPIO |
| 16 | GP12 | PA18 | 4 | GPIO |
| 17 | GP13 | PA19 | 5 | GPIO |
| 18 | GND | GND | — | Ground |
| 19 | GP14 | PA20 | 6 | GPIO |
| 20 | GP15 | PA22 | 8 | GPIO |
| 21 | GP16 | PA6 | 16 | SPI MISO, default mapping |
| 22 | GP17 | PA4 | 14 | SPI NSS or software chip select |
| 23 | GND | GND | — | Ground |
| 24 | GP18 | PA5 | 15 | SPI SCK, default mapping |
| 25 | GP19 | PA7 | 17 | SPI MOSI, default mapping |
| 26 | GP20 | PB6 | 26 | GPIO |
| 27 | GP21 | PB7 | 27 | GPIO |
| 28 | GND | GND | — | Ground |
| 29 | GP22 | PA23 | 9 | GPIO |
| 30 | RUN | PA21 | 7 | RST input; preserve reset option-byte configuration |
| 31 | GP26 / ADC0 | PA0 | 10 | ADC channel 0 |
| 32 | GP27 / ADC1 | PA1 | 11 | ADC channel 1 |
| 33 | AGND | GND | — | Continuous ground plane |
| 34 | GP28 / ADC2 | PA2 | 12 | ADC channel 2 |
| 35 | ADC_VREF | NC | — | No independent external ADC reference input |
| 36 | 3V3_OUT | 3V3_OUT | — | Fixed 3.3 V output; prototype load rating pending |
| 37 | 3V3_EN | NC | — | Reserved; isolated from high-voltage regulator control |
| 38 | GND | GND | — | Ground |
| 39 | VSYS | VSYS | — | 4.3-5.5 V input only; diode-isolated from PD VBUS |
| 40 | VBUS | PD_OUT | — | Switched negotiated 5-20 V output; incompatible with fixed-5V Pico carriers |

## Reserved MCU pins

| X035 GPIO | Package pin | Board function |
|---|---:|---|
| PC16 | 32 | USB_DM |
| PC17 | 33 | USB_DP |
| PC14 | 38 | CC1 |
| PC15 | 39 | CC2 |
| PC18 | 34 | SDIO |
| PC19 | 37 | SDCK |
| PB0 | 20 | VBUS_SENSE |
| PB1 | 21 | PDOUT_SENSE |
| PB2 | 22 | PD_ENABLE |
| PB3 | 23 | STATUS_LED |
| PB4 | 24 | PD_FAULT_N |
| PA3 | 13 | CURRENT_SENSE |

The seven unused MCU pins are PC6, PC7, PB5, PB8, PB9, PB12 and PB13,
package pins 18, 19, 25, 28, 29, 35 and 36. They have no header or test-pad
connection and are explicitly NC in the schematic. SDI recovery
uses PC18/PC19 (two wires), not the V003 single-wire SWIO protocol. BOOT pulls
PC17/D+ high through 4.7 kΩ during power-up, matching WCH's reference circuit.
Release BOOT before USB ISP. No first-time external programmer is needed for
normal factory USB bootloader entry. The factory bootloader is WCH vendor
code; the planned application/PD firmware and host tools are source-available
under their respective open-source licenses. Do not describe the ROM as MIT.

## Peripheral access

This is a board-level assessment against WCH datasheet v1.7, table 2-1.
A peripheral listed in the chip's feature list does not necessarily have a
free connection on this board. Alternate functions share pins and cannot all
operate together.

| Function | Access on Rev B |
|---|---|
| ADC / touch sensing | Seven header inputs: PA0, PA1, PA2, PA4, PA5, PA6 and PA7. ADC3, ADC8 and ADC9 monitor board current, VBUS and PD OUT. The LQFP48 package does not expose ADC10–13. |
| OPA1 | No free external positive input or output. PB0/PB4 serve board power sensing/faults, PB8 is NC; outputs PA3/PB5 are current sensing/NC. It is unavailable as a general-purpose external op-amp on the assembled board. |
| OPA2 | Usable through header pins, for example PA7 positive input, PA5 negative input and PA4 output. These share SPI/ADC pins. |
| USART1 / USART2 / USART4 | Header TX/RX pairs exist: PB10/PB11; PA15/PA16 with USART2 remap 2; PA5/PA9 with USART4 remap 1. Flow-control and synchronous-clock availability varies with mapping. |
| USART3 | No free header RX. PB4 is the fault input; alternate RX is PC19 at the SDCK test pad. PA18 can supply remapped TX, but using PC19 sacrifices simultaneous SDI debugging. |
| PIOC programmable I/O | PC18/PC19 are accessible only at SDIO/SDCK test pads and share the debug interface. The alternative one-wire pin PC7 is NC. |
| Timers / PWM | Many header timer functions remain. PB9's dedicated TIM1_CH1 and PB12/PC16 TIM1_CH4 paths are NC or USB. These limit the normal alternate-function mapping; the separate GPIO PWM mapping must be assessed for each firmware use. |
| Clock output | MCO is on PB9, which is NC. There is no external clock-output connection. |
| Comparators | Header input choices remain for all three. CMP1 output is PA1; CMP2/CMP3 outputs are PB2/PB3, assigned to load-switch enable and the LED. Internal timer-trigger uses do not need an output pin. |
| USB / USB PD | Connected to USB-C, not free header GPIO. The power circuit is a PD sink; USB host power sourcing and PD source/DRP operation are not provided by this board. |
| Core, memory, DMA, watchdogs | No additional external pins needed. |

Pins 35 and 37 being NC are separate Pico-compatibility limits, not missing
X035 GPIO connections. Adding pads for the seven unused MCU pins would require
a layout revision; firmware alone cannot expose them.

## Power protection and firmware work

The switch defaults off through a 10 kΩ enable pulldown. The 470L variant
provides adjustable OVLO, active fault current limiting, reverse blocking,
controlled turn-on and thermal latch-off. Its 600 Ω ILM resistance sets an
approximately 5.56 A nominal fault threshold, with tolerance; that threshold
is not an output load rating and is not a negotiated-current limiter. Firmware
must account for the actual source contract and board load. The ILM voltage
is available to PA3 for monitoring.

The 82 kΩ / 4.7 kΩ OVLO divider trips at about 22.14 V nominal. VBUS and
PD OUT each have 100 kΩ / 10 kΩ ADC dividers and 100 nF filtering. These
are sense inputs; load current never goes through a GPIO. USB ESD clamps
reference 3.3 V, not the high-voltage rail.

Firmware must keep the output off until a valid contract and PS_RDY are
established and measured VBUS agrees with the selected voltage. Disable before
renegotiation; wait for output discharge; invalidate the contract on detach,
hard reset, fault, timeout or watchdog reset. After any such event require a
new explicit enable. Native CDC can provide commands and a console, but has
not yet been integrated or bench-tested. Charging-only USB-C sources may
provide PD power without a USB data host.

WCH's datasheet notes early silicon lacking I2C and ADC channels including
ADC3. Procurement must exclude those early lots and bring-up must test I2C
and PA3 current sensing. Headers ADC0/1/2 and VBUS ADC8/9 avoid those missing
channels, but that does not remove the current-sense/I2C lot requirement.

## Current checks and cost

`make check` passes: zero schematic ERC violations, exported-netlist parity,
zero placement DRC violations, the marking audit, and 48 unit/fault tests.
The saved routed board also passes independent KiCad DRC with zero violations
and zero unconnected nets. Freerouting produced the passing candidate with
95 vias and 1066.682 mm of track; the native router candidate failed. Checks
confirm source pad/net parity, retained critical copper, no drilled vias in
solder-paste lands, and sampled USB ground-reference coverage.

The 93 × 71 mm KiKit panel passes DRC and verifies all four copies against
the source pad/net map, trace/via geometry and silkscreen. Five panels still
mean 20 devices. These checks do not establish a continuous output-current
rating or certify USB/PD performance.

The fitted BOM estimate for 20 devices is **$3.9110 per board** (41 fitted
parts), excluding assembly, PCB, setup, attrition, MOQ rounding, shipping and
tax. This is above the original low-cost target once manufacturing is added.
The protected 5 A switch and wide-input 3.3 V buck account for about $2.25 of
that total. This BOM is provisional, not a claim of minimum achievable cost.
Reproduce it with `python3 scripts/revb_bom_review.py` from the dated inventory
snapshot. Cost optimization remains part of the revision work.

The selected 5 A USB-C socket is about $0.2445 each at the observed tier.
The ESD part is now USBLC6-2SC6 (C7519), with 45,703 reported available,
replacing the scarce SOT666 part. Only **two** C29779902 MCUs were reported
available; that does not cover the 20-board run. Inventory is not reserved.

The MIT code in `firmware/pd/policy.c` implements and tests fixed-PDO selection,
current budgeting, output-discharge gating, ACCEPT/PS_RDY sequencing, explicit
arming, stale-request
rejection and fault/detach handling. It is platform-independent policy code,
**not yet flashable X035 firmware**. The tests compile it with address and
undefined-behavior sanitizers. USB-PD transport, ADC/GPIO drivers, watchdog
handling and CDC integration still need implementation and hardware tests.

## Remaining release gates

- Review the routed power layout and confirm the TI stencil apertures and JLC component orientations.
- Complete and test the PD/USB firmware, including detach, hard reset and voltage changes.
- Validate hot-plug/inrush, 3.3 V stability, switch temperature, 5 A copper/contact
  temperature, fault current, output discharge and backfeed with assembled boards.
- Resolve live MCU inventory for 20 devices plus assembly attrition.
- Confirm the actual JLC quote, allocations and five-panel assembly tier.

The Rev A source, generation scripts and all then-current outputs were archived
before changing the circuit. The routing and manufacturing-preview workflow
now handles Rev B; revision and source checks reject stale layouts. The Rev A
programmer build remains preserved and refuses to build as Rev B.

## Generated files

- `hardware/review/ch32-pico.kicad_pcb`: saved Rev B routed review checkpoint.
- `hardware/review/validation.json`: router comparison and independent checks.
- `build/ch32-pico.kicad_sch`: generated schematic.
- `docs/images/ch32-pico.png`: front/back CAD render.
- `build/manufacturing-preview/`: single-board Gerber/BOM/CPL preview.
- `build/panel-preview/`: four-up KiKit PCB, Gerbers, BOM and CPL.
- `build/quote-package/`: factory-review inputs, with stock-shortfall notices.
- `firmware/pd/`: tested policy source and the remaining transport-integration requirements.

Rebuild with `make check`, `make route`, `make review`, `make render`,
`make manufacturing-preview`, `make panel-preview`, `make order-review` and
`make quote-package`, in that order. No command purchases parts or submits an
order. The preview manifests remain explicitly unreleased.

The BOOT resistor is next to D+ and isolates the longer button wire. The PD
output uses both outer copper layers beside the upper mounting hole. The
fixed buck has explicit local switching and capacitor paths. These routes
are protected from autorouter changes and checked against the generated seed.

## Sources

- [WCH CH32X035 datasheet, English v1.7](https://akizukidenshi.com/goodsaffix/CH32X035.pdf),
  pin diagrams/table 2-1, electrical ratings and silicon notes.
- [WCH reference hardware and evaluation guide](https://github.com/openwch/ch32x035/tree/c6253942b29ff2a3f5e2829182a874afffa45881/EVT/PUB).
- [TI TPS25947 datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf),
  exact 470L variant, protection tolerances and RPW0010A land pattern.
- [Diodes AP63203 datasheet](https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf).
- [G-Switch GT-USB-7010AW manufacturer drawing](https://www.lcsc.com/datasheet/C963411.pdf),
  2023-02-01: 5 A VBUS, 1.85 mm reference mating gap. Cable/stake fit still needs testing.
- [USB-IF PD overview](https://www.usb.org/sites/default/files/D2T2-1%20-%20USB%20Power%20Delivery.pdf).
- [MIT ch32fun PD sink source](https://github.com/cnlohr/ch32fun/tree/1e4887e11d4bfa739ed5604524b69f5be9f9275b/examples_x035/usbpd_sink).
