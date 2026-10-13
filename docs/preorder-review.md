# Rev E parts, stock and power review

Reviewed 2026-10-13 for the current 20-board batch: five four-board panels.
There are 41 fitted components per board, 820 placements and 20 distinct
purchased part numbers. No boards have been assembled or thermally tested.

The batch cannot be fully assembled from the reported stock. The exact MCU,
CH32X035C8T6 / C29779902, has two pieces available against 20 required.
The other 19 part numbers cover the provisional quantities below. Two MCUs
do not cover even one four-board panel. No substitute or replenishment date
has been validated. Ask JLC to source and allocate the exact LQFP-48 MPN and
confirm the silicon lot needed for ADC3 and I2C before ordering assembly.

Follow-up sourcing found ICkey offers for the exact MCU reporting 235
pieces (minimum one) and 25,000 pieces (minimum 250). These are potential
external supply, not JLC assembly inventory. See the [MCU sourcing notes](mcu-alternatives.md)
for prices, consignment requirements and the unsent supplier inquiry.
Allocation, silicon lot and delivery to JLC remain unconfirmed.

The power path is also **not qualified for continuous use at any PD voltage**.
The current-limit change fixed the earlier excessive nominal threshold, but
the following review found additional work before claiming safe operation.
The proposed 2 A bench target below is not an approved operating rating.

## Current stock for every fitted part

JLC public inventory observed at 2026-10-13T14:15:39.076026+00:00.

