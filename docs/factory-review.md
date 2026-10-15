# Parts and factory review

The current cost-reduced Rev E has 52 fitted parts, 31 part numbers and a
$5.69 parts-only estimate at 20 boards. The [current pre-order review](preorder-review.md)
contains the 2026-10-14 stock table and cost assumptions. The MCU still has
only two reported units; no parts are reserved. See [Rev E](revision-e.md) for
the power circuit, placement and qualification limits, and [factory notes](factory-notes.txt)
for the current manufacturing instructions. The routed board and generated panel pass checks; matching exports are generated.

## Historical factory observations

Everything below records earlier circuits and uploads. Part counts, prices,
stock, circuit descriptions and approvals in this section are historical and
must not be used to order the cost-reduced board.

## Rev E update

Rev E exposes PC7 on header 35 only through normally open SJ1 and changes TP7
from PC7 to FAULT. TP14–TP24 add eleven diagnostic contacts; two tented
ground vias stitch the USB-end pour to L2. Silkscreen identifies every new
contact and reads PC7*, SJ1, FAULT and REV E. Assembly placement and the panel
process are unchanged; SJ1 receives no paste or
factory solder bridge. `just jlcpcb` creates the current Rev E fabrication files in `build/jlcpcb/`. No Rev E
factory upload, allocation or approval has been performed. See the
[Rev E design and usage notes](revision-e.md).

