# Revision E: optional PC7 and board diagnostics

The cost-reduced Rev E groups the power circuit beside USB-C and pin 40,
places RESET and BOOT together at the bottom, and retains LEFT SHIFT LOGICAL
branding. It keeps the 21 × 51 mm outline, 40 header positions, castellations,
33 accessible GPIOs and native CH32 USB-PD. All 52 fitted parts remain on the
front. Four copper layers replace the earlier six-layer checkpoint.

The dated parts-only estimate is $5.69 per device for 20 devices, down from
$22.88. This excludes fabrication, assembly setup/feeders, attrition, minimum
purchases, shipping and tax. See the [recorded screen](../hardware/research/cost-down-screen.json).
The saved layout has zero DRC violations and zero unconnected nets; all 96 tests
pass. Matching panel and manufacturing exports are generated. No assembled-board current rating,
USB compliance result or production release exists.

## Power-path correction

MX26631DL replaces the costly TPS26630 plus separate ideal-diode controller.
Its BGATE/DRV outputs drive AON7264E Q1 and BSS138-7-F Q2 for reverse blocking.
The device operates at 4.5–40 V and has 60 V absolute-maximum input/output
ratings. Absolute maximum is not an operating voltage. MODE and PGTH are
grounded to retain current-limit fault detection and controlled recovery slew.

TPS3701 independently pulls SHDN low on low VBUS. It senses upstream of Q1
so shutdown cannot prevent the sense voltage from reaching its startup threshold.
R27/R28 are 82.5 kohm / 7.68 kohm, 0.1%, 25 ppm/C. Including a 100 C drift
allowance and input leakage, startup screens at 4.665–4.883 V and falling
thresholds at 4.630–4.765 V. A provisional hot-Q1 resistance screen leaves
about 4.515 V at U3 IN at the upper fault-current screen. Propagation delay,
fast collapse and transistor heating still require measurement. Weak 5 V sources
or cable loss can cause dropout; full current from every 5 V cable is not promised.

R17 = 11 kohm gives 3.636 A using the manufacturer's piecewise formula.
The datasheet's 24 kohm table and formula disagree. The ±15% engineering
allowance plus resistor tolerance/drift gives 3.001–4.311 A; this is not a
manufacturer-guaranteed range at 11 kohm. Qualify the purchased lot. R25 is
10 kohm, 0.1%, giving nominal 0.260 V/A above 2 A. Use the minimum monitor
gain plus resistor/ADC uncertainty for protection. R17 is never the ADC shunt.

MX26631 automatically retries faults. Firmware must latch PD_ENABLE low on
FAULT and require explicit re-arm, with a watchdog and default-off pull-down.
Test repeated fault heating if firmware stalls; hardware latch-off is not
provided. The portable PD policy is tested code, not a complete firmware image.

D5/D6 TVS2200 input/output clamps, D7 PMEG4030ER-QX negative clamp and the
50 V capacitors remain. C8 is 22 nF, nominal slew 2.29 V/ms and 8.73 ms to 20 V.
C12 is 4.7 uF/50 V X7R; C14/C16 are 1 uF/50 V. C5 and the separate controller's
C15 are removed. No 16 V C1525 is fitted. R20/R21 OVLO corners screen at
21.450–23.751 V. The specified TVS hot surge clamp is 28.35 V, within the
power-stage voltage envelope but not an arbitrary motor-energy rating.

The high-current path now stays near the USB end. USB VBUS pad escapes use
0.6 mm traces; local input/output spreads use parallel vias; the back-layer
output trunk is 1.8 mm with a 1.2 mm neck near pin 40. All are design geometry,
not a measured ampacity. U3 dissipates up to 0.45 W at 3 A using its 50 milliohm
resistance bound, plus external FET, copper and contact losses. Off-pad thermal
vias avoid paid filled/capped via-in-pad; exact-board temperature testing is essential.

The 3 A input-contract target leaves at most 2.9 A at pin 40 after the policy's
minimum 100 mA board reserve. Higher control/header load requires a larger
reserve. External motor drivers need local flyback/recirculation. No unknown
inductive load or sustained regeneration is qualified. R8 plus the divider can
take about 17.6 seconds to discharge 100 uF from 20 V to 0.8 V; wait for measured
discharge before changing voltage. See [qualification](power-qualification.md).

