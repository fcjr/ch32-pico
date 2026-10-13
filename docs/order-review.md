# Prototype order review

The current Rev E batch is five supplied panels with four boards each: 20
boards, 820 fitted components and 20 CH32X035 MCUs. The 93 × 71 mm panel
preserves the 21 × 51 mm outline, 40 header positions and castellations.
There are no mounting holes. Assembly uses 41 parts per board, 164 placements
per panel, all on top. The diagnostic pads and open jumper are not assembled.

Use Standard PCBA. The dated [JLC capability review](factory-review.md) records
that Economic PCBA does not support castellations. The supplied panel includes
rails, tooling holes and fiducials. Enter one design, four copies per supplied
panel and five panels; do not request another four-way panelization.

## Dated cost and stock scenario

These figures use the saved 2026-10-13 public inventory and fee observations.
They are planning figures, not a factory quote or stock allocation.
`just order-review` recalculates them from the current BOM and saved observations;
`just procurement` separately refreshes public inventory.

| Item | Batch USD |
|---|---:|
| Parts with provisional attrition | 80.5506 |
| Standard single-side setup | 25.56 |
| Single-side stencil | 8.21 |
| 20 feeder types | 30.60 |
| SMT lands scenario | 4.928 |
| Partial total | 149.8486 |

That is $7.49 per board before PCB fabrication, USB manual work, fixtures,
X-ray inspection, handling, shipping, tax and other exclusions. The fitted BOM
alone is $3.9214 per board. The complete list of assumptions and exclusions is
in `build/order-review/order-review.json` and [factory review](factory-review.md).

The scenario uses the larger of fitted quantity plus displayed loss count and
displayed assembly minimum for each C-code. JLC must confirm actual quantities
and attrition. Public purchasing minimums are separate from assembly allocation.

The saved observation reports two C29779902 CH32X035C8T6 MCUs against a need
for twenty, a shortfall of eighteen. The other nineteen C-codes have sufficient
reported stock for the provisional quantities. These observations can become
stale; no components are reserved. Obtain the exact reviewed MCU and qualified
silicon lot, or validate any replacement before changing the BOM.

## Fabrication files and assembly review

```sh
just jlcpcb
```

This checks and generates the full set under `build/jlcpcb/`:

- `gerbers.zip`, `bom.csv` and `cpl.csv` are the matching panel upload inputs.
- `factory-notes.txt` specifies the stackup, castellations, stencil, component
  lot, polarity and inspection requirements.
- `assembly-orientation.svg` and `.json` give physical anchors for checking
  every part model. All 164 panel placements are checked locally.
- `order-review.json` records quantities, dated costs, shortages and exclusions.
- `manifest.json` records the board, panel and output hashes.

`build/ch32-pico-jlcpcb.zip` bundles the entire directory. Extract it first;
upload only the inner `gerbers.zip` to JLCPCB's PCB form, followed by the BOM
and CPL at the assembly step. See [manufacturing](manufacturing.md) and
[build setup](build.md).

KiCad angles are not verified JLC model offsets. Check IC pin 1, diode/LED
polarity, USB mouth, switch orientation and centroids in the assembly preview.
Record any required corrections in source before regenerating the files.

No Rev E assembly preview, stock allocation or factory approval has been
completed. Earlier Rev C browser observations remain historical evidence in
[factory review](factory-review.md); they do not approve these files. Native
USB/PD firmware, cable fit, power behavior and thermal qualification still
require assembled prototypes. No order or payment has been submitted.
