# Build and routing

The project uses `uv` for Python environments and `just` for commands.
`just jlcpcb` generates the fabrication bundle from the checked
board. It does not reroute the design, submit an order or reserve parts.

## Tools and environments

Install `uv`, `just` and KiCad 10.0.6 with `kicad-cli` on your PATH. The general
Python tools use Python 3.13, selected by `.python-version`, and the dependencies
in `uv.lock`. `uv run --locked` creates and synchronizes `.venv` automatically.

KiCad's native `pcbnew` and `wx` modules must use KiCad's own Python interpreter.
The default macOS path is:

```text
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
```

Set `KICAD_PYTHON` to the appropriate interpreter on another installation.
KiKit runs in `build/kikit-venv`, which inherits those native modules and installs
hash-locked packages through `uv pip sync`. It does not modify or re-sign KiCad.
This separate Python 3.9 environment is intentional for the validated macOS
KiCad bundle; the main project's Python version does not replace it.

```sh
just setup     # optional upfront installation; jlcpcb also prepares its tools
just --list    # all available commands
just check     # schematic ERC, netlist parity, placement and regression checks
just jlcpcb    # checked board, four-up panel, assembly review and upload bundle
just render    # front/back README image from the checked PCB
```

The panel environment pins are in `scripts/kikit-requirements.in` and its
hash-locked `scripts/kikit-requirements.txt`. To deliberately update the lock:

```sh
uv pip compile --python-version 3.9 --generate-hashes scripts/kikit-requirements.in -o scripts/kikit-requirements.txt
```

## Design sources

`hardware/circuit.py` defines every component terminal, including explicit NCs.
`hardware/design.py` owns the Pico outline and header allocation.
`hardware/placement.py` owns component positions; `hardware/diagnostics.py`
defines the diagnostic pad nets, locations and labels. The local library holds
reviewed package geometry and exact LCSC identifiers.

`hardware/branding.py` owns the name, revision and Left Shift Logical logo.
`hardware/markings.py` checks legends against actual pad nets and MCU pins,
board side, text orientation and placement. `BOARD_REVISION` sets the schematic,
silkscreen and manufacturing revision. See [markings](markings.md).

There are 40 header holes and 40 castellations, and no mounting holes.
Placement checks may report open connections. Routed-board and panel checks
require zero open connections and zero DRC violations.

## Routing

To reproduce the checked layout:

```sh
just route-power
just review
just render
just jlcpcb
```

`route-power` retrieves the hash-pinned PCB at commit `461bf67` and applies
the saved, reviewed layout changes. It then runs independent geometry,
connectivity and source-parity checks. A clone containing that commit is
required. This reproduces the layout; it does not qualify its current rating.

For a new placement or a broader routing change, `just route` compares the
pinned KiCadRoutingTools and Freerouting engines from the generated seed.
KiCadRoutingTools must be checked out at
`ad7f24deb8fbffa6c498a09a6ebda46e012c37ff` in `~/git/KiCadRoutingTools`, with its
Rust extension built in that checkout's `.venv`. Follow the
[upstream build instructions](https://github.com/drandyhaas/KiCadRoutingTools).
For the full-board router, `uv run python -m hardware.routing --krt PATH` selects
another checkout; it rejects changed revisions or tracked modifications.

The full comparison downloads checksum-pinned Freerouting 2.5.0 and uses Java
25. Analytics are disabled. Python routing processes finish normally, with no
forced termination or routing deadline.

`just review` saves a passing candidate to `hardware/review/`, including the
PCB, DRC report, validation JSON and layer SVGs. Artwork-only edits can reuse
an existing routed candidate. Regenerate the panel and fabrication files after
saving a changed board. A fresh clone can run `just jlcpcb` from the committed
checked board without router installation or a reroute.

The four-layer stack is F.Cu signals, In1.Cu ground, In2.Cu 3.3 V and signals,
and B.Cu signals. The USB pair stays entirely on F.Cu. Its two probe contacts
expose existing trace copper without adding branches or vias. Independent gates
check source/PCB parity, critical geometry, USB ground reference, paste
clearance and the power layout. Ground stitches use ordinary
tented 0.45/0.20 mm vias. The surge clamp must reach at least two local
ground vias within 2.5 mm through top copper at least 0.4 mm wide, and pin 40
must keep both its 1.2 mm bottom trunk and its front-layer feed. These checks
do not establish USB or thermal compliance.

## Rendering

`just render` uses locked Pillow and easyeda2kicad dependencies. Missing supplier
models download into ignored `build/render/`, then must match the committed
[model hashes](render-models.json). The switch model's imported materials are
fully transparent. Its manifest entry requests an opaque render copy, preserving
the original cached model and its hash. Models attach only to a disposable render
copy of the PCB. The render copy uses KiCad SVG plot strokes for silkscreen
to avoid intermittent missing glyphs in the macOS 3D text renderer. The checked
PCB keeps editable text, and fabrication exports use it directly. KiCad renders both sides, and Pillow combines them into
`docs/images/ch32-pico.png`. `render.json` records the checked board hash.
The front and back PNGs are also saved separately. The connector mouth is at
the board edge in the current placement. A CAD render does not qualify cable
fit, assembly orientation or printed legibility.

## Fabrication outputs

`just jlcpcb` runs the source/regression checks, rechecks the saved board,
exports single-board manufacturing files, prepares KiKit, builds the four-up
panel, checks its DRC and assembly-file parity, and creates the final bundle.
It fails on stale or mismatched inputs.

Upload `build/jlcpcb/gerbers.zip`, `bom.csv` and `cpl.csv` together. The full
`build/ch32-pico-jlcpcb.zip` also contains factory notes, orientation guides,
stock/cost review, licenses and a hash manifest. Read
[manufacturing](manufacturing.md) and [panelization](panelization.md) before
using those files. All `build/` files are ignored by Git. Commit sources, tool
locks and the checked board; attach an exact bundle to a tagged release when
preparing a fabrication release.

## Firmware

The X035 PD/USB application and assembled-board qualification remain pending.
`firmware/pd/` holds the portable PD sink policy and its tests. See the
[design notes](design.md) for current behavior and limitations.