## Pin 35 and SJ1

Pin 35 is marked `PC7*`. The asterisk means that the normally open `SJ1` jumper
must be bridged with solder to connect PC7. SJ1 is on the back near the upper
middle of the board. Its two exposed pads have a 0.30 mm copper gap and no
paste apertures. The factory must leave it open.

With SJ1 open, header pin 35 connects only to one side of the jumper and is
isolated from the MCU and power rails. Bridging it exposes PC7 as a GPIO or the
one-wire PIOC connection without taking the SDI debug pins. Remove the solder
bridge to restore isolation. Turn off and disconnect all power before changing
it, then check continuity. This does not provide the Pico's ADC reference
function or an extra ADC input. Check any carrier connection to ADC_VREF before
bridging SJ1.

The old direct-PC7 pad, TP7, is now FAULT. PC7 remains reachable at the MCU side
of SJ1 even when the jumper is open; header access requires the solder bridge.
There are 33 independent free GPIOs: 26 normal header GPIOs, six underside GPIOs
and optional PC7. The fault signal is shared with board circuitry and is not
an additional unrestricted GPIO.

## FAULT pad

TP7 is labeled `FAULT`, in the second row of the underside expansion pads.
It connects to `PD_FAULT_N`: MX26631 pin 14, CH32X035 PB4 at package pin 24,
and the existing 10 kΩ pull-up to 3.3 V. The switch's fault indication is active
low. Use a high-impedance scope or 3.3 V-compatible input to observe it. Do not
drive it from an external output or directly attach a load. It is a diagnostic
signal, not an emergency-stop input or proof that PD OUT is safe to touch.
It is not a valid powered diagnostic when the 3.3 V rail is off.

## Shutdown control

