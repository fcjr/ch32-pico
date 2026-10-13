> **Rev A reference.** This document describes the former CH32V003 board.
> See [Revision C](revision-c.md) for the current X035/PD design.

# Cost and sourcing

The current circuit has 33 fitted components and 17 unique LCSC part numbers.
At five panels with four boards per panel, the 2026-10-12 parts estimate is
**$1.2345 per board, $24.69 for 20 boards**. This excludes fabrication,
assembly setup/feeder charges, solder joints, attrition, purchase minimums,
shipping and tax. It is not an assembled-board quote.

| Component group | Per board |
| --- | ---: |
| Two CH32V003F4P6 MCUs, C5187096 | $0.5774 |
| ST USBLC6-2P6 ESD device, C15999 | $0.2473 |
| Two ME6211 regulators, C82942 | $0.1226 |
| G-Switch USB-C socket, C2988369 | $0.0878 |
| Target reset switch, C720477 | $0.0525 |

ESD protection remains fitted. The programmer binary is compiled from source.

`just procurement` records public JLC inventory, exact MPN matches, price tiers
and response hashes. `just cost-review` prices each part at the total build
quantity. Two MCUs per board means 40 MCUs for this batch. Observations do not
reserve inventory or establish lead time. The reported pre-purchase minimum
is distinct from the quantity available for ordinary assembly allocation.
Order-specific attrition and minimum quantities must be reviewed in JLC.
At 04:43 UTC, the exact MCU was checked on LCSC. Its own inventory was
out of stock, while Other Suppliers on LCSC reported 8,962 pieces, a 50-piece
minimum, $0.1902 each at 50 and an estimated 3–5 business days to LCSC.
That is not a confirmed JLC assembly allocation. The observation is saved
in `hardware/lcsc-mcu-observation.json`. Other LCSC inventory is not independently
verified.

The 16:07 UTC JLC refresh reports 3,980 CH32V003 chips in stock, with 2,883
available to order. The current supply blocker is C15999 (USBLC6-2P6): zero
reported stock against 20 required. Source that exact part or validate a
replacement before release. Inventory has not been reserved. Check the latest
`hardware/procurement-observation.json`; do not infer that the presence of an
LCSC code makes a part immediately orderable. No substitute MCU is authorized
without a new pin, firmware and procurement review.

Four layers, castellations and ENIG can dominate a 20-board
prototype price. The KiKit panel stays within 100 x 100 mm, but that does not
guarantee JLC's advertised prototype tier applies to this fabrication and
assembly combination. A two-layer revision is a future cost opportunity;
the current routed/checked stackup must not be silently changed in the order.

The 2026-10-12 capability review establishes that castellations require
[Standard PCBA](https://jlcpcb.com/capabilities/pcb-assembly-capabilities).
The generated [order review](order-review.md) includes feeder charges for all
17 part types, setup, stencil and a provisional attrition scenario. Its partial
total is $89.32 for 20 boards ($4.47 each), before PCB fabrication and other
unquoted charges. A two-layer redesign would not remove the assembly-service
restriction while the castellations remain.

Every via is 0.45 mm in diameter with a 0.20 mm drill. The quote form permits
standard multilayer via pricing for this combination. Preserve the actual
stackup and check the final quote after changing any fabrication option.

The uploaded-panel calculation retains JLC04101H-3313 and Nan Ya
NP-155F and shows $92.85 for five bare panels. Assembly remains unquoted
because the site's login handler fails when advancing. The combined planning
figure is $9.11 per board before shipping and other exclusions; see
[order review](order-review.md).
