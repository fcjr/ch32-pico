# Prototype order review

The current batch scenario is five four-up panels, 20 boards. The cost-reduced
protection stage has 52 top-side fitted parts per board, 208 per panel and
31 exact part numbers. The 93 x 71 mm panel preserves the 21 x 51 mm board
outline, 40 header positions and castellations. There are no mounting holes.

Use Standard PCBA; Economic PCBA does not support this castellated layout.
Enter one design and five supplied panels with four copies each. Do not request
another four-way panelization.

The [pre-order review](preorder-review.md) contains the latest exact-part stock
snapshot and parts-cost scenario. The exact CH32 is short of the 20-board need.
No stock is reserved. Older cost totals and 40-part board counts are superseded.

`just jlcpcb` checks the saved current layout and creates matching panel Gerbers,
BOM, CPL, orientation guide and hash manifest. Extract the outer ZIP and use its
inner Gerber archive with its matching BOM/CPL. Never mix files from old builds.
The command fails on stale source or failed routing. The files remain prototype
review inputs, not a production release.

Confirm every IC pin 1 and diode polarity against the physical orientation guide
in the supplier preview. U1/D2 require the recorded model-frame rotation delta;
J2 requires its recorded origin offset. The new imported power footprints use
their LCSC frames; online model/stencil confirmation is still required. Quote
hidden-joint X-ray for U3, Q1 and the TVS packages, USB shell assembly, fixtures,
castellations, actual stackup, all attrition, delivery and tax.

No order, payment, stock allocation or supplier message has been submitted.
Physical power/USB qualification and native board firmware remain open. See the
[qualification plan](power-qualification.md) and [factory notes](factory-notes.txt).

This revision uses four copper layers and front-side fitted assembly.
Earlier fabrication quotes do not approve the new copper and assembly; request a fresh
JLC04101H-3313 quote before ordering.

The dated planning scenario is $206.38 for the 20-board batch ($10.32 per
board), including provisional component attrition and modeled assembly costs
but excluding PCB fabrication and other quoted services, shipping and tax. It
is not a supplier quote. Fitted components alone total $113.74 ($5.69 per board).


## Further cost review, 2026-10-15

R20 now shares R27's 82.5 kohm, 0.1%, 25 ppm/C C852928. The OVLO
screen becomes 21.450–23.751 V; the independent UVLO is unchanged. This
removes one feeder and saves $1.80 across the provisional 20-board scenario.
All 52 fitted components, castellations and the existing layout are retained.

| Batch | Panels | Fitted parts per board | Partial parts + assembly per board | Partial batch |
|---|---:|---:|---:|---:|
| 20 boards | 5 | $5.6870 | $10.3191 | $206.38 |
| 100 boards | 25 | $4.6314 | $5.8240 | $582.40 |

Both use the Oct14 exact fitted-part price snapshot and the same published
Standard PCBA fee assumptions. The partial totals include provisional attrition,
setup, stencil, 31 feeders and modeled SMT joints. PCB fabrication, required
inspection, USB/manual assembly, handling, fixtures, shipping and tax remain
additional. These are planning scenarios, not quotes. The default batch remains
20 boards. MCU allocation and prototype qualification remain unresolved;
100 boards is not an order recommendation before testing.
`just order-review` writes both scenarios to
`build/order-review/batch-scenarios.json` without changing panel quantity.

The proposed regulator saving did not survive the 20-board reference-circuit
cost screen. SCT2332 C509069 is $0.5984 versus the recorded AP63203 $1.0571,
but its recommended circuit adds three resistor values, a compensation
capacitor, another output capacitor, and a different inductor. Four feeder
fees, the extra output capacitor and the priced inductor alone exceed the
IC saving by $0.0143/board, before pricing the new small passives and extra
assembly. At 100 boards there is a possible saving below $0.231/board before
those remaining costs; that alternative has not been laid out or qualified.
This is a reference-circuit comparison, not an exhaustive optimized design.
The simpler fixed 3.3 V SCT2323 is stock zero and marked discontinued by JLC;
SCT2320 and SCT2322 also showed zero stock. AP63203 remains fitted.

The protection alternatives were reviewed and not adopted. SMBJ22A's specified
35.5 V clamp exceeds the regulator's 32 V operating and 34 V absolute limits.
The cheaper TECH PUBLIC TPS3808G01DBVR-TP has stock, but its full-temperature
threshold, leakage, response and supply-off behavior were not established from
an authoritative manufacturer specification. TI's similarly named part is not
its datasheet. TPS3701 and both TVS2200 clamps remain fitted.
Sources, dated candidate inventory and the calculation are recorded in
[the second cost screen](../hardware/research/cost-round2.json).

The panel exporter now clears its generated Gerber directory and verifies its
inventory against the four-layer Gerber job. This removes obsolete In3/In4
files left by a previous six-layer export. The final ZIP also checks that its
file list matches the current job before bundling.
