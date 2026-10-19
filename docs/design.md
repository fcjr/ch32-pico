# Rev A: design, pinout and limits

ch32-pico places a CH32X035C8T6 on the 21 × 51 mm Pico outline with 40 header
positions, castellations and native CH32 USB-PD. The power circuit sits beside
USB-C, RESET and BOOT sit together at the bottom, and the back carries LEFT
SHIFT LOGICAL branding. All 29 fitted parts are on the front. The board has
four copper layers and exposes 37 GPIOs.

The dated parts-only estimate is $2.36 per device for 20 devices. This
excludes fabrication, assembly setup/feeders, attrition, minimum purchases,
shipping and tax. The saved layout has zero DRC violations and zero
unconnected nets, and all regression tests pass. Matching panel and
manufacturing exports are generated. No assembled-board current rating, USB
compliance result or production release exists.

## Placement

USB-C sits at the top edge with its ESD diode, CC pull-downs, VBUS clamp and
the status LED beside it. The 3.3 V buck, its diode-OR inputs and the VBUS
sense divider occupy the band directly below, next to header pins 36, 37 and
39 that they serve. The MCU is centred on the GPIO rows at y = 28 mm with its
decoupling at the supply corner, so the two header columns and the USB pair
reach it with similar lengths. RESET, BOOT and the SDI pads line the bottom
edge, with the SJ1 solder jumper beside the right header row just below the
MCU. The back carries the GPIO expansion and probe pads.

## Pin 40 is USB VBUS

Pin 40 connects directly to USB-C VBUS, as on the Pico. Every source starts
at 5 V, so pin 40 is 5 V by default. It rises to 9, 12, 15 or 20 V only after
firmware requests that contract, and returns to 5 V after detach or a PD hard
reset. A carrier on pin 40 must tolerate every voltage the firmware may request.

As on the Pico, there is no switch, current limit or reverse blocking on
pin 40:

- The USB source's own overcurrent protection is the only short-circuit limit.
- A hung MCU leaves the last negotiated voltage on pin 40.
- Do not power pin 40 from another supply while USB is connected; nothing
  blocks that supply from reaching the USB source.
- Large carrier capacitance draws inrush at attach and during PD voltage
  changes. Some sources may reset.

D5 (TVS2200, 22 V standoff, 28.35 V specified hot surge clamp) sits at the
USB VBUS breakout. Plugging a cable into a source already at 20 V can ring
toward twice the supply. D5 keeps that below U4's 40 V input rating. It
protects the board's own regulator; it is not a motor-energy
rating for pin 40. External motor drivers need local flyback/recirculation.

R1/R2 divide VBUS by 11 into PB0 (VSNS), so firmware can confirm the
negotiated voltage. D1 feeds the 3.3 V buck from VBUS; D4 feeds it from
VSYS. Header pin 39 VSYS is a 4.3–5.5 V input only, diode-isolated from VBUS.

## 3.3 V regulator

U4 is a Silergy SY8301: a 2 MHz synchronous buck rated for 4.5–40 V input and
1 A, with 22 µA quiescent current. R13/R14 (47 kΩ / 15 kΩ) set the output to
0.8 V × (1 + 47/15) = 3.31 V; R13 senses the output capacitors over a
dedicated bottom-layer trace, away from the shared 3.3 V pour. L1 is 4.7 µH
(about 0.29 A ripple at 20 V in), C1 10 µF/50 V at the input, C2/C3 2 × 22 µF
at the output and C4 100 nF between BS and LX. The 2.5 A peak current limit and
hiccup short-circuit protection are the regulator's; the board's 3.3 V load
goal is 50 mA at the header plus the MCU, so the 1 A rating is not the limit.
IN and GND sit on opposite sides of the SOT-23-6, so the input loop closes
through the ground plane with vias beside both C1 and the IC's ground pin.

The high-current path stays near the USB end. Both VBUS contacts reach a
0.9 mm bottom- and inner-layer bar through four vias, and a 1.2 mm bottom-layer
trunk runs from there to pin 40 (12.64 mm). The right-hand VBUS contact also
feeds pin 40 directly on the front layer: a 0.4 mm neck past the connector's
locating peg, then 0.8 mm between the shell stakes (11.42 mm). Neither contact
depends on a single via. This is design geometry, not a measured ampacity. The
3 A target still needs connector, via, trunk and contact temperature testing.
See [qualification](power-qualification.md).

