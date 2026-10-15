# Local component library

Exact MPN metadata and vendor symbols were imported from EasyEDA/LCSC with
`easyeda2kicad` 1.0.1 on 2026-10-11. Each fitted component in `hardware/circuit.py`
selects its LCSC C-number; `hardware/library.py` reads the associated metadata
and assigns reviewed electrical pin types. The schematic generator draws its
own typed symbols instead of using the importer's unspecified pin types.

On 2026-10-13, the 100 nF selection changed to Samsung CL05B104KB54PNC,
[C307331](https://www.lcsc.com/product-detail/C307331.html), verified as
50 V, X7R, ±10%, 0402. Its symbol reuses C1525's two-terminal geometry and
the existing C0402 footprint, with corrected MPN, voltage and vendor link.
C1525 remains in the library for historical designs and regression checks.
Voltage checks read vendor descriptions independently of circuit value labels.

RESET and BOOT now use XUNPU TS-1088-AR02516, C720478. The C720477 order
rows showed zero availability and warnings despite public catalog stock.
The replacement symbol was imported from EasyEDA on 2026-10-13 and retains
the reviewed `SW-SMD_L3.9-W3.0-P4.45` copper. The manufacturer drawing gives
a 4.8 +/- 0.3 mm terminal span and 1.3 mm terminal width; our pads span
5.59 mm overall, with a 3.13 mm inner gap and 1.86 mm width. The AR variant
has no locating peg. Height increases from 2.0 to 2.5 mm; force remains
1.6 N. See `hardware/research/switch-replacement.json` for source hashes,
dimensions and dated stock. The updated render uses the C720478 model.

Revisions B and C use the KiCad LQFP-48 7 × 7 mm land pattern for CH32X035C8T6
and SOT-23-6 for USBLC6-2SC6. `scripts/prepare_footprints.py` vendors those
patterns and moves imported legends to fabrication layers. Normal builds use
the checked-in files and do not depend on the workstation's library.

`scripts/prepare_pd_footprints.py` generates the selected GT-USB-7010AW
connector and TI RPW0010A eFuse footprint. The AW drawing specifies 5 A on
VBUS. Its SMT row has a 50 µm tailward adjustment within the manufacturer's
land-pattern tolerance to clear the locating holes. See the
[connector research](../research/usb-c/README.md) for the pinned source and
mechanical limits. Rev C removes the Pico mounting holes and positions the
socket mouth 0.30 mm beyond the short board edge.

The historical TPS259470L eFuse copper follows TI drawing 4225183/A. Overlapping rectangles share
terminal numbers at the L-shaped corner lands. Separate paste-only apertures
follow TI's 0.100 mm stencil example, including two windows per IN/OUT land.
The nominal paste coverage is about 93% at corner terminals and 82% at IN/OUT.
JLC must still review stencil thickness and assembly orientation.

LCSC import metadata identifies every fitted part by its C-number. Rev A
parts and preparation scripts remain available for maintaining the older
generation workflow; the current fitted population comes from `circuit.py`.
Rejected experimental Rev B package duplicates have been removed.

KiCad library source: [kicad-footprints](https://gitlab.com/kicad/libraries/kicad-footprints).
Its [CC BY-SA 4.0 license with library exception](https://www.kicad.org/libraries/license/)
applies to those upstream files. EasyEDA/LCSC data has separate provenance;
the probe firmware's MIT license does not relicense third-party CAD data.

`Pico_Header.kicad_mod` is generated from our mechanical contract. It includes
40 header lands and 40 connected castellated half-holes. Rev C has no mounting
holes. `TestPad_1mm` is a local PCB feature, not a purchased component. Review
all exact manufacturer package drawings and JLC assembly orientation before
releasing a manufacturing package.

For the archived Rev A design, ST USBLC6-2P6, C15999, uses a locally generated SOT-666
footprint from [ST DS4260 Rev 7, Figure 21](https://www.st.com/resource/en/datasheet/usblc6-2.pdf).
Run `uv run python scripts/prepare_esd_footprint.py` to reproduce it. The six lands
are 0.30 x 0.99 mm with 0.50 mm pitch and a 0.62 mm gap between rows.
Pin 1 is bottom left in this footprint's zero-degree orientation. Pins 1/6
carry D+, pins 3/4 carry D-, pin 2 is ground and pin 5 is VBUS. The symbol uses the manufacturer's pin assignments.

## License notices

Original ch32-pico design work uses CERN-OHL-P-2.0. Imported records retain
their upstream rights. See [project license scope](../../docs/licensing.md),
the [KiCad library notice](../../LICENSES/third-party/KiCad-library-license.md)
and [CC BY-SA 4.0 text](../../LICENSES/third-party/CC-BY-SA-4.0.txt).
KiCad library contributors retain copyright in the upstream footprints.
Local changes made on 2026-10-11 and 2026-10-12 remove unavailable models,
move imported silk to fabrication layers, and adapt the connector pad aliases,
SMT row and courtyard as documented above.

`SolderJumper_Open.kicad_mod` is an original Rev E PCB feature. Two 1 × 1.5 mm
pads have a 0.30 mm gap, mask openings and no paste. SJ1 is excluded from
BOM and placement files and must remain open during assembly.

`USB_Probe_Inline` is an original paste-free 1 x 0.1537 mm contact that stays
inside the existing USB trace. `TestPad_0.6mm` is an original bare probe pad
for PB3 where a 1 mm pad would crowd nearby markings. Neither is assembled.

Power review changes (2026-10-13): C307441 / CL05C102JB5NNNC is a
1 nF, 50 V C0G 0402 timing capacitor. C51205 / CL31B475KBHNNNE is a
4.7 µF, 50 V X7R 1206 output capacitor; Samsung's bias and temperature
characteristics are recorded in `../research/power-revision-sources.json`.
Their symbols reuse the existing two-terminal capacitor geometry and the
matching 0402/1206 lands. R17 uses C159141 / RTT021131FTH (1.13 kΩ, 1%,
0402). R20/R21 use C852929 / RT0402BRD0782KL and C851038 /
AT0402BRD074K75L (82 kΩ and 4.75 kΩ, 0.1%, 25 ppm/°C, 0402), reusing
R0402 geometry. Exact MPNs and JLC public stock were checked; inventory is
not reserved. Datasheet links are stored in each symbol. These selections
and generated files do not establish an operating current rating.

## Historical 60 V stage, 2026-10-13

The preceding design superseded the intermediate TPS259470L/R17/C8 selections
above with TPS26630RGER C1850276, LM74700QDBVTQ1 C2653623, CSD19537Q3T
C134143, TPS3710DDCR C140262, TVS2200DRVR C523793 and PMEG4030ER-QX
C5709679. These symbols and lands were imported with easyeda2kicad 1.0.1.
Imported models were removed, legends moved to F.Fab and courtyards expanded
to include pads/body plus 0.25 mm. All fitted parts are on F.Cu. R17 is now
5.1 kohm C25905 and C8 is 22 nF 50 V C1532. C14-C16 are 1 uF 50 V C28323.
R25 is a separate 10 kohm 0.1% IMON resistor. See the circuit source and
power research records for exact MPNs, connections and source hashes.

`prepare_protection_stencil.py` applies the TPS26630 RGE0024H exposed-pad
stencil example from TI drawing 4219016/A: four 1.188 mm rounded squares at
+/-0.694 mm, approximately 78% coverage for the example 0.125 mm stencil.
The copper land remains 2.7 mm square. Factory stencil/process review and
X-ray remain required. No drill is placed under that exposed-pad copper.


## Cost-reduced stage, 2026-10-14

The current circuit uses MX26631DL C18197523, AON7264E C431191, BSS138-7-F
C40912 and TPS3701DDCR C132788. TVS2200DRVR C523793 and PMEG4030ER-QX
C5709679 remain. R17 is 11 kohm C25749; the upstream undervoltage divider
uses 82.5 kohm C852928 and 7.68 kohm C852919, both 0.1%, 25 ppm/C.
C8 remains 22 nF / 50 V, C14/C16 are 1 uF / 50 V, and C15 is removed.
The current exact population is defined by `../circuit.py`.

Imported symbols and footprints were checked against manufacturer pinouts.
Legends remain on fabrication layers. The MX26631 2.7 mm exposed land shares
the four-window paste geometry described above; that TI stencil example is
only a provisional geometry choice, not Maxin process approval. Confirm the
paste design and reflow process with the assembler. Adjacent thermal vias
remain outside solder lands; assembled-board thermal qualification is required.

The [cost screen](../research/cost-down-screen.json) records exact part numbers,
dated stock/prices and the Maxin V12 datasheet hash. Supplier render models
are cached in `models/` and hash-pinned in `../../docs/render-models.json`.
The illustration is not a physical fit or assembly-process qualification.


Cost follow-up, 2026-10-15: R20 now uses the already reviewed C852928 /
RT0402BRD0782K5L, sharing R27's 82.5 kohm, 0.1%, 25 ppm/C selection.
The R0402 footprint and connections are unchanged. OVLO is recalculated in
`hardware/power_review.py`; UVLO is unchanged. C852929 remains historical.
