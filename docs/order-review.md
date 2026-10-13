> **Rev A reference.** The [current Rev C design](revision-c.md) supersedes the circuit, pinout, costs and manufacturing status below.

# Prototype order review

Five supplied panels contain four identical boards each: 20 complete boards,
660 fitted components and 40 MCUs. The 93 x 71 mm KiKit panel preserves every
21 x 51 mm board, all 40 header positions and all four mounting holes.

**Standard PCBA is required.** JLC's [assembly capability table](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
does not support castellated holes on Economic PCBA. The revised panel exceeds
Standard's 70 x 70 mm minimum and includes rails, tooling holes and fiducials.
The requested five-panel quantity remains; Economic/prototype pricing does not.

## Cost at 20 boards

These are offline planning figures from the 2026-10-12 stock observation and
[JLC's published fees](https://jlcpcb.com/help/article/pcb-assembly-price), not
a checkout quote. `make order-review` regenerates the calculation from the BOM,
saved board and panel. The dated fee inputs are in
`hardware/jlc-assembly-policy.json`.

| Item | Batch USD |
| --- | ---: |
| Components with provisional attrition | 25.5992 |
| Single-side Standard setup | 25.56 |
| Single-side stencil | 8.21 |
| 17 feeder types at $1.53 | 26.01 |
| 123 SMT lands per board × 20 × $0.0016 | 3.936 |
| **Partial total** | **89.3152** |

That is **$4.47 per board before PCB fabrication**, USB shell/insertion work,
any fixture, packing, handling, panel, storage or placement-review charges,
shipping and tax. JLC may count solder joints differently from physical lands.
If all four USB shell stakes require manual soldering, a separate illustrative
charge is $4.89 per batch including manual labor. Two rigid-PCB fixtures would
add $16.42 if required. Neither is included in the partial total.

The BOM alone remains $1.2345 per board. At this prototype quantity, assembly
fees consume the intended price advantage. Scaling the batch amortizes setup,
stencil and feeder charges; preserving castellations prevents switching this
design to Economic PCBA. Do not change layers or finish in the order form
without revalidating the layout and stackup.

## Parts and attrition

The local scenario uses `max(fitted quantity + displayed loss count, displayed
assembly minimum)` for each C-code across the batch. This is an explicit
planning assumption, not a verified JLC order formula. The resulting parts
cost is $25.5992 instead of $24.69 fitted-only. Actual quantities must come
from JLC's Parts Calculator/order matching. The public pre-purchase MOQ is
separate and must not be imposed on every in-stock assembly line item.

Sixteen of the 17 selected C-codes have enough reported JLC stock for this
scenario. At 16:07 UTC, **C15999 (USBLC6-2P6) has zero reported stock**;
20 are required. This exact ESD device needs sourcing or a separately validated
replacement. **C5187096 has restocked: 3,980 reported, 2,883 available to order.**
Forty CH32V003F4P6 MCUs are fitted. The public price tiers suggest requesting
50: $11.23 for 50 is less than $11.548 for 40 and supplies ten extras. These
prices do not establish availability or constitute a sourcing quote.

The earlier 04:43 UTC LCSC observation separately showed 8,962 units under Other Suppliers, MOQ 50,
$0.1902 each and an estimated 3–5 business days to LCSC. LCSC's own stock was
empty. This third-party offer is not a JLC allocation; retain exact MPN/package
and request a JLC sourcing quote before spending. The evidence is in
`hardware/lcsc-mcu-observation.json`.

[JLC pre-order](https://jlcpcb.com/help/article/how-to-build-your-own-parts-library-in-jlcpcb)
can reserve eligible stock or request non-stock parts with a purchase minimum.
[Global sourcing](https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service)
is an alternative if JLC can obtain this exact MCU. Sourced parts must reach
JLC before assembly allocation. No parts have been purchased or reserved.

## Assembly review package

Run `make panel-preview` after changing panel geometry, then `make order-review`.
The latter verifies the saved board, panel and exported file hashes and writes:

- `build/order-review/order-review.json`: quantities, fee assumptions and exclusions.
- `build/order-review/assembly-orientation.svg`: top-view physical orientation guide.
- `build/order-review/assembly-orientation.json`: every terminal's net and coordinates,
  all 132 checked panel CPL rows and transformed pin/polarity anchor coordinates.

The guide distinguishes D1 pin 1 (cathode) from D3 pin 2 (cathode), locates
MCU/LDO/ESD pin 1, identifies MOSFET gate/source/drain, and shows the USB mouth.
Compare these physical anchors against JLC's actual part models. A model's
red dot is not necessarily pin 1, as JLC explains in its
[placement FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2).
No JLC rotation offsets are inferred from KiCad angles alone.

`make quote-package` produces `build/ch32-pico-QUOTE-REVIEW.zip` with the checked
panel Gerbers, BOM, CPL, orientation guide, cost assumptions and upload settings.
Extract this review bundle first. Upload its inner `gerbers.zip` to JLC's PCB
form, then its BOM and CPL at the assembly step. The bundle's manifest records
each file hash and the source-board/panel hashes. It is not an order release.

For quoting, use the panel Gerber ZIP, panel BOM and panel CPL together from
`build/panel-preview/`. Select five customer-supplied panels, one design,
four copies per panel, Standard top-side assembly, four layers, 1.0 mm,
ENIG and castellated holes. All vias are 0.45/0.20 mm; the quote form explicitly
allows that combination at standard multilayer via pricing. Record both
diameter and actual drill size in the PCB remarks and confirm the pricing
category with JLC. Preserve the documented JLC04101H-3313 stackup. The form can
reset that selection when other settings change, so recheck it last.
Do not request a second four-up panelization.

Before order release, resolve C15999 supply and confirm all part allocations and charged quantities,
JLC model rotations/centroids, USB hybrid assembly, tab handling, and the full
landed price. Prototype USB operation, cable fit, power limits and programmer
recovery remain physical tests. The local reports do not qualify those tests.

## Uploaded quote, 2026-10-12

JLC accepted the panel Gerbers and detected four layers and 71 x 93 mm. The
entered settings retain five supplied panels, four copies per panel, Standard
top-side assembly, existing customer rails/fiducials, Nan Ya NP-155F and
JLC04101H-3313. The form disables Tented and says it upgrades to Plugged free.
The fabrication calculator shows **$92.85 for the five panels**, excluding
assembly; its separate shipping estimate is $31.44. Neither is a final quote.
No small-via or Kelvin-test fee appears in this fresh calculation.

The BOM/CPL step is blocked: both Next and Sign In log
`Cannot read properties of undefined (reading 'gotoLogin')`. This also occurs
in a fresh quote tab after a hard reload. The main parts interface recognizes
My Account, but the cart interface continues showing Sign In. No assembly
model review, component allocation, saved order or payment has occurred.
The selected settings and displayed charges are recorded in
`hardware/jlc-upload-observation.json`.

The refreshed parts scenario plus this fabrication calculator is about
$182.17 for 20 boards ($9.11 each), **before shipping and other exclusions**.
It remains a planning combination, not a factory assembly quote.

## Artwork update, 2026-10-12

The current local files include `ch32-pico`, `REV A` and the Left Shift Logical logo
on the front silkscreen. Programmer/target pad labels and `RESET` now sit
beside their front-side contacts. Back header labels use `NC`, `RST` and
corner pin numbers; see the [marking review](markings.md).
Copper, board outline, holes and fitted parts are
unchanged. The earlier browser upload and quote observation predate this
artwork update. Re-upload the regenerated Gerbers for the final factory
preview; do not treat the earlier upload as the current file revision.
