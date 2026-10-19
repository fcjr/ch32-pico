# Parts and factory review

The board has 29 fitted parts, 20 part numbers and a $2.15 parts-only
estimate at 20 boards. Pin 40 is direct USB VBUS. The
[pre-order review](preorder-review.md) contains the 2026-10-19 stock table and
cost assumptions. Every part shows stock for the batch; none is reserved.
See the [design notes](design.md) for the power circuit, placement and
qualification limits, and [factory notes](factory-notes.txt) for the
manufacturing instructions. The routed board and generated panel pass checks;
matching exports are generated. No factory upload, allocation or approval has
been performed, and no order, payment or reservation has been made.

## Parts

All 20 distinct fitted C-numbers match the expected MPN in JLC's public
catalogue. There are 29 fitted parts per device and 21 BOM rows, because
one part number appears under two circuit descriptions. The batch has 580
placements.

All 20 C-numbers have enough reported stock for the provisional attrition
scenario. C29779902 / CH32X035C8T6 reports 1,082 pieces on 2026-10-19, up
from two in the previous snapshot; a catalogue observation does not reserve
stock or prove JLC allocation, so confirm it in the order.

Use JLC sourcing for the exact MPN and package.
Do not replace it with another X035 package without a new pinout and footprint
review. Require a lot supporting I2C and ADC3/ADC7: the early-silicon restriction
in [WCH datasheet v1.7, table 2-1 note 3](https://akizukidenshi.com/goodsaffix/CH32X035.pdf)
affects functions used on this board. Catalogue stock does not identify the lot.
The factory must provide lot identification; bring-up must exercise those functions.

Both buttons use C49234124 / hanxia HX 3x4x2-2P-1.6N (Extended). The XUNPU
TS-1088 parts that share this land pattern, C720477 and C720478, both showed
no stock on the order page despite catalogue stock, so they are listed as
substitutes only. The [switch review](../hardware/research/switch-replacement.json)
records dimensions, stock and sources.

## Fabrication and assembly findings

The board and four-copy panel have zero DRC violations and zero open connections.
All 104 CPL entries match the physical centers, angles and top-side population.
The panel copies preserve the board's pads, nets, copper and markings. No drilled
via intersects a paste aperture. The underside GPIO and diagnostic pads have no
paste and add no assembly operation. These checks validate the files; they do
not establish factory model orientation or physical yield.

The 0.60 mm castellated drills meet the stricter published
[castellation guide](https://jlcpcb.com/help/article/what-is-castellated-holes).
There are 160 half-holes per panel, including the internal milled slots.
Standard PCBA supports these castellations and the panel dimensions; Economic
PCBA does not. See [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities).

D5 uses the TVS2200 WSON-6 land with an exposed ground pad. JLC must confirm
the stencil process, including compatibility with the USB connector and 0402
parts, and inspect the hidden pad joint by X-ray.

The orientation guide identifies U1/U4/D2/D5 pin 1, D1/D4 cathodes at pin 1,
D3 cathode at pin 2, reset/boot contacts and USB mouth direction. The USB part
must remain GT-USB-7010ASV (or the 5 A AN variant on the same land pattern),
with its four plated shell stakes and two locating
holes. JLC must confirm insertion, shell soldering, reflow compatibility and
any pallet. The corner tab clears the nominal socket, but manufacturing and
placement tolerances still require review. Unused header holes must stay open.

Dimensional targets come from JLC's [PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities),
[process-edge guidance](https://jlcpcb.com/help/article/specifications-for-adding-process-edges-and-positioning-holes)
and [Standard PCBA fiducial guidance](https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order).

## Costs

The dated planning scenario is $114.25 for the 20-board batch ($5.71 per
board), including provisional component attrition and modeled assembly costs
but excluding PCB fabrication and other quoted services, shipping and tax. See
[order review](order-review.md). The
[current fee table](https://jlcpcb.com/help/article/pcb-assembly-price)
also lists X-ray inspection and a handling minimum. USB manual work, fixtures,
packing, production/placement review, sourcing, shipping and tax still need an
actual order-specific quote. This is not a complete or accepted factory price.

## Factory handoff

[factory-notes.txt](factory-notes.txt) contains the review requirements and is
included in the regenerated quote bundle. It has not been sent to a factory
representative. Select production-file and parts-placement confirmation, and
review their deadlines in the order form.

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
board. See [build instructions](build.md) for source changes and routing.
`just procurement` separately refreshes the dated public inventory. No generation
command places an order.