## Pin 35 and SJ1

Pin 35 is marked `PC7*`. The asterisk means that the normally open `SJ1` jumper
must be bridged with solder to connect PC7. SJ1 is on the front, beside the
right header row just below the MCU. Its two exposed pads have a 0.30 mm copper gap and no
paste apertures. The factory must leave it open.

With SJ1 open, header pin 35 connects only to one side of the jumper and is
isolated from the MCU and power rails. Bridging it exposes PC7 as a GPIO or the
one-wire PIOC connection without taking the SDI debug pins. Remove the solder
bridge to restore isolation. Turn off and disconnect all power before changing
it, then check continuity. This does not provide the Pico's ADC reference
function or an extra ADC input. Check any carrier connection to ADC_VREF before
bridging SJ1.

There are 37 independent free GPIOs: 26 normal header GPIOs, seven underside
expansion pads, three underside probe pads (PA3, PB1, PB2) and optional PC7.
`GPIO35` names the isolated header-side copper, not another MCU GPIO.

## Shutdown control

Pico header pin 37, labeled `EN`, connects to U4's EN pin, which R15 (100 kΩ)
pulls up to VIN_SYS, the diode-OR of VBUS and VSYS, so the regulator starts on
either supply with pin 37 open. Grounding pin 37 disables the converter;
releasing it starts a new soft-start. The EN thresholds are 1.4 V rising and
1.0 V falling, and the pin is rated to 40 V.

The released pin sits at VIN_SYS: about 4.5 V on a plain USB supply, up to
about 19.7 V after a 20 V PD contract, through 100 kΩ. That is higher than the
Pico, whose 3V3_EN floats at VSYS. Use a dry-contact switch between pins 37
and 38, or an external open-drain transistor rated at least 40 V with its
source/emitter at board ground. A 3.3 V push-pull driver can hold the pin
high or low and sinks at most 200 µA, but do not connect pin 37 to a logic
input, and do not add another pull-up.

Shutdown removes the MCU and header 3.3 V supply. It stops USB and PD control
once the rail discharges; it is not galvanic isolation or an emergency stop,
and it does not remove VBUS from pin 40. Power applied externally to 3V3 or
through signal/debug pins can keep the MCU alive and defeat shutdown. The CC
pins and the VBUS sense divider stay connected while off. Their off-state
injection/back-power must be checked against WCH electrical limits; a zero-volt
MCU rail and reliable cold restart are not yet qualified. The WCH datasheet
lists an I/O limit of VDD + 0.3 V without a separate powered-off tolerance
guarantee. Validate this before using shutdown as a released feature.

Before release, test cold startup with EN open and held low, repeated release,
all supported USB/VSYS input conditions, low-leakage and partially powered
external drivers, USB disconnect/re-enumeration and signal back-power. Board
standby current is not the regulator's shutdown current alone; the EN pull-up,
sense divider and CC terminations still draw current.

Source: [SY8301 datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2207131830_Silergy-Corp-SY8301ABC_C2927130.pdf), pin descriptions, electrical characteristics and layout notes.

## Header allocation

Top/component view, USB at the top. Pin numbers follow the original Pico.

| Pico pin | Pico function | Net | MCU package pin | Function |
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
| 35 | ADC_VREF | GPIO35 | — | Isolated by open SJ1; bridge SJ1 for PC7 GPIO / one-wire PIOC |
| 36 | 3V3_OUT | 3V3_OUT | — | Fixed 3.3 V output; prototype load rating pending |
| 37 | 3V3_EN | 3V3_EN | — | Pull low to shut down 3.3 V; release for automatic startup |
| 38 | GND | GND | — | Ground |
| 39 | VSYS | VSYS | — | 4.3-5.5 V input only; diode-isolated from VBUS |
| 40 | VBUS | VBUS | — | USB VBUS, 5 V by default; follows any higher PD contract firmware requests |

## Peripheral access

This is a board-level assessment against WCH datasheet v1.7, table 2-1.
A peripheral listed in the chip's feature list does not necessarily have a
free connection on this board. Alternate functions share pins and cannot all
operate together.