Pin 37 is labeled `EN`. Grounding it disables the AP63203 regulator; releasing
it enables automatic startup. Use a dry contact or an appropriately rated
open-drain driver. The [Rev D shutdown-control notes](revision-d.md#shutdown-control)
apply unchanged, including the unspecified released EN voltage and unqualified
MCU back-power through CC, sense and external signal connections. Complete
shutdown/restart testing before treating this as a qualified power-off feature.

Pin 40 remains the switched 5–20 V PD output, off by default. Its voltage and
power behavior differ from the Pico's fixed USB VBUS connection.

## Header allocation

Top/component view, USB at the top. Pin numbers follow the original Pico.

| Pico pin | Pico function | Rev E net | MCU package pin | Function |
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
| 39 | VSYS | VSYS | — | 4.3-5.5 V input only; diode-isolated from PD VBUS |
| 40 | VBUS | PD_OUT | — | Switched negotiated 5-20 V output; incompatible with fixed-5V Pico carriers |

`GPIO35` names the isolated header-side copper, not another MCU GPIO.

## Peripheral access

The header UART, I2C, SPI, ADC and timer mappings are unchanged from
[Rev D's peripheral table](revision-d.md#peripheral-access). OPA connections
remain available on PB5/PB8 and the corresponding header pins. PC7/PIOC now
uses SJ1 instead of TP7.

| Back pad | Label | MCU package pin | Function |
|---|---|---:|---|
| TP6 | PC6 | 18 | GPIO, TIM1 complementary output |
| TP7 | FAULT | 24 | Shared PD switch diagnostic, active low; observe only |
| TP8 | PB5 | 25 | OPA1 output, timer break input |
| TP9 | PB8 | 28 | OPA1 positive input, TIM1 complementary output |
| TP10 | PB9 | 29 | Clock output, TIM1 channel 1 |
| TP11 | PB12 | 35 | TIM1 channel 4 remap |
| TP12 | PB13 | 36 | USART4 TX remap |
| TP13 | GND | 47 | Common ground |

## Diagnostic contacts

Every MCU signal is now reachable through a header, the PC7 jumper or a probe
contact. The reserved USB, PD, LED and measurement signals remain connected
to board circuitry; exposing them does not make them free GPIOs.

| Pad | Silk | Side | Connection and use |
|---|---|---|---|
| TP14 | ISNS | Back | PA3 / ADC3, filtered current-monitor voltage after R24 and C13 |
| TP15 | VBUS | Back | Raw USB input rail, 5–20 V; present even with PD OUT disabled |
| TP16 | GND | Back | Ground near the USB-end measurement pads |
| TP17 | VSNS | Back | PB0 / ADC8, filtered VBUS / 11 voltage |
| TP18 | OSNS | Back | PB1 / ADC9, filtered PD OUT / 11 voltage |
| TP19 | CC1 | Back | PC14, USB-C CC1 / PD communication |
| TP20 | CC2 | Back | PC15, USB-C CC2 / PD communication |
| TP21 | PDEN | Back | PB2 / eFuse enable interlock, default-low control signal |
| TP22 | PB3 | Back | MCU side of the application LED resistor R11 |
| TP23 | D+ | Front | PC17 / USB D+, inline probe contact |
| TP24 | D- | Front | PC16 / USB D−, inline probe contact |

Use high-impedance probes on these shared signals. Do not attach external
outputs to them while the MCU drives them. Loading ISNS can disturb the
current-limit measurement; it is not a precision current-output terminal.
VSNS and OSNS are nominally 1.82 V at a 20 V rail and are filtered by the existing
100 nF capacitors. They are measurements, not external ADC inputs. ADC3 still
requires the qualified MCU silicon lot described in Rev D.

VBUS is an unswitched high-voltage measurement pad, not another power-output
terminal. Its small probe branch is not sized for load current. Use header 40
for the protected output. PDEN can enable that output and must not be mistaken
for the regulator's EN on header 37. CC1/CC2 retain their existing pull-downs;
probe loading can disrupt USB-C attachment or PD communication.

The eight general measurement pads are 1 mm diameter. PB3 uses a 0.6 mm pad.
D+ and D− use 1 × 0.1537 mm exposed sections of their existing front-side traces,
with no added USB branches or vias. Use a fine low-capacitance probe. These
contacts are not intended as an alternate USB connector or flying-wire port.
All contacts have no paste and add no fitted parts.

## Layout and verification

The earlier jumper migration started from Rev D in commit `23297c1`.
The cost-reduced protection design uses a new placement and locked USB/power routing
seed, followed by the pinned Freerouting and KiCadRoutingTools routers. It uses ordinary
tented vias; there is no filled/capped via-in-pad. The eFuse exposed pad reaches
the ground planes through its GND/PGTH copper and adjacent off-pad vias. This
has less direct heat conduction than an array of vias under the exposed pad;
the 3 A target requires thermal testing on this exact assembly.
Independent KiCad
checks verify connectivity, clearances, critical power/USB geometry, ground
reference, paste, and the updated silkscreen.

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

`just route-jumper` is retained for the earlier jumper migration from Rev D
and rejects the current power-component changes.
`just route-power` reproduces the later power correction from its pinned
routing checkpoint and runs independent geometry checks. `just route` remains available for routing the whole
design from its generated seed. Earlier revision generators are retained.

- `hardware/review/ch32-pico.kicad_pcb`: checked Rev E board.
- `hardware/review/validation.json`: route, geometry and marking checks.
- `build/ch32-pico.kicad_sch`: current generated schematic.
- `docs/images/ch32-pico.png`: current front/back CAD render.
- `build/panel-preview/`: four-up panel, Gerbers, BOM and CPL.
- `build/jlcpcb/`: current upload inputs and factory notes.
- `build/ch32-pico-jlcpcb.zip`: complete JLCPCB fabrication bundle.

Use the Rev E files together. The earlier Rev C browser upload and the saved
Rev D export do not describe SJ1, FAULT or the diagnostic pads. Assembly quantity remains five
four-up panels, 20 devices, with 208 top-side fitted placements per panel.
There is no underside assembly: test pads and SJ1 are bare copper features.
See the [factory review](factory-review.md) for stock, cost and approval limits.


## Four-layer routing

The stack is JLC04101H-3313, nominal 1 mm, with 1 oz outer and 0.5 oz inner
copper. In1.Cu remains ground; In2.Cu carries 3.3 V pours and signals. The
0.0994 mm front-to-ground spacing is retained. Fitted components remain on
F.Cu. The checked layout has 193 vias and 1,774.969 mm of trace centerline,
zero DRC violations and no unconnected nets. Critical copper, USB ground
reference, pad/net parity and drill-to-paste checks pass. The four-up panel
and matching manufacturing exports are regenerated; old six-layer artifacts
are not current manufacturing inputs.