The subsequent [power-path correction](revision-e.md#power-path-correction)
uses seven 50 V 100 nF capacitors, a 1 nF C0G C8, a larger 4.7 µF C12,
a single 1.13 kΩ R17 and precision OVLO resistors. R18 is removed. There
are now 40 fitted parts per board. C5/C8/C12/D4/R4/R17/R24 placement and
routing changed. Review the regenerated BOM/CPL and factory preview.
The Rev C quantities and prices below are historical and predate this correction.
C307331's separate dated stock observation is recorded in
`hardware/procurement-observation.json`; the current quantity and cost reports
are generated under `build/order-review/`.

## Rev D update

Rev D adds pin 37 regulator shutdown and updates its back label to `EN` and
the front revision to `REV D`. The BOM, placement, panel process and part
requirements remain unchanged. See [Rev D shutdown control](revision-d.md#shutdown-control)
for operation, external-driver requirements and remaining bench tests.
The Rev D upload bundle has since been superseded by Rev E. The Rev C upload observation
below does not validate the new files. No Rev D factory upload or approval has
been performed.

## Rev C review record

Reviewed 2026-10-13 UTC for five four-up panels, 20 devices. Local fabrication
and assembly-file checks pass after the corrections below. **Factory approval
and component allocation are still pending.** No order, payment or reservation
has been made.

## Corrections from this review

- Enlarged all functional silkscreen to at least 1.0 mm high with 0.15 mm strokes.
  Moved labels clear of header pads and USB shell stakes. Corner pins have
  explicit numbers; header and expansion-pad mappings still pass the net audit.
- Increased both short-end breakaway tabs to 5 mm. The USB-end tab starts at
  the left corner and clears the socket in the final milled outline. Reduced
  nominal mouse-bite pitch from 1.0 to 0.8 mm, with 0.5 mm drills.
- Changed rail tooling from 1.152 to 2 mm NPTH for the Standard process-edge
  recommendation. Kept the 7 mm rails and 93 x 71 mm panel envelope.
- Enlarged fiducial mask openings from 1 to 2 mm around 1 mm copper dots.
  Moved centers from 3.5 to 4.5 mm inward, leaving 3.5 mm beyond the opening.
  A new geometry check rejects the former openings, positions and tooling.
- Fixed the assembly guide's obsolete 132-placement label. It checks 164
  placements per panel and identifies Rev C. Added hidden-joint X-ray to the
  explicit cost exclusions and supplied detailed factory notes.

The dimensional targets come from JLC's [PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities),
[process-edge guidance](https://jlcpcb.com/help/article/specifications-for-adding-process-edges-and-positioning-holes)
and [Standard PCBA fiducial guidance](https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order).
The individual board's copper, parts, outline and pinout are unchanged.

## Parts

All 20 distinct fitted C-numbers match the expected MPN in JLC's public catalogue.
There are 41 fitted parts per device and 21 BOM rows, because one part number
appears under two circuit descriptions. The batch has 820 placements.

Nineteen C-numbers have enough reported stock for the provisional attrition
scenario. **C29779902 / CH32X035C8T6 has only two pieces, leaving 18 short.**
The [LCSC page](https://www.lcsc.com/product-detail/C29779902.html) independently
shows two pieces too. No alternative supplier offer or replenishment date was
shown. Neither observation reserves stock or proves JLC allocation.

Use JLC sourcing for the exact MPN and package, or wait for replenishment.
Do not replace it with another X035 package without a new pinout and footprint
review. Require a lot supporting I2C and ADC3/ADC7: the early-silicon restriction
in [WCH datasheet v1.7, table 2-1 note 3](https://akizukidenshi.com/goodsaffix/CH32X035.pdf)
affects functions used on this board. Catalogue stock does not identify the lot.
The factory must provide lot identification; bring-up must exercise those functions.

| LCSC part | Exact MPN | Fitted batch qty | Provisional qty | JLC stock | Shortfall |
|---|---|---:|---:|---:|---:|
| [C11702](https://jlcpcb.com/partdetail/C11702) | 0402WGF1001TCE | 60 | 70 | 7,999,000 | 0 |
| [C13585](https://jlcpcb.com/partdetail/C13585) | CL31A106KBHNNNE | 20 | 24 | 2,204,369 | 0 |
| [C1525](https://jlcpcb.com/partdetail/C1525) | CL05B104KO5NNNC | 180 | 190 | 23,583,634 | 0 |
| [C2286](https://jlcpcb.com/partdetail/C2286) | KT-0603R | 20 | 30 | 7,083,479 | 0 |
| [C25741](https://jlcpcb.com/partdetail/C25741) | 0402WGF1003TCE | 40 | 50 | 7,970,630 | 0 |
| [C25744](https://jlcpcb.com/partdetail/C25744) | 0402WGF1002TCE | 120 | 130 | 19,052,863 | 0 |
| [C25867](https://jlcpcb.com/partdetail/C25867) | 0402WGF1501TCE | 20 | 30 | 1,921,364 | 0 |
| [C25900](https://jlcpcb.com/partdetail/C25900) | 0402WGF4701TCE | 40 | 50 | 14,244,292 | 0 |
| [C25905](https://jlcpcb.com/partdetail/C25905) | 0402WGF5101TCE | 40 | 50 | 5,458,422 | 0 |
| [C29277](https://jlcpcb.com/partdetail/C29277) | CL21A226MPQNNNE | 40 | 40 | 29,147 | 0 |
| [C29779902](https://jlcpcb.com/partdetail/C29779902) | CH32X035C8T6 | 20 | 20 | 2 | 18 |
| [C3662793](https://jlcpcb.com/partdetail/C3662793) | TPS259470LRPWR | 20 | 20 | 557 | 0 |
| [C4142](https://jlcpcb.com/partdetail/C4142) | 0402WGF8202TCE | 20 | 30 | 26,593 | 0 |
| [C48496](https://jlcpcb.com/partdetail/C48496) | SWPA5040S4R7MT | 20 | 24 | 7,370 | 0 |
| [C52923](https://jlcpcb.com/partdetail/C52923) | CL05A105KA5NQNC | 20 | 30 | 7,222,988 | 0 |
| [C720477](https://jlcpcb.com/partdetail/C720477) | TS-1088-AR02016 | 40 | 44 | 686,289 | 0 |
| [C7519](https://jlcpcb.com/partdetail/C7519) | USBLC6-2SC6 | 20 | 22 | 45,269 | 0 |
| [C780769](https://jlcpcb.com/partdetail/C780769) | AP63203WU-7 | 20 | 20 | 13,446 | 0 |
| [C8598](https://jlcpcb.com/partdetail/C8598) | B5819W SL | 40 | 48 | 390,210 | 0 |
| [C963411](https://jlcpcb.com/partdetail/C963411) | GT-USB-7010AW | 20 | 20 | 1,109 | 0 |

Provisional quantity is `max(fitted + displayed loss count, displayed assembly
minimum)` once per C-number across the batch. This is a planning assumption,
not the factory's confirmed attrition calculation. Pre-purchase MOQ is separate.
Evidence is in [the JLC snapshot](../hardware/procurement-observation.json) and
[the independent MCU observation](../hardware/lcsc-x035-observation.json).

## Fabrication and assembly findings

The board and four-copy panel have zero DRC violations and zero open connections.
All 164 CPL entries match the physical centers, angles and top-side population.
The panel copies preserve the board's pads, nets, copper and markings. No drilled
via intersects a paste aperture. The underside GPIO pads have no paste and add
no assembly operation. These checks validate the files; they do not establish
factory model orientation or physical yield.

The 0.60 mm castellated drills meet the stricter published
[castellation guide](https://jlcpcb.com/help/article/what-is-castellated-holes).
There are 160 half-holes per panel, including the internal milled slots.
Standard PCBA supports these castellations and the panel dimensions; Economic
PCBA does not. See [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities).

U3 uses the exact TPS259470LRPWR and RPW0010A land pattern. Its paste windows
match TI drawing 4225183/A, including two windows on each IN/OUT land and reduced
corner apertures. The [TI stencil example](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
is based on 0.100 mm thickness. JLC must confirm the actual stencil process,
including compatibility with the USB connector and 0402 parts, and inspect the
hidden QFN joints by X-ray.

The orientation guide identifies U1/U3/U4/D2 pin 1, D1/D4 cathodes at pin 1,
D3 cathode at pin 2, reset/boot contacts and USB mouth direction. The USB part
must remain GT-USB-7010AW, with its four plated shell stakes and two locating
holes. JLC must confirm insertion, shell soldering, reflow compatibility and
any pallet. The corner tab clears the nominal socket, but manufacturing and
placement tolerances still require review. Unused header holes must stay open.

## Costs

The refreshed fitted BOM is **$3.9214 per device**, or $78.428 for 20.
Provisional attrition raises parts to $80.5506. Parts plus the recorded setup,
stencil, 20 feeder types and SMT-joint assumptions total **$149.8486**, or
$7.49 per device **before PCB fabrication and the remaining charges**.

The [current fee table](https://jlcpcb.com/help/article/pcb-assembly-price)
also lists $16.40 for 20 QFN X-ray inspections and a handling minimum of
$14.93. Those add $31.33 to the planning scenario if applied as listed.
USB manual work, fixtures, packing, production/placement review, sourcing,
shipping and tax still need an actual order-specific quote. This is not a
complete or accepted factory price.

## Factory handoff

[factory-notes.txt](factory-notes.txt) contains the review requirements and is
included in the regenerated quote bundle. It has not been sent to a factory
representative. Select production-file and parts-placement confirmation, and
review their deadlines in the order form.

The shared quote page still shows Sign In. Its sign-in button throws
`Cannot read properties of undefined (reading 'gotoLogin')`, reproduced in a
fresh tab. Gerber parsing works, but account-dependent BOM/CPL matching,
allocation and factory placement-model review remain blocked. The earlier
Rev A upload observation does not approve Rev C.

The final Rev C panel upload parsed as four layers and 71 x 93 mm. Its
[upload observation](../hardware/jlc-factory-observation.json) records the
Gerber archive, panel and board hashes. Parsing does not confirm assembly
settings or factory acceptance.

Pending factory decisions are exact MCU sourcing and lot, actual attrition,
model rotations/centroids, stencil, USB assembly, panel handling/tolerances,
and the complete delivered quote. Firmware and assembled-board USB/PD,
thermal, current and fault testing remain separate prototype work.

## Generate the current fabrication files

```sh
just jlcpcb
just render
```

The fabrication bundle is `build/ch32-pico-jlcpcb.zip`. Extract it first;
only its inner `gerbers.zip` goes into JLC's PCB upload. Use its panel BOM and
CPL together at the assembly step. The orientation guide is generated in
`build/order-review/`; panel geometry, DRC and tooling results are in
`build/panel-preview/manifest.json`. File hashes tie the bundle to the checked
Rev E board. See [build instructions](build.md) for source changes and routing.
`just procurement` separately refreshes the dated public inventory. No generation
command places an order.