| LCSC / exact MPN | Fitted / board | Fitted / batch | Provisional order qty | Reported stock | Shortfall |
|---|---:|---:|---:|---:|---:|
| [C11702](https://jlcpcb.com/partdetail/C11702) / 0402WGF1001TCE | 2 | 40 | 50 | 7,858,306 | 0 |
| [C13585](https://jlcpcb.com/partdetail/C13585) / CL31A106KBHNNNE | 1 | 20 | 24 | 2,155,314 | 0 |
| [C2286](https://jlcpcb.com/partdetail/C2286) / KT-0603R | 1 | 20 | 30 | 7,017,695 | 0 |
| [C25741](https://jlcpcb.com/partdetail/C25741) / 0402WGF1003TCE | 2 | 40 | 50 | 10,157,791 | 0 |
| [C25744](https://jlcpcb.com/partdetail/C25744) / 0402WGF1002TCE | 6 | 120 | 130 | 22,421,961 | 0 |
| [C25867](https://jlcpcb.com/partdetail/C25867) / 0402WGF1501TCE | 1 | 20 | 30 | 1,929,472 | 0 |
| [C25900](https://jlcpcb.com/partdetail/C25900) / 0402WGF4701TCE | 3 | 60 | 70 | 16,587,237 | 0 |
| [C25905](https://jlcpcb.com/partdetail/C25905) / 0402WGF5101TCE | 2 | 40 | 50 | 5,430,099 | 0 |
| [C29277](https://jlcpcb.com/partdetail/C29277) / CL21A226MPQNNNE | 2 | 40 | 40 | 278,825 | 0 |
| [C29779902](https://jlcpcb.com/partdetail/C29779902) / CH32X035C8T6 | 1 | 20 | 20 | 2 | 18 |
| [C307331](https://jlcpcb.com/partdetail/C307331) / CL05B104KB54PNC | 9 | 180 | 190 | 15,043,347 | 0 |
| [C3662793](https://jlcpcb.com/partdetail/C3662793) / TPS259470LRPWR | 1 | 20 | 20 | 523 | 0 |
| [C4142](https://jlcpcb.com/partdetail/C4142) / 0402WGF8202TCE | 1 | 20 | 30 | 26,683 | 0 |
| [C48496](https://jlcpcb.com/partdetail/C48496) / SWPA5040S4R7MT | 1 | 20 | 24 | 7,361 | 0 |
| [C52923](https://jlcpcb.com/partdetail/C52923) / CL05A105KA5NQNC | 1 | 20 | 30 | 7,772,334 | 0 |
| [C720477](https://jlcpcb.com/partdetail/C720477) / TS-1088-AR02016 | 2 | 40 | 44 | 697,846 | 0 |
| [C7519](https://jlcpcb.com/partdetail/C7519) / USBLC6-2SC6 | 1 | 20 | 22 | 42,788 | 0 |
| [C780769](https://jlcpcb.com/partdetail/C780769) / AP63203WU-7 | 1 | 20 | 20 | 8,099 | 0 |
| [C8598](https://jlcpcb.com/partdetail/C8598) / B5819W SL | 2 | 40 | 48 | 383,322 | 0 |
| [C963411](https://jlcpcb.com/partdetail/C963411) / GT-USB-7010AW | 1 | 20 | 20 | 1,109 | 0 |

Fitted parts estimate: $79.4540 per batch. With provisional attrition: $81.6224. These are parts-only estimates; they exclude PCB fabrication, assembly, sourcing uplifts, shipping and tax.

Quantities include JLC's displayed attrition/minimum fields using
`max(fitted + displayed loss count, displayed assembly minimum)` once per
part number for the batch. This is a provisional planning rule, not confirmed
order attrition. The exact C-number and MPN were matched in each public JLC
response. These are assembly-library stocks, not reserved parts or LCSC retail
stock. The attempted independent LCSC MCU refresh was blocked by HTTP 403;
the earlier LCSC observation is not treated as a fresh stock check.

Evidence: [dated stock snapshot](../hardware/procurement-observation.json),
with response hashes and price tiers. `just procurement` refreshes it;
`just order-review` recalculates batch requirements. JLC must confirm actual
allocation, charged quantities and assembly eligibility during quoting.

J1 is bare header/castellated copper and is not a fitted connector. Header
pins, mating sockets, carrier, USB cable and external load are not included
in these stock quantities. Their exact parts and current ratings remain
unspecified. Test pads and SJ1 require no purchased components.

## Electrical review by component group

| Parts | Finding |
|---|---|
| C4/C5/C6/C8/C9/C10/C11/C12/C13 | C307331 is 100 nF, 50 V, X7R, 0402. The earlier 16 V mismatch is fixed. Effective capacitance under DC bias still needs review, particularly C8 and C12. |
| C1 | 10 µF / 50 V on VIN_SYS. Voltage margin is adequate for nominal 20 V. It charges through D1 before U3, so the eFuse slew control does not limit its input inrush. |
| C2/C3; C7 | 22 µF / 10 V and 1 µF / 25 V on 3.3 V. Nominal voltage ratings have margin; verify buck ripple, DC-bias capacitance and startup. |
| U3, R17/R18 | Correct adjustable-OVLO, latch-off TPS259470L variant. Current threshold screens at 2.613–3.258 A with IC and 1% resistor tolerance. A 3 A continuous load is not guaranteed to stay below current limit. |
| C8 | 100 nF directly on dVdT exceeds TI's 10 nF threshold for recommending a 100 Ω series resistor. Nominal 20 V rise time is about one second. Redesign or add the resistor and validate loaded startup. |
| C12 | 0.1 µF nominal, below TI's recommended ≥1 µF output bypass. Review a suitable higher-capacitance, high-voltage part and its effective capacitance. |
| R20/R21 | OVLO is 22.14 V nominal. Comparator/resistor tolerance and +100 nA pin leakage can put the rising threshold at about 23.000 V. There is essentially no static margin below U3's 23 V operating limit; temperature drift and transients remain. |
| R1/R2/R5/R6, C9/C10 | Dividers give about 1.94 V at 21 V with worst 1% divider ratio, below a powered 3.3 V rail. R1/R5 dissipation is only a few mW. Powered-off injection into the MCU remains unqualified. |
| R8 | Bleed resistor dissipates 40 mW at 20 V nominal, or 44.55 mW at 21 V and -1% resistance, against 62.5 mW nominal rating. Check temperature derating and discharge time with the maximum external capacitance. |
| U4, L1, D1/D4 | AP63203 supports 3.8–32 V input; the 40 V / 1 A diodes carry only control-supply current. Check 5 V cable/diode drop, cold startup, inductor peak current/saturation and buck faults. The 50 mA header bring-up budget is not a qualified 3.3 V rating. |
| J2 | The selected manufacturer's drawing specifies 5 A VBUS. That does not rate the adjoining traces, vias, solder joints or pin-40 connection. Verify both plug orientations and cable fit. |
| U1 | Correct LQFP-48 MCU and native PD function. Exact-MPN stock shortage; silicon-lot confirmation is still needed. USB-PD transport, ADC calibration and watchdog application are not integrated. |
| D2, C11 | USBLC6-2SC6 clamps USB data to the fixed 3.3 V rail. It does not protect raw VBUS, CC pins or PD_OUT from power transients. |
| R3/R4 | Separate 5.1 kΩ CC pull-downs. Normal CC signaling is low voltage; they are not protection against a VBUS-to-CC fault. |
| R7/R9/R10 | Low-voltage gate default-off, fault pull-up and reset pull-up. Check actual reset, shutdown and unpowered behavior. |
| R11/D3, R12/SW2, SW1 | Low-voltage LED, boot and reset networks. No new high-voltage rating mismatch found. Verify polarity, boot entry and reset on assembled boards. |
| R24/C13 | Current-monitor filter. ADC conversion must use 1,137 Ω and account for gain, resistor and ADC error. The long ILM route and filter loading need review. |

Component evidence includes [C307331](https://www.lcsc.com/product-detail/C307331.html),
[R8's 62.5 mW rating](https://www.lcsc.com/product-detail/C25744.html),
[D1/D4 ratings](https://www.lcsc.com/product-detail/C8598.html),
[AP63203 specifications](https://www.diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf),
and the local [connector drawing provenance](../hardware/research/rev-b-sources.json).
The inductor saturation/temperature curve and final 3.3 V load envelope remain
open; a stock match does not establish those margins.

## Continuous current and startup

Supported requests are fixed 5, 9, 12, 15 and 20 V. PPS/AVS and EPR 28/36/48 V
are not supported. A source need not offer every requested voltage, including
12 V. Firmware must refuse absent modes rather than substitute a voltage.

At 45 mΩ, switch conduction loss is 0.180 W at 2 A, 0.281 W at 2.5 A and
0.405 W at 3 A. Multiplying by the datasheet's JEDEC 74.5 °C/W gives example
rises of 13.4, 21.0 and 30.2 °C. These are not predictions for this small PCB.
The actual copper, mounting, airflow and adjacent heat determine its thermal
resistance. [TI explains the limitations of these thermal metrics](https://www.ti.com/lit/an/spra953d/spra953d.pdf).

The original estimate of an 80 °C rise at 5 A likewise uses a reference board,
not a measurement. Adding parallel widths does not establish equal current
sharing. The 0.32 mm USB stubs, 0.30 mm U3 escapes, vias and ground return
need a current-distribution and thermal review. No IPC trace-width calculation
alone qualifies these short, connected copper structures.

Startup can dominate steady heating. Using TI's nominal slew equation with
100 nF gives 0.020 V/ms. For an illustrative resistor drawing 2 A at the final
voltage, an ideal linear ramp produces the following calculated switch stress:

| Output | Nominal ramp | Peak ramp loss | Ramp energy | Qualified continuous current |
|---:|---:|---:|---:|---|
| 5 V | 250 ms | 2.5 W | 0.417 J | None |
| 9 V | 450 ms | 4.5 W | 1.350 J | None |
| 12 V | 600 ms | 6.0 W | 2.400 J | None |
| 15 V | 750 ms | 7.5 W | 3.750 J | None |
| 20 V | 1,000 ms | 10.0 W | 6.667 J | None |

These are analytical demands, not a safe-operating-area result. Thermal
shutdown or foldback can interrupt the assumed ramp; capacitive or constant
power loads behave differently. See [TI sections 7.3.5, 8.3 and 8.4](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
for slew control, transient protection and layout requirements. The current
board has no VBUS TVS or output negative-transient clamp. OVLO disconnects
the output; it cannot clamp the voltage applied to U3's input.

The saved board has about 57.5 mm of total PD_ILM track and four vias, including
the remote ADC-filter branch. Length alone does not prove excessive capacitance,
but it needs review against TI's local-component and <50 pF parasitic guidance.
The standalone policy accepts caller-supplied limits up to 5 A; it must not be
used as an application-level board rating.

## Required qualification work

First resolve C8 timing/series resistance, C12 bypass, OVLO margin, transient
protection and ILM layout. Select the exact output contact/carrier, maximum
external capacitance, allowable load type and environmental envelope. Keep
the output off by default and complete PD/ADC/watchdog integration. No released
continuous current can be assigned while these conditions are unspecified.

For initial characterization, use at least three boards from different panel
positions. A proposed starting envelope is an open board in still air at
25 °C and 40 °C ambient; an enclosure or higher ambient needs separate testing.
Begin with a current-limited bench supply and low load. Progress through 0.1,
0.5, 1.0, 1.5 and at most 2.0 A only while temperatures, ripple and voltages
remain acceptable. Do not jump directly to 2 A. The 2 A endpoint is an
engineering test target, not permission to operate the present circuit there.

Test every supported voltage, both USB orientations, representative cables,
the chosen header/carrier and ground return, and maximum 3.3 V loading.
Record input/output voltage and current, drop across each bottleneck, ambient,
U3 top temperature, connector contacts, vias, copper necks, R8, D1, U4 and L1.
Hold each final load for at least one hour and until temperature changes by
less than 1 °C over ten minutes. Proposed engineering acceptance limits are
≤20 °C connector/trace rise, all parts below their derated ratings, and an
estimated U3 junction temperature ≤110 °C using a validated measurement method.
These limits do not establish touch-temperature or regulatory compliance.

Separately scope loaded startup, load steps, detach, hard reset, renegotiation,
brownout, shutdown/restart, and controlled overload/short-circuit recovery.
Check U3 input/output transients against recommended and absolute limits;
test the specified capacitive and active loads. Characterize current-limit
tolerance and ADC error, then set the firmware budget below the lowest
demonstrated hardware limit and subtract control-supply consumption from the
negotiated input current. Use the lowest passing rating across all modes,
boards, contacts and environments. Leave any untested configuration unrated.

`just power-review` regenerates the calculation in `build/power-review.json`.
Factory bundles include it under the manufacturing manifest's power estimates.
Passing ERC/DRC and the software regressions verifies the generated files;
it does not close these physical qualification items.