| Function | Access |
|---|---|
| ADC / touch sensing | Seven header inputs: PA0, PA1, PA2, PA4, PA5, PA6 and PA7. ADC3 (PA3) and ADC9 (PB1) are free on back pads; ADC8 (PB0) monitors VBUS. The LQFP48 package does not expose ADC10–13. |
| OPA1 | Available through PB8 positive input and PB5 output on back pads, with negative input choices PA1/PA6/PB6 on the main headers. |
| OPA2 | Usable through header pins, for example PA7 positive input, PA5 negative input and PA4 output. These share SPI/ADC pins. |
| USART1 / USART2 / USART4 | Header TX/RX pairs exist: PB10/PB11; PA15/PA16 with USART2 remap 2; PA5/PA9 with USART4 remap 1. Flow-control and synchronous-clock availability varies with mapping. |
| USART3 | PB4 on TP7 is the default RX; alternate RX is PC19 at the SDCK test pad. PA18 can supply remapped TX. Using PC19 sacrifices simultaneous SDI debugging. |
| PIOC programmable I/O | Two-wire operation uses PC18/PC19 at SDIO/SDCK and shares debugging. PC7 through SJ1 provides the alternative one-wire connection without taking those debug pins. |
| Timers / PWM | Header timer functions remain, with PB9 TIM1_CH1 and PB12 remapped TIM1_CH4 on back pads. Select a compatible remap for the complete timer; alternate functions are not all simultaneous. |
| Clock output | MCO is available on PB9 at TP10. |
| Comparators | Header input choices remain for all three. CMP1 output is PA1; CMP2 output is PB2 on TP21; CMP3 output is PB3, assigned to the LED. Internal timer-trigger uses do not need an output pin. |
| USB / USB PD | Connected to USB-C, not free header GPIO. The board is a PD sink; USB host power sourcing and PD source/DRP operation are not provided. |
| Core, memory, DMA, watchdogs | No additional external pins needed. |

Pin 37 controls the regulator directly and consumes no MCU GPIO.

| Back pad | Label | MCU package pin | Function |
|---|---|---:|---|
| TP6 | PC6 | 18 | GPIO, TIM1 complementary output |
| TP7 | PB4 | 24 | GPIO, USART3 RX |
| TP8 | PB5 | 25 | OPA1 output, timer break input |
| TP9 | PB8 | 28 | OPA1 positive input, TIM1 complementary output |
| TP10 | PB9 | 29 | Clock output, TIM1 channel 1 |
| TP11 | PB12 | 35 | TIM1 channel 4 remap |
| TP12 | PB13 | 36 | USART4 TX remap |
| TP13 | GND | 47 | Common ground |

## Diagnostic contacts

Every MCU signal is reachable through a header, the PC7 jumper or a probe
contact. The reserved USB, CC, LED and VBUS-sense signals remain connected
to board circuitry; exposing them does not make them free GPIOs.

| Pad | Silk | Side | Connection and use |
|---|---|---|---|
| TP14 | PA3 | Back | PA3 / ADC3, free GPIO |
| TP15 | VBUS | Back | USB VBUS, 5–20 V; same rail as header pin 40 |
| TP16 | GND | Back | Ground near the USB-end measurement pads |
| TP17 | VSNS | Back | PB0 / ADC8, filtered VBUS / 11 voltage |
| TP18 | PB1 | Back | PB1 / ADC9, free GPIO |
| TP19 | CC1 | Back | PC14, USB-C CC1 / PD communication |
| TP20 | CC2 | Back | PC15, USB-C CC2 / PD communication |
| TP21 | PB2 | Back | PB2, free GPIO |
| TP22 | PB3 | Back | MCU side of the application LED resistor R11 |
| TP23 | D+ | Front | PC17 / USB D+, inline probe contact |
| TP24 | D- | Front | PC16 / USB D−, inline probe contact |

Use high-impedance probes on these shared signals. Do not attach external
outputs to them while the MCU drives them. VSNS is nominally 1.82 V at a 20 V
rail and is filtered by the existing 100 nF capacitor. It is a measurement, not
an external ADC input. ADC3 on PA3 requires an MCU silicon lot that supports
it; see [factory notes](factory-notes.txt).

