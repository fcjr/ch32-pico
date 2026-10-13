# Revision C: CH32X035 + USB PD

Historical revision: the current board is [Rev D](revision-d.md), which connects
pin 37 to regulator enable. The pinout and measurements below describe Rev C.

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
Seven additional GPIOs now reach unpopulated underside pads.

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
40 header positions remain unchanged. Rev C removes all four Pico mounting
holes. Mount through the headers or castellations; this revision does not
fit mounting hardware that relies on those holes.

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

| Pico pin | Pico function | Rev C signal | X035 package pin | Function |
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

The seven previously unused MCU pins now connect to underside solder pads.
They add no fitted components or assembly operations. The new pads have no
solder-paste apertures and are intended for hand-soldered wires or test probes.

| Back pad | Signal | MCU package pin | Useful alternate function |
|---|---|---:|---|
| TP6 | PC6 | 18 | GPIO, TIM1 complementary output |
| TP7 | PC7 | 19 | One-wire PIOC without taking the SDI pins |
| TP8 | PB5 | 25 | OPA1 output, timer break input |
| TP9 | PB8 | 28 | OPA1 positive input, TIM1 complementary output |
| TP10 | PB9 | 29 | Clock output, TIM1 channel 1 |
| TP11 | PB12 | 35 | TIM1 channel 4 remap |
| TP12 | PB13 | 36 | USART4 TX remap |
| TP13 | GND | 47 | Ground |

There are 33 general-purpose connections across the headers and expansion
pads, plus reset and the separate debug pads. SDI recovery
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

| Function | Access on Rev C |
|---|---|
| ADC / touch sensing | Seven header inputs: PA0, PA1, PA2, PA4, PA5, PA6 and PA7. ADC3, ADC8 and ADC9 monitor board current, VBUS and PD OUT. The LQFP48 package does not expose ADC10–13. |
| OPA1 | Available through PB8 positive input and PB5 output on back pads, with negative input choices PA1/PA6/PB6 on the main headers. PB0, PB4 and PA3 remain assigned to power monitoring/control. |
| OPA2 | Usable through header pins, for example PA7 positive input, PA5 negative input and PA4 output. These share SPI/ADC pins. |
| USART1 / USART2 / USART4 | Header TX/RX pairs exist: PB10/PB11; PA15/PA16 with USART2 remap 2; PA5/PA9 with USART4 remap 1. Flow-control and synchronous-clock availability varies with mapping. |
| USART3 | No free header RX. PB4 is the fault input; alternate RX is PC19 at the SDCK test pad. PA18 can supply remapped TX, but using PC19 sacrifices simultaneous SDI debugging. |
| PIOC programmable I/O | Two-wire operation uses PC18/PC19 at SDIO/SDCK and shares debugging. PC7 on TP7 provides the alternative one-wire connection without taking those debug pins. |
| Timers / PWM | Header timer functions remain, with PB9 TIM1_CH1 and PB12 remapped TIM1_CH4 now on back pads. Select a compatible remap for the complete timer; alternate functions are not all simultaneous. |
| Clock output | MCO is available on PB9 at TP10. |
| Comparators | Header input choices remain for all three. CMP1 output is PA1; CMP2/CMP3 outputs are PB2/PB3, assigned to load-switch enable and the LED. Internal timer-trigger uses do not need an output pin. |
| USB / USB PD | Connected to USB-C, not free header GPIO. The power circuit is a PD sink; USB host power sourcing and PD source/DRP operation are not provided by this board. |
| Core, memory, DMA, watchdogs | No additional external pins needed. |

Pins 35 and 37 being NC are separate Pico-compatibility limits, not missing
X035 GPIO connections. The seven expansion pads are part of the Rev C layout. No free ADC inputs
are added because these seven pins do not have ADC functions.

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

## Placement and routing

Rev C keeps the GT-USB-7010AW 5 A socket and moves its mouth to 0.30 mm
beyond the PCB edge. The four mounting holes were removed with user approval.
The old 1.15 mm recess is gone. The manufacturer's plug-mating dimension is
still a reference, not a guaranteed cable-fit test; verify real cables and
stake/peg clearance on the first assembled boards.

The AP63203 and inductor moved from about Y=40 mm to Y=15 mm, above the MCU.
The protected PD output and its timing capacitor remain near the USB
connector and pin 40. The timing connection is under 5 mm on the top layer. The buck
input capacitor has direct top-copper connections to VIN and GND, each below
2 mm of centerline length. Its switching and bootstrap paths remain local
and on the top layer. The dedicated feedback trace runs on the back; an In2
copper keepout at the feedback via prevents the shared 3.3 V plane from
bypassing it. The buck powers the MCU and fixed 3.3 V header, not PD OUT.

