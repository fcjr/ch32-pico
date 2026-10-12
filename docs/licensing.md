# Licensing

Copyright © 2026 ch32-pico contributors.

The project uses two permissive licenses, so you can modify the design and
build or sell boards without a requirement to publish your modifications.
Keep the required notices and record changes when redistributing modified
hardware source. The full license texts govern the grants.

| Material | License |
| --- | --- |
| Original Python code in `hardware/`, `scripts/`, and `tests/`; build files; original firmware changes and examples | [MIT](../LICENSES/MIT.txt) |
| Original hardware design, including circuit, header mapping, placement, routing, schematic, PCB, original footprints, panel and manufacturing outputs | [CERN-OHL-P-2.0](../LICENSES/CERN-OHL-P-2.0.txt) |
| Original README and written documentation | MIT |
| Third-party firmware, CAD libraries, supplier data, screenshots and 3D models | Their existing licenses and notices, as described below |

Python expresses much of the hardware. MIT applies to the program code;
CERN-OHL-P-2.0 applies to the original hardware design it expresses and the
design outputs. Neither grant overrides third-party rights in incorporated
material. License and attribution files accompany generated manufacturing
and firmware packages.

The hardware license is the **Permissive** variant of CERN OHL version 2.
It was chosen to match the permissive software license. It allows commercial
manufacture and distribution, includes a patent grant, and requires notices
and dated descriptions of modifications to redistributed modified source.
See the [official CERN OHL license collection](https://ohwr.org/licences/).
The software uses the [standard MIT license](https://opensource.org/license/mit).

## Third-party software

- [rv003usb](https://github.com/cnlohr/rv003usb), revision
  `5524a833c656a6007fca9f6c947fd49ddcc16eb6`, supplies the onboard programmer.
  Its [MIT notice](../LICENSES/third-party/rv003usb-MIT.txt) is retained.
  The board patch is original MIT-licensed work. Upstream bitbang files offer
  MIT or NewBSD; this project uses the MIT option.
- [ch32fun](https://github.com/cnlohr/ch32fun), revision
  `1e4887e11d4bfa739ed5604524b69f5be9f9275b`, supplies target support and
  minichlink. Its [MIT notices](../LICENSES/third-party/ch32fun-MIT.txt) name
  CNLohr and the other contributors. Its bundled arithmetic support retains
  [the upstream notices](../LICENSES/third-party/ch32fun-libgcc.txt).
- KiCad, KiKit, KiCadRoutingTools, Freerouting, easyeda2kicad and the compiler
  are external build tools, not relicensed by this project. Dependency
  checkouts and toolchain archives retain their upstream notices.

## CAD and reference material

The KiCad-derived footprints retain
[CC BY-SA 4.0 with the KiCad library exception](https://www.kicad.org/libraries/license/).
The exception allows their use in circuit designs without forcing the
resulting board design to use CC BY-SA. Changes to the library files
themselves remain subject to the library license. The local
[library notes](../hardware/lib/README.md) identify their provenance and changes.

EasyEDA/LCSC-imported symbols and land patterns retain their upstream rights.
The project does not claim to relicense them under MIT or CERN OHL. The import
metadata and [preparation scripts](../scripts/prepare_footprints.py) identify
their sources. An explicit redistribution license for those imported CAD
records has not been established here; that remains a public-release review
item. Original circuit and PCB design work is covered by the grants above.

Supplier 3D models are downloaded into the ignored `build/render/` cache,
not vendored as project source. [The render manifest](render-models.json)
records their source, importer version and hashes. The rendered illustrations
include those models; the project license does not grant rights to the
underlying supplier models. Manufacturer datasheets and JLC screenshots
also remain third-party reference material.

## Name and logo

The Left Shift Logical name and double-chevron logo identify the original
project. The silkscreen adapts the mark from the Left Shift Logical website
source. No trademark rights or endorsement are granted by these licenses.
See section 7.2 of CERN-OHL-P-2.0 for use of licensors' names and logos.
