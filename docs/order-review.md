# Prototype order review

The current batch scenario is five four-up panels, 20 boards. There are 29
top-side fitted parts per board, 116 per panel and 20 exact part numbers.
The 93 x 71 mm panel preserves the 21 x 51 mm board outline, 40 header
positions and castellations. There are no mounting holes.

Use Standard PCBA; Economic PCBA does not support this castellated layout.
Enter one design and five supplied panels with four copies each. Do not request
another four-way panelization.

The [pre-order review](preorder-review.md) contains the latest exact-part stock
snapshot and parts-cost scenario. Every part shows stock for the batch; none
is reserved.

`just jlcpcb` checks the saved layout and creates matching panel Gerbers,
BOM, CPL, orientation guide and hash manifest. Extract the outer ZIP and use its
inner Gerber archive with its matching BOM/CPL. Never mix files from different
builds. The command fails on stale source or failed routing. The files remain
prototype review inputs, not a production release.

Confirm every IC pin 1 and diode polarity against the physical orientation guide
in the supplier preview. U1/D2 require the recorded model-frame rotation delta;
J2 requires its recorded origin offset. D5 uses its LCSC frame; online
model/stencil confirmation is still required. Quote hidden-joint X-ray for the
D5 TVS package, USB shell assembly, fixtures, castellations, actual stackup,
all attrition, delivery and tax.

No order, payment, stock allocation or supplier message has been submitted.
Physical power/USB qualification and native board firmware remain open. See the
[qualification plan](power-qualification.md) and [factory notes](factory-notes.txt).

The board uses four copper layers and front-side fitted assembly. Request a
JLC04101H-3313 quote before ordering.

## Planning scenarios

| Batch | Panels | Fitted parts per board | Partial parts + assembly per board | Partial batch |
|---|---:|---:|---:|---:|
| 20 boards | 5 | $2.3568 | $5.9195 | $118.39 |
| 100 boards | 25 | $1.9186 | $2.7887 | $278.87 |

Both use the 2026-10-19 exact fitted-part price snapshot and the published
Standard PCBA fee assumptions. The partial totals include provisional attrition,
setup, stencil, feeders for the Extended parts and modeled SMT joints. PCB fabrication, required
inspection, USB/manual assembly, handling, fixtures, shipping and tax remain
additional. These are planning scenarios, not quotes. The default batch is
20 boards. MCU allocation and prototype qualification remain unresolved;
100 boards is not an order recommendation before testing.
`just order-review` writes both scenarios to
`build/order-review/batch-scenarios.json` without changing panel quantity.

The panel exporter clears its generated Gerber directory and verifies its
inventory against the four-layer Gerber job. The final ZIP also checks that its
file list matches the current job before bundling.
