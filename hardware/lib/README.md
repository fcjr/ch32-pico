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

The eFuse copper follows TI drawing 4225183/A. Overlapping rectangles share
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
