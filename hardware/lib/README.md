# Local component library

Exact MPN metadata and vendor symbols were imported from EasyEDA/LCSC with
`easyeda2kicad` 1.0.1 on 2026-10-11. Each fitted component in `hardware/circuit.py`
selects its LCSC C-number; `hardware/library.py` reads the associated metadata
and assigns reviewed electrical pin types. The schematic generator draws its
own typed symbols instead of using the importer's unspecified pin types.

The active CH32V003 footprint is the KiCad 10.0.6 TSSOP-20 land pattern.
The selected G-Switch GT-USB-7010ASV connector is derived from a pinned,
unmodified KiCad footprint kept in `hardware/research/usb-c`.
Run `python3 scripts/prepare_lowcost_usb.py` to reproduce the selected file.
The result has been checked to regenerate byte-for-byte.

Common USB power/ground contacts are merged into single physical lands, and
shell stake numbers match the source netlist. A 25 um tailward SMT-row shift
retains the manufacturer's land-pattern tolerance while clearing the locating
holes. The courtyard follows the shell/stakes with 0.10 mm allowance. This
preserves the Pico mounting holes but does not provide ordinary screw-head
clearance. See [mechanical fit](../../docs/mechanical.md).

The imported ME6211 SOT-23-5 land pattern uses pin 1 VIN, 2 GND, 3 CE, 4 NC
and 5 VOUT. Imported legends are on fabrication layers; board silkscreen is
explicit in the generator. Unavailable 3D model references are removed.
Normal builds use these local files rather than workstation-global libraries.

The library contains only the 17 exact fitted LCSC parts and their active
footprints, plus generated Pico header and test-pad geometry. Duplicate import
records have been removed. `scripts/prepare_footprints.py` reproduces the
current MCU land pattern and normalizes the active local library.

KiCad library source: [kicad-footprints](https://gitlab.com/kicad/libraries/kicad-footprints).
Its [CC BY-SA 4.0 license with library exception](https://www.kicad.org/libraries/license/)
applies to those upstream files. EasyEDA/LCSC data has separate provenance;
the probe firmware's MIT license does not relicense third-party CAD data.

`Pico_Header.kicad_mod` is generated from our mechanical contract. It includes
40 header lands, 40 connected castellated half-holes, and four 2.1 mm mounting
holes. `TestPad_1mm` is a local PCB feature, not a purchased component. Review
all exact manufacturer package drawings and JLC assembly orientation before
releasing a manufacturing package.

The ST USBLC6-2P6 ESD device, C15999, uses a locally generated SOT-666
footprint from [ST DS4260 Rev 7, Figure 21](https://www.st.com/resource/en/datasheet/usblc6-2.pdf).
Run `python3 scripts/prepare_esd_footprint.py` to reproduce it. The six lands
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
