# Pre-order review

The board has 29 fitted parts and 20 exact part numbers, all on
the front. Five four-up panels contain 20 devices and 580 fitted placements.
The fitted-parts estimate is **$2.357 per board**,
$47.14 for the batch. Fabrication, assembly, attrition, minimum
purchases, inspection, shipping and tax are additional. No order or reservation
has been made. Schematic, routed-board and panel checks pass; matching exports are generated.

## Stock and purchasing

Observed 2026-10-19T01:30:24 UTC from JLCPCB public product pages.
These are dated catalog observations, not reservations, stock history or
confirmed assembly allocations. One observation cannot establish regular high
availability. LCSC stock was not independently rechecked in this snapshot.

Every fitted part number covers the provisional quantity below.
CH32X035C8T6 / C29779902 reports 1,082 units (1,066 orderable), up from two
in the previous snapshot; TVS2200DRVR reports 1,349. Obtain an exact-MPN
allocation and verify the MCU silicon lot for I2C and ADC3/ADC7; do not
substitute a different package without a new pinout and footprint review.

Provisional quantity is the larger of fitted quantity plus the displayed loss
count and the displayed assembly minimum. This assumes loss is charged once
per part number for the batch; the actual order may differ. Pre-purchase MOQ
is a separate purchasing route and is not applied to ordinary assembly here.

| Exact part | Per board | Provisional batch quantity | Reported stock | Shortfall |
|---|---:|---:|---:|---:|
| [C11702](https://jlcpcb.com/partdetail/C11702) / 0402WGF1001TCE | 1 | 30 | 21,648,372 | 0 |
| [C13585](https://jlcpcb.com/partdetail/C13585) / CL31A106KBHNNNE | 1 | 24 | 2,274,820 | 0 |
| [C2286](https://jlcpcb.com/partdetail/C2286) / KT-0603R | 1 | 30 | 8,538,700 | 0 |
| [C25741](https://jlcpcb.com/partdetail/C25741) / 0402WGF1003TCE | 2 | 50 | 9,330,303 | 0 |
| [C25744](https://jlcpcb.com/partdetail/C25744) / 0402WGF1002TCE | 2 | 50 | 21,126,626 | 0 |
| [C25756](https://jlcpcb.com/partdetail/C25756) / 0402WGF1502TCE | 1 | 30 | 1,990,403 | 0 |
| [C25792](https://jlcpcb.com/partdetail/C25792) / 0402WGF4702TCE | 1 | 30 | 7,048,006 | 0 |
| [C25900](https://jlcpcb.com/partdetail/C25900) / 0402WGF4701TCE | 1 | 30 | 15,932,328 | 0 |
| [C25905](https://jlcpcb.com/partdetail/C25905) / 0402WGF5101TCE | 2 | 50 | 5,072,603 | 0 |
| [C2927130](https://jlcpcb.com/partdetail/C2927130) / SY8301ABC | 1 | 20 | 20,409 | 0 |
| [C29277](https://jlcpcb.com/partdetail/C29277) / CL21A226MPQNNNE | 2 | 48 | 120,511 | 0 |
| [C29779902](https://jlcpcb.com/partdetail/C29779902) / CH32X035C8T6 | 1 | 20 | 1,082 | 0 |
| [C307331](https://jlcpcb.com/partdetail/C307331) / CL05B104KB54PNC | 4 | 90 | 23,901,866 | 0 |
| [C48496](https://jlcpcb.com/partdetail/C48496) / SWPA5040S4R7MT | 1 | 24 | 7,243 | 0 |
| [C523793](https://jlcpcb.com/partdetail/C523793) / TVS2200DRVR | 1 | 20 | 1,349 | 0 |
| [C52923](https://jlcpcb.com/partdetail/C52923) / CL05A105KA5NQNC | 1 | 30 | 8,983,823 | 0 |
| [C720477](https://jlcpcb.com/partdetail/C720477) / TS-1088-AR02016 | 2 | 44 | 623,546 | 0 |
| [C7519](https://jlcpcb.com/partdetail/C7519) / USBLC6-2SC6 | 1 | 22 | 33,175 | 0 |
| [C8598](https://jlcpcb.com/partdetail/C8598) / B5819W SL | 2 | 48 | 598,350 | 0 |
| [C963411](https://jlcpcb.com/partdetail/C963411) / GT-USB-7010AW | 1 | 20 | 1,099 | 0 |

This provisional parts scenario is $49.96, or
$2.50 per device, before the excluded costs above.
The machine-readable observations are in
[procurement-observation.json](../hardware/procurement-observation.json).
`just cost-review` and `just order-review` regenerate the detailed estimates.

Both buttons use C720477 / TS-1088-AR02016, a 2.0 mm, 1.6 N tactile switch
in JLC's Basic library. The 2.5 mm C720478 fits the same copper but showed no
stock for the order. The
[switch review](../hardware/research/switch-replacement.json) records its
dimensions, stock and sources.

## Electrical and manufacturing limits

Pin 40 is direct USB VBUS, as on the Pico, with a D5 input TVS clamp and a
50 V buck input capacitor.
See [pin 40 power](design.md#pin-40-is-usb-vbus) and the
[qualification plan](power-qualification.md) for required tests.

The 3 A target is unqualified. A 3 A input contract with the minimum 100 mA
board reserve allows at most 2.9 A for the external load. There is no on-board
current limit; the USB source's protection handles shorts. Unknown inductive
loads need an external driver and local suppression.
Native USB-PD application firmware and assembled-board testing remain open.

The four-layer JLC04101H-3313 board uses top-side assembly, ordinary tented
vias and no filled/capped via-in-pad. Castellations require Standard PCBA.
Use the generated 93 × 71 mm four-up panel; quote five panels, not twenty panels.
Review IC orientation, hidden-joint inspection, stencil, actual stackup,
USB-shell assembly, attrition and shipping with the factory. No quote or
supplier preview has approved the parts or placement.
