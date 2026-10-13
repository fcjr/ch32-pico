# MCU alternatives, 2026-10-13

The selection priority is now **deep, regularly available stock**, rather
than merely enough parts for twenty boards. This supersedes the initial
CH32V205RCT6 recommendation: its 59-piece inventory does not meet that
preference, even though its feature set is promising. No MCU substitution
has been made in the circuit, reviewed board or manufacturing files.

## Selected direction: retain CH32X035C8T6 and source the exact part

The user accepted pursuing the existing C8T6. Native PD and the existing
GPIO allocation remain required; a separate PD controller is excluded.
No MCU or footprint change is needed for an exact-MPN supply.

An exact-part search in ICkey's live browser catalog on 2026-10-13 found:

| Offer | Reported stock | Minimum / increment | Displayed price | Mainland delivery |
| --- | ---: | --- | --- | --- |
| [ICkey preferred supply](https://www.ickey.cn/detail/1003001027318459/CH32X035C8T6.html) | 235 | 1 / 1 | ¥3.8755 each below 50; ¥3.0935 at 50 | 3–5 working days |
| [ICkey domestic supply](https://www.ickey.cn/detail/1003001029027659/CH32X035C8T6.html) | 25,000 | 250 / 250 | ¥2.40 at 250; ¥600 for the minimum order | 5–8 working days |

Prices are the site's mainland VAT-inclusive amounts, before any delivery
or assembly charges. The first offer labels its date code as within two
years; the second says 25+. Both leave the package field blank. These are
supplier-reported availability, not independently confirmed warehouse
counts, allocated parts, or evidence of regular replenishment. Exact lot
markings, LQFP48 package and provenance still need confirmation. The live
search snapshot is saved in `build/procurement/c8-ickey-observation.json`.
Indexed brand pages differed from the live catalog; use the exact-MPN
search and individual offers when requesting a quote.

JLC's existing C29779902 was rechecked at 15:50 UTC and still has two
pieces. C35602243, found in a mirrored datasheet filename, did not resolve
to an exact-part JLC inventory record and is not an approved BOM code.

The practical next step is a quote for 25 or 50 exact C8T6 devices from
the small-quantity offer, plus a 250-piece option for future builds.
Twenty boards require twenty fitted MCUs; extra quantity remains subject
to JLC's actual attrition and minimum requirements. Before purchasing,
confirm the silicon supports ADC3/ADC7 and hardware I2C: WCH documents
restricted early lots, and this board uses ADC3 for current sensing.
Ask for the complete top marking and traceable manufacturer packaging.

[JLC permits consignment from mainland China](https://jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb-from-mainland-china).
Register the exact part in Parts Manager, obtain the account-specific
receiving details and packaging requirements, and have the supplier ship
with the required invoice and tracking. Supplier willingness to do this
has not been confirmed. Under [JLC's inventory rules](https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order),
consigned/global-sourced units cannot be combined with the two public-stock
units for this same MCU in one assembly order. Source the entire MCU batch
through one compatible inventory pool and wait for warehouse receipt.

Prepared supplier inquiry (not sent):

> Please quote original WCH CH32X035C8T6, LQFP48 7 × 7 mm, for 25, 50 and
> 250 pieces. Confirm physical availability, dispatch date, manufacturer
> packaging and traceability, and provide complete chip top markings and
> lot/date codes. We require silicon with working ADC channels 3 and 7 and
> hardware I2C; please confirm the offered lot does not have WCH's early-lot
> restrictions. Can you ship directly to our registered JLCPCB mainland
> consignment address with an invoice and tracking? Please also state
> replenishment lead time and whether recurring supply can be supported.

No inquiry, order, reservation or consignment submission has been sent.
This supply lead does not clear the separate power-stage qualification
items in [the preorder review](preorder-review.md).

## Stock-depth follow-up

Further live JLCPCB checks on the same date found:

| Part | JLC code | Reported stock | Constraint |
| --- | --- | ---: | --- |
| CH32X035G8U6 | [C7437027](https://jlcpcb.com/partdetail/C7437027) | 10,179 | Native PD; only 27 physical GPIOs, approximately 15 free with present internal functions |
| CH32V203C8T6 | [C3001172](https://jlcpcb.com/partdetail/C3001172) | 6,508 | No native PD; 37 GPIOs before internal reservations, so cannot retain all 33 external GPIOs |
| FUSB302BMPX | [C132291](https://jlcpcb.com/partdetail/C132291) | 7,898 | Possible separate PD PHY/controller; requires host policy firmware and extra interface pins |
| CH32V203RBT6 | [C5116460](https://jlcpcb.com/partdetail/C5116460) | 546 | More pins, but little stock; separate PD required |
| CH32V307RCT6 | [C2988083](https://jlcpcb.com/partdetail/C2988083) | 393 | Separate PD required |
| CH32V307WCU6 | [C5142795](https://jlcpcb.com/partdetail/C5142795) | 288 | Separate PD required |
| CH32V305RBT6 | [C5187529](https://jlcpcb.com/partdetail/C5187529) | 770 | Separate PD required |
| CH32V208RBT6 | [C5448615](https://jlcpcb.com/partdetail/C5448615) | 191 | Separate PD required |
| CH32X035G8R6 | [C49118551](https://jlcpcb.com/partdetail/C49118551) | 15 | Smaller GPIO budget and little stock |

The G8U6 is the strongest observed native-PD stock candidate, with the
previously documented GPIO, reset and I2C compromises. Search-indexed LCSC
pages also show older stock observations ranging from hundreds to several
thousand; those are not a continuous historical record or evidence of a
guaranteed stock floor. None of these checks establishes that a part will
regularly remain above a particular inventory threshold.

LCSC's live CH32L103 family search lists K8U6 as unavailable/discontinued
in its catalog and the K8U7 replacement listing at zero. That catalog status
is not a manufacturer lifecycle declaration. The C8T6 remains at 771.

No checked JLC public-stock part currently meets all three preferences together: native PD,
the existing accessible GPIO capacity, and stock in many thousands. A
separate-PD architecture was subsequently rejected by the user. The stock observations are in
`build/procurement/mcu-volume-stock.json`; additional counts above were
read directly with the same exact-MPN validation routine.

## Assembly inventory

Public JLCPCB pages were fetched at 2026-10-13T15:29:34Z. Exact C-number and
manufacturer part number were matched before accepting stock. Counts are
observations, not reservations. Prices are the displayed twenty-piece tier,
excluding assembly and other charges.

| Part | JLC code | Reported stock | USD each at 20 | Assessment |
| --- | --- | ---: | ---: | --- |
| CH32V205RCT6 | [C54973461](https://jlcpcb.com/partdetail/C54973461) | 59 | 1.3717 | Best new candidate; actual silicon lot must support PD |
| CH32V205CCT6 | [C54973459](https://jlcpcb.com/partdetail/C54973459) | 0 | — | Smaller pin count; no stock |
| CH32H417MEU6 | [C54973456](https://jlcpcb.com/partdetail/C54973456) | 402 | 4.5962 | Much larger firmware/platform change; 88-pin QFN |
| CH32H417WEU6 | [C52196060](https://jlcpcb.com/partdetail/C52196060) | 0 | — | No JLC stock; family feature claims require package-specific checking |
| CH32M030C8T7 | [C54152956](https://jlcpcb.com/partdetail/C54152956) | 0 | — | No stock |
| CH32L103C8T6 | [C22398291](https://jlcpcb.com/partdetail/C22398291) | 771 | 0.6263 | Stocked, but loses GPIO capacity and PIOC |

The original CH32X035C8T6 was separately rechecked at 15:19Z: two pieces.
An exact LCSC browser search for CH32X035R8T6 returned no matching product
and suggested CH32X035C8T6 instead. This is not proof that no distributor
can supply R8T6; an orderable source and exact assembly-library identity
remain unverified. CH32X305/X315 searches did not establish an orderable
stocked candidate.

Raw inventory observations and response hashes are retained locally in
`build/procurement/mcu-alternatives-expanded.json` and the cached product
pages in that directory. Retail LCSC and JLC counts must not be added.

## CH32V205RCT6 electrical assessment

The [WCH V1.3 datasheet](https://ch32-riscv-ug.github.io/CH32V205/datasheet_en/CH32V205DS0.PDF)
lists 51 GPIOs, USB-PD, PIOC, USB full/high speed, 192 MHz, 256 KB flash and
32 KB RAM. CC1/CC2 use PA0/PA1, so our existing ADC/header assignment must
change. The resource-table footnote says some lot codes lack CAN and
USBPD. Public stock does not establish the silicon revision of those parts.

A first pin-count budget leaves 39 GPIOs after reserving twelve for our
existing internal functions. This is an upper bound before clock, boot,
alternate-function and electrical restrictions. It suggests that retaining
33 accessible GPIOs is feasible, but a complete pin allocation is still
required. The V3B core, peripheral registers, boot arrangements and power
pins differ: this requires a firmware port and a new routed PCB. It also
has two comparators rather than the X035C8T6's three. Controller support
for EPR does not qualify our existing 5–20 V power path for higher voltage.

## Mechanical screen

The existing board is 21 × 51 mm; U1 is centered at (10.5, 28) mm.
Standard KiCad footprint courtyards were compared with front-side
component courtyard bounding boxes. This is an initial space check,
not a completed placement, routing or DRC qualification.

| Candidate | Body | Courtyard screen | Existing courtyard overlaps |
| --- | --- | --- | --- |
| CH32X035R8T6 | 10 × 10 mm, 0.5 mm pitch | 13.4 × 13.4 mm; inside board outline | R2, R5, R6, C9, C10, C6, C7, R10, R11, TP23, TP24 |
| CH32V205RCT6 | 7 × 7 mm, 0.4 mm pitch | 10.36 × 10.36 mm; inside board outline | TP24 |

The R8T6 is physically plausible within the board outline, but cannot
occupy the current U1 position with all neighboring placements unchanged.
Its two supply pairs also require a reviewed decoupling arrangement. The
V205 has a substantially easier space requirement, though its finer pitch
and different pinout still require a new footprint and routing.

The measured bounding boxes are saved in
`build/procurement/mcu-fit-screen.json`. The screen does not assess trace
escape, vias, power integrity, assembly yield or the open power-stage issues.

If reconsidered, the V205 needs supplier confirmation of the silicon lot.
The R8T6 fallback needs a confirmed purchasing source as well as a new
placement; switching to it now would leave the ordering problem unresolved.
Neither presently satisfies the user's subsequent stock-depth preference.