`hardware/power_layout.py` checks the short input-capacitor connections,
switch-node layer/length, absence of switching vias, the local load-switch timing connection, and
feedback-plane isolation. These supplement source-net parity, KiCad DRC, critical-copper
preservation, no drilled vias in paste lands, USB ground-reference sampling,
and the front/back marking audit. They do not establish a continuous current
rating or certify USB/PD performance.

The saved route was selected from the pinned KiCadRoutingTools and
Freerouting 2.5.0 comparison. Freerouting passes all final gates; the native
candidate retains three opens and is not used. The saved board has 137 vias
and 1,350.217 mm of trace centerline. The routed VSYS branch is 6.108 mm,
down from 58.56 mm in Rev B. The buck input-capacitor connections are
1.562 mm each; the load-switch timing connection is 4.269 mm.

Validation includes 54 passing tests, zero schematic ERC violations, zero
board DRC violations and zero unconnected items. The four panel copies also
have zero DRC violations and zero opens, with pad-net, copper and silkscreen
parity against the saved board. All 41 fitted components remain on the front;
the underside expansion pads do not add assembly placements.

The 93 × 71 mm panel contains four boards. Five panels mean 20 devices.
The panel rails are separated from the board edges by 3 mm, leaving room
for the 0.30 mm connector overhang before depaneling. The top breakaway tab
is offset to the left of USB-C. The final outline, including milling fillets,
is checked for overlap with all four connector overhangs. The castellated
sides have no tabs.

## Cost and remaining work

The 2026-10-13 UTC fitted BOM estimate for 20 devices is **$3.9214 per board** (41 fitted
parts), excluding assembly, PCB, setup, attrition, MOQ rounding, shipping and
tax. This is above the original low-cost target once manufacturing is added.
The protected 5 A switch and wide-input 3.3 V buck account for about $2.25 of
that total. This BOM is provisional, not a claim of minimum achievable cost.
Reproduce it with `uv run python scripts/revb_bom_review.py` from the dated inventory
snapshot. Cost optimization remains part of the revision work.

The selected 5 A USB-C socket is about $0.2445 each at the observed tier.
The ESD part is now USBLC6-2SC6 (C7519), with 45,269 reported available,
replacing the scarce SOT666 part. Only **two** C29779902 MCUs were reported
available; that does not cover the 20-board run. Inventory is not reserved.

The MIT code in `firmware/pd/policy.c` implements and tests fixed-PDO selection,
current budgeting, output-discharge gating, ACCEPT/PS_RDY sequencing, explicit
arming, stale-request
rejection and fault/detach handling. It is platform-independent policy code,
**not yet flashable X035 firmware**. The tests compile it with address and
undefined-behavior sanitizers. USB-PD transport, ADC/GPIO drivers, watchdog
handling and CDC integration still need implementation and hardware tests.

See the [parts and factory review](factory-review.md) for the refreshed inventory,
panel corrections and outstanding factory confirmations.

## Remaining release gates

- Review the routed power layout and confirm the TI stencil apertures and JLC component orientations.
- Complete and test the PD/USB firmware, including detach, hard reset and voltage changes.
- Validate hot-plug/inrush, 3.3 V stability, switch temperature, 5 A copper/contact
  temperature, fault current, output discharge and backfeed with assembled boards.
- Resolve live MCU inventory for 20 devices plus assembly attrition.
- Confirm the actual JLC quote, allocations and five-panel assembly tier.

The Rev A source, generation scripts and all then-current outputs were archived
before changing the circuit. Rev B is preserved in Git commit `479ceb9`.
The routing and manufacturing-preview workflow now handles Rev C; revision and source checks reject stale layouts. The Rev A
programmer build remains preserved and refuses to build as Rev C.

## Generated files

- `hardware/review/ch32-pico.kicad_pcb`: saved Rev C routed review checkpoint.
- `hardware/review/validation.json`: router comparison and independent checks.
- `build/ch32-pico.kicad_sch`: generated schematic.
- `docs/images/ch32-pico.png`: front/back CAD render.
- `build/manufacturing-preview/`: single-board Gerber/BOM/CPL preview.
- `build/panel-preview/`: four-up KiKit PCB, Gerbers, BOM and CPL.
- `build/jlcpcb/`: factory-review inputs, with stock-shortfall notices.
- `firmware/pd/`: tested policy source and the remaining transport-integration requirements.

Rebuild with `just check`, `just route`, `just review`, `just render`,
`just manufacturing-preview`, `just panel-preview`, `just order-review` and
`just jlcpcb`, in that order. No command purchases parts or submits an
order. The preview manifests remain explicitly unreleased.

The BOOT resistor is next to D+ and isolates the longer button wire. The PD
output runs through the protected switch near the connector. The fixed buck
has explicit local switching, input-capacitor and feedback paths. These routes
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
