# Local component library

Exact MPN metadata and vendor symbols were imported from EasyEDA/LCSC with
`easyeda2kicad` 1.0.1. Each fitted component in `hardware/circuit.py`
selects its LCSC C-number; `hardware/library.py` reads the associated metadata
and assigns reviewed electrical pin types. The schematic generator draws its
own typed symbols instead of using the importer's unspecified pin types.
Normal builds use the checked-in files and do not depend on the workstation's
library.

The library contains only the fitted parts plus C1525, a 16 V 100 nF
capacitor kept so regression tests can prove a low-voltage substitution is
rejected. Voltage checks read vendor descriptions independently of circuit
value labels.

## Parts

- CH32X035C8T6, [C29779902](https://www.lcsc.com/product-detail/C29779902.html),
  on the KiCad LQFP-48 7 × 7 mm land pattern. USBLC6-2SC6, C7519, uses the
  KiCad SOT-23-6 pattern. `scripts/prepare_footprints.py` vendors those
  patterns and moves imported legends to fabrication layers.
- GT-USB-7010AW USB-C receptacle, C963411. Its footprint follows the
  manufacturer drawing. The AW drawing specifies 5 A on VBUS. Its SMT row
  has a 50 µm tailward adjustment within the manufacturer's land-pattern
  tolerance to clear the locating holes. The socket mouth sits 0.30 mm beyond
  the short board edge; there are no Pico mounting holes.
- TVS2200DRVR, C523793, WSON-6 with exposed ground pad. Imported with
  easyeda2kicad; model removed, legends moved to F.Fab and courtyard expanded
  to include pads/body plus 0.25 mm.
- SY8301ABC, C2927130, on the EasyEDA SOT-23-6 land with legends moved to
  F.Fab; its 47 kΩ / 15 kΩ feedback resistors are C25792 / C25756.
  SWPA5040S4R7MT 4.7 µH inductor, C48496.
  B5819W Schottky diodes, C8598, SOD-123.
- 100 nF capacitors are Samsung CL05B104KB54PNC,
  [C307331](https://www.lcsc.com/product-detail/C307331.html), verified as
  50 V, X7R, ±10%, 0402. The 10 µF buck input capacitor is CL31A106KBHNNNE,
  C13585, 50 V 1206. Output capacitors are CL21A226MPQNNNE, C29277, 10 V 0805.
- RESET and BOOT use XUNPU TS-1088-AR02016, C720477, a JLC Basic part, on
  its `SW-SMD_L3.9-W3.0-P4.45` land pattern: pads span 5.59 mm overall with
  a 3.13 mm inner gap and 1.86 mm width. The AR variant has no locating peg,
  is 2.0 mm high and has 1.6 N force. The 2.5 mm TS-1088-AR02516 (C720478)
  fits the same copper if it is the one in stock; see
  `hardware/research/switch-replacement.json`.
- 0402 resistors and the 0603 LED use the generic imported lands.

Supplier render models are cached in `build/render/` and hash-pinned in
`../../docs/render-models.json`. The illustration is not a physical fit or
assembly-process qualification.

## Board features

`Pico_Header.kicad_mod` is generated from our mechanical contract. It includes
40 header lands and 40 connected castellated half-holes. `TestPad_1mm` and
`TestPad_0.6mm` are local PCB features, not purchased components; the 0.6 mm
pad serves PB3 where a 1 mm pad would crowd nearby markings.

`SolderJumper_Open.kicad_mod` is an original PCB feature. Two 1 × 1.5 mm pads
have a 0.30 mm gap, mask openings and no paste. SJ1 is excluded from BOM and
placement files and must remain open during assembly.

`USB_Probe_Inline` is an original paste-free 1 × 0.1537 mm contact that stays
inside the existing USB trace. None of these features is assembled.

Review all exact manufacturer package drawings and JLC assembly orientation
before releasing a manufacturing package.

## License notices

Original ch32-pico design work uses CERN-OHL-P-2.0. Imported records retain
their upstream rights. See [project license scope](../../docs/licensing.md),
the [KiCad library notice](../../LICENSES/third-party/KiCad-library-license.md)
and [CC BY-SA 4.0 text](../../LICENSES/third-party/CC-BY-SA-4.0.txt).
KiCad library source: [kicad-footprints](https://gitlab.com/kicad/libraries/kicad-footprints).
Its [CC BY-SA 4.0 license with library exception](https://www.kicad.org/libraries/license/)
applies to those upstream files; KiCad library contributors retain copyright
in them. EasyEDA/LCSC data has separate provenance. Local changes remove
unavailable models, move imported silk to fabrication layers, and adapt the
connector pad aliases, SMT row and courtyard as documented above.
