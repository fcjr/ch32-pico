# JLCPCB fabrication files

## Files for the five-panel prototype

Run `just jlcpcb` from the repository root. It checks the design,
builds the panel and assembles the files below. See [build setup](build.md).

Five panels contain four devices each, for twenty devices total.

| File | Use |
| --- | --- |
| `build/ch32-pico-jlcpcb.zip` | Complete fabrication bundle; extract it first |
| `build/jlcpcb/gerbers.zip` | Upload to the JLC PCB quote form |
| `build/jlcpcb/bom.csv` | Panel assembly BOM |
| `build/jlcpcb/cpl.csv` | Panel assembly placement file |
| `build/jlcpcb/assembly-orientation.svg` | Visual guide for factory part-model checks |
| `hardware/review/ch32-pico.kicad_pcb` | Checked single-board KiCad source |
| `build/panel-preview/ch32-pico-panel.kicad_pcb` | Generated four-copy KiKit panel |

The fitted BOM estimate is $3.171 per device at twenty devices, before
attrition, purchase minimums, PCB fabrication, assembly, shipping and tax.
The latest dated breakdown and stock shortages are in [order review](order-review.md).
No order has been submitted and no parts are reserved.

## Regeneration and single-board outputs

After a routing change, run `just route`, then `just review`.
After an artwork-only change, `just review` reuses the existing routed candidate.
Then run `just manufacturing-preview`.
The last command checks the source and schematic, regenerates the critical
copper, independently checks the saved board, and exports into
`build/manufacturing-preview/`. A failed export preserves the previous preview.
It performs no upload, purchase or stock reservation.

The folder contains:

- `ch32-pico-gerbers-PREVIEW.zip`: four copper layers, masks, silkscreen, paste,
  outline and separate PTH/NPTH Excellon drill files.
- `gerbers/`: the individual files and SVG drill maps for inspection.
- `bom.csv`: exact LCSC identifiers and MPNs, grouped from the electrical source.
- `cpl.csv`: actual KiCad board placement, filtered to the same 26 fitted parts.
- `manifest.json`: board and file hashes, tool version, source hashes, checks
  and open engineering reviews.

The placement file uses millimeters, the KiCad absolute origin, positive X
right and positive Y up. The board therefore occupies negative Y coordinates.
The exporter checks each position against the placement source and rejects
missing or duplicated fitted parts. It deliberately includes the hybrid USB-C
connector, which an SMD-only filter can omit. Board-only headers and test pads
are excluded from assembly.

Column names follow JLC's [KiCad BOM/CPL instructions](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad).
The CPL contains KiCad footprint angles. They have not yet been qualified
against JLC's component models. Verify pin 1, diode/LED polarity, USB mouth,
switch orientation and component centers in JLC's assembly preview. Record
any required angle or centroid correction in source before regenerating files.

PCB settings are 21 x 51 mm, four layers, 1.0 mm, ENIG, JLC04101H-3313,
outer 1 oz / inner 0.5 oz. Request castellated holes. All vias are 0.45 mm
diameter with 0.20 mm drills. JLC's quote-form note permits standard multilayer
via pricing for this combination; confirm that treatment during quoting.
The design does not use filled/capped via-in-pad. Assembly is entirely on top.
JLC panel rails, fiducials and handling requirements need confirmation for this
small castellated board. Review the exact stackup and USB geometry before
selecting any controlled-impedance order option.

JLC's [published assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
exclude castellated holes from Economic PCBA. Use **Standard PCBA**, top side,
with the 93 x 71 mm supplied panel and five-panel quantity. A single 21 x 51 mm
board is below Standard's 70 x 70 mm minimum. Prototype quantity does not remove
this restriction. The panel includes the required rails and fiducials.

`just order-review` checks panel artifact hashes, computes a dated assembly-cost
scenario and writes a physical pin/polarity guide under `build/order-review/`.
The JSON guide checks all 208 panel CPL rows and gives anchor coordinates in
both board and panel/CPL conventions. Panel CPL angles apply reviewed JLC
model-frame deltas (U1/D2 rotation, J2 anchor); JLC preview confirmation is
still required. See [order review](order-review.md).

The preview is not an order release. Check the reviews in `manifest.json`,
resolve the recorded component shortages, allocation and assembly attrition for the chosen
quantity, inspect the Gerbers and drill maps, and review all assembly rotations.
A zero-error board DRC does not prove USB signal quality, thermal limits or
physical fit. Programming and power validation require assembled prototypes.

For the requested five-panel batch, use `just panel-preview` and the files in
`build/panel-preview`, described in [panelization](panelization.md). Each panel
contains four boards. The circuit is described in the [design notes](design.md); no preview is released for ordering.

Generated upload files are Git-ignored under `build/`. The checked PCB, design
sources and locked tools are committed. Keep a copy of the exact bundle used
for a fabrication run with its source commit and manifest hashes.
