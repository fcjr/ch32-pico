# Revision E: optional PC7 and board diagnostics

Rev E adds a normally open solder jumper for header pin 35 and exposes the PD
switch's fault signal on the underside. Eleven additional probe contacts expose
the remaining internal MCU signals, raw VBUS and ground. Two local ground
stitching vias connect the USB-end pour to the internal ground plane. It keeps Rev D's regulator-enable
connection at pin 37, the 21 × 51 mm outline, 40 header positions, castellations
and edge-aligned USB-C. There are no mounting holes. The fitted BOM remains
41 parts. The power-path correction below changes the capacitor part and R17.

This is a routed prototype, not a manufacturing release. PD/USB application
firmware, physical power qualification and factory approval remain pending.
The [Rev D architecture](revision-d.md#selected-architecture) still describes
the MCU, USB, protected PD output and fixed 3.3 V supply.

## Power-path correction

All nine 100 nF capacitors now use Samsung CL05B104KB54PNC,
[LCSC C307331](https://www.lcsc.com/product-detail/C307331.html), a 50 V X7R
0402 part. The original C1525 was rated only 16 V despite the 50 V BOM label.
C5 and C12 see negotiated VBUS; C8 on dVdT requires a rating of at least
VIN + 5 V. The other six positions also use C307331 to keep one 100 nF BOM row.

R17 is now 4.7 kΩ, C25900, in parallel with the existing 1.5 kΩ R18.
The effective 1,137 Ω sets a nominal 2.93 A current limit using
[TI's TPS25947 equation](https://www.ti.com/lit/ds/symlink/tps25947.pdf).
This replaces the earlier 600 Ω / 5.56 A setting and the 5 A design goal in
the historical revision notes. IC and resistor tolerances can allow more than
3 A. This is not a guaranteed 3 A ceiling or a continuous output rating.

The locked connector and eFuse copper still needs thermal qualification.
At 3 A and an assumed hot 45 mΩ on-resistance, the switch alone dissipates
about 0.405 W. Qualify traces, vias, switch temperature and the actual pin-40
contact before assigning a load rating. Firmware must use the lower qualified
limit and allow for control-supply current and current-limit tolerance.
Current sensing must use the new ILM resistance when converting ADC voltage.

The footprints and copper are unchanged. Circuit checks reject underrated
high-voltage capacitors, misleading voltage labels and the old ILM network;
PCB and netlist checks also compare part identity and value with the source.

The [pre-order parts and power review](preorder-review.md) records the current
MCU shortage and additional startup, bypass, OVLO and transient-protection
issues. The 2.93 A nominal limit does not resolve those qualification items.

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
It connects to `PD_FAULT_N`: TPS259470L pin 4, CH32X035 PB4 at package pin 24,
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
| TP21 | PDEN | Back | PB2 / TPS259470L enable, default-low control signal |
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

The incremental route starts from the hash-checked Rev D board in Git commit
`23297c1`. It removes the obsolete PC7-to-TP7 traces, adds SJ1, and routes
GPIO35, PC7 and the new FAULT branch before the diagnostic connections, using
the pinned KiCadRoutingTools router. The two ground stitches use ordinary
tented vias; there is no filled/capped via-in-pad.
All other existing traces and vias must remain identical. Independent KiCad
checks verify connectivity, clearances, critical power/USB geometry, ground
reference, paste, and the updated silkscreen.

The routed board has 152 vias and 1,445.197 mm of trace
centerline. Source/PCB checks, regression tests and routed-board DRC
pass with zero open connections. Panel and export checks must also pass
before `just jlcpcb` creates the upload bundle. See [build setup](build.md) for
the uv/just environments and prerequisites.

## Generated files

```sh
just route-jumper
just review
just render
just jlcpcb
```

`just route-jumper` includes schematic, placement and regression checks. It
retrieves the pinned Rev D checkpoint from Git history, so a full clone with
that commit is required. `just route` remains available for routing the whole
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
four-up panels, 20 devices, with 164 top-side fitted placements per panel.
There is no underside assembly: test pads and SJ1 are bare copper features.
See the [factory review](factory-review.md) for stock, cost and approval limits.