VBUS is a high-voltage measurement pad, not another power-output terminal.
Its small probe branch is not sized for load current; use header 40.
CC1/CC2 retain their existing pull-downs; probe loading can disrupt USB-C
attachment or PD communication.

The eight underside diagnostic and GPIO pads are 1 mm diameter. PB3 uses a 0.6 mm pad.
D+ and D− use 1 × 0.1537 mm exposed sections of their existing front-side traces,
with no added USB branches or vias. Use a fine low-capacitance probe. These
contacts are not intended as an alternate USB connector or flying-wire port.
All contacts have no paste and add no fitted parts.

## Layout and verification

The layout starts from a code-defined placement and locked USB/power routing
seed, followed by the pinned Freerouting and KiCadRoutingTools routers; the
Freerouting result was kept. It uses ordinary tented vias; there is no
filled/capped via-in-pad. Independent KiCad checks verify connectivity,
clearances, critical power/USB geometry, ground reference, paste and the
silkscreen.

The saved validation report records the current via count, trace length,
source parity and DRC result. Panel and export checks must also pass
before `just jlcpcb` creates the upload bundle. See [build setup](build.md) for
the uv/just environments and prerequisites.

## Generated files

```sh
just route-power
just review
just render
just jlcpcb
```

`just route-power` reproduces the checked layout from its pinned routing
checkpoint and runs independent geometry checks. `just route` remains available
for routing the whole design from its generated seed.

- `hardware/review/ch32-pico.kicad_pcb`: checked board.
- `hardware/review/validation.json`: route, geometry and marking checks.
- `build/ch32-pico.kicad_sch`: current generated schematic.
- `docs/images/ch32-pico.png`: current front/back CAD render.
- `build/panel-preview/`: four-up panel, Gerbers, BOM and CPL.
- `build/jlcpcb/`: current upload inputs and factory notes.
- `build/ch32-pico-jlcpcb.zip`: complete JLCPCB fabrication bundle.

Assembly quantity is five four-up panels, 20 devices, with 116 top-side fitted
placements per panel. There is no underside assembly: test pads and SJ1 are
bare copper features. See the [factory review](factory-review.md) for stock,
cost and approval limits.

## Four-layer routing

The stack is JLC04101H-3313, nominal 1 mm, with 1 oz outer and 0.5 oz inner
copper. In1.Cu is an unbroken ground reference; In2.Cu carries 3.3 V pours
and signals. The 0.0994 mm front-to-ground
spacing is retained. Fitted components are on F.Cu. The checked layout has
131 vias and 1,266.899 mm of trace centerline, zero DRC violations and no
unconnected nets. Critical copper, USB ground reference, pad/net parity and
drill-to-paste checks pass.

D5 sits at the USB VBUS breakout, with a 4.235 mm direct front-layer
connection from the adjacent VBUS contact. Its exposed pad has two local
ground vias reached through at least 0.4 mm front copper within 2.5 mm.
The 1.2 mm bottom trunk passes below the connector-region ground stitch and
follows the right edge to pin 40; the 0.8 mm front feed crosses under the
connector between its shell stakes. A locked 0.6 mm trunk on the 3.3 V
layer joins the regulator output to a via at the MCU's decoupling capacitor
and to header pin 36, so the rail never depends on router-width taps between
fragments of the shared pour; the pour itself is one polygon on this route.
VSYS reaches D4 at 0.4 mm. All 27 ground vias and the eight header ground
pins reach one connected, refilled L2 polygon. Fifteen tented stitching vias
tie the back pour to the ground plane on a clearance-filtered grid, so no
point of that pour is more than 6 mm from a ground via or pin. Vias remain
outside paste; no filled or capped via process is introduced. No signal is routed on L2; the USB reference is
covered at every audited sample. This is geometry, not an EMC qualification.
Surge, thermal and continuous-current qualification still require assembled boards.

The silkscreen uses consistent 0.8 mm header legends, with leaders identifying
pins 1 and 40 around the USB mounting stakes. CC labels share a baseline, and
every probe label is closer to its own pad than to any other. Probe-label
audits compare every test pad on the same side, including the expansion pads,
and reject missing top-pin leaders.
