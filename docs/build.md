# Build and routing

`hardware/circuit.py` defines all 174 physical terminals, including explicit
NCs. `hardware/design.py` owns the Pico geometry and header mapping.
`hardware/placement.py` owns component positions. Local library files contain
exact LCSC identifiers and reviewed package geometry.

`make check` generates the six-sheet schematic, runs ERC, compares KiCad's
exported netlist to the circuit, and runs fault/regression checks.
`make placement-check` generates the four-layer PCB and verifies pad nets,
component positions, all Pico header/castellation/mounting-hole geometry and DRC.
Placement may have open connections. A saved route must have none.

## Commands and tools

Use Python 3.12+, KiCad CLI 10.0.6 and KiCad's bundled Python for PCB API
operations. The validated firmware toolchain is xPack RISC-V GCC 14.2.0-3.
Routing uses the pinned KiCadRoutingTools checkout and Freerouting 2.5.0
with Java 25. The Makefile exposes `PYTHON`, `KICAD_CLI` and `KICAD_PYTHON`
overrides for local installations.

```sh
make check                   # schematic ERC, netlist parity, regression checks
make placement-check         # source/PCB parity and placement DRC
make firmware target-demo    # build firmware, never flash attached devices
make route                   # run both routers and independent checks
make review                  # save a passing route and current silkscreen
make manufacturing-preview   # checked single-board Gerbers, BOM and CPL
make panel-dependencies      # pinned local KiKit environment
make panel-preview           # four-board panel and verified assembly files
make procurement cost-review # refresh public inventory and dated estimate
make order-review            # quantity/attrition scenario and orientation guide
make quote-package           # bundle verified inputs for factory review
make render                  # front/back README render of the checked PCB
```

Do not reroute merely to change artwork. `hardware/branding.py` owns the
project name, revision and Left Shift Logical silkscreen. Change
`BOARD_REVISION` in `hardware/design.py` when releasing a board revision;
the silkscreen, schematic and manufacturing manifest share this value. Placement generation and
`make review` apply the same artwork. The latter rechecks the existing routed
candidate with KiCad before saving it. Regenerate manufacturing and panel
outputs after changing the saved board.

## Rendering

Install `easyeda2kicad==1.0.1` and Pillow in the Python environment used for
rendering. `make render` downloads any missing supplier models into ignored
`build/render/`, checks them against [the pinned hashes](render-models.json),
and attaches them to a disposable copy of the checked board. It does not
change the source PCB or routing. The capacitor and resistor models represent
the common package sizes; markings and colors are illustrative.

KiCad renders the front and back separately. The script places those views
side by side in `docs/images/ch32-pico.png`, embedded by the README, and writes
the source PCB hash in `docs/images/render.json`. `ch32-pico-front.png` and
`ch32-pico-back.png` are also available separately.

The USB model uses a +1.325 mm model-Y offset because its supplier origin
is different from the reviewed KiCad footprint. At J2's 180-degree board
rotation its mouth is at board Y = 4.825 - 5.000 + 1.325 = 1.150 mm.
Its 8.94 mm width is centered on X = 10.5 mm. The render therefore shows
the intentional recess, not a flush socket. The two IC package models
also have explicit rotations to align with the reviewed pin-one locations.
A CAD illustration does not establish cable fit or factory model rotations.

## Firmware

`make firmware target-demo` builds the programmer and a printf example from
pinned open-source inputs. It never flashes a connected device. Install the
RISC-V compiler described in [firmware notes](../firmware/lowcost/README.md).
The compiler prefix is configurable with `RISCV_PREFIX`.

## Routing

KiCadRoutingTools is pinned to `ad7f24deb8fbffa6c498a09a6ebda46e012c37ff`.
The workstation checkout is `~/git/KiCadRoutingTools`, with its Rust extension
installed in `.venv`. On another workstation, clone
[the upstream repository](https://github.com/drandyhaas/KiCadRoutingTools),
check out that revision and follow its `build_router.py` instructions.
`python3 -m hardware.routing --krt PATH` selects another checkout and rejects
wrong revisions or tracked changes.

`scripts/router_dependencies.py` fetches and checksum-verifies Freerouting
2.5.0. Java 25 is used, with a project-local profile and analytics disabled.
The Java build avoids the native macOS distribution's serialization failure.

Both engines get the same board after explicit USB, supply and MCU pin-exit
routes and completed ground/main-supply plane connections. The layout uses
JLC04101H-3313: F.Cu and B.Cu signals, In1.Cu GND, In2.Cu main 3.3 V and
signals. This is a four-layer board even with two signal layers selected.

Trace/space floors are 0.15 mm. All vias are 0.45/0.20 mm. The two USB traces
spread outward by 0.10 mm beneath the ESD package, allowing its VBUS via to
use the same size without cutting the sampled ground return. JLC's quote-form
note allows this size at standard multilayer via pricing; confirm it at checkout.
Via/NPTH drill-to-copper clearance is 0.20 mm. Plated-pad hole-to-copper and
hole-to-hole constraints are 0.30 mm and 0.45 mm. The native and DSN adapters
use the same fabrication rules. No DRC categories are suppressed.

Every delivered route is independently refilled and checked by KiCad.
Additional gates check source pad nets, component positions, vias outside
paste, preserved critical trace/via geometry, no foreign ground-layer tracks,
and sampled GND reference beneath every USB signal trace. A successful
router process exit does not establish connectivity or DRC success.

The adapter disables stub-layer swapping and sets `KICAD_RIP_PREEXISTING=0`
to preserve established copper during plane repair. Cleanup may remove unused
vias and short dead stubs only when per-net connectivity is preserved and
no new DRC issues appear. Required seed copper must still survive grading.

Python routing processes finish normally. There is no kill or subprocess
routing deadline. Logs record commands and environment. The current comparison
is `build/routing/comparison.json`; `make review` saves a passing candidate,
source checks, remaining engineering reviews and layer SVGs in `hardware/review`.

Two complete KiCadRoutingTools runs produced identical trace/via geometry:
`7f151ddb4ce39bf99e24f3bada5c8eec08711009666fdaa43e54e01be54f4993`.
The selected board has zero DRC violations, zero open connections, 97 vias
and about 880 mm of trace. Freerouting leaves two connections open.
The reproduction record is `hardware/routing-reproducibility.json`.

## Manufacturing previews

Run `make manufacturing-preview` after saving a route, then `make panel-preview`
for the four-board KiKit panel. BOM and CPL coverage, placement coordinates,
rotations, translated pad nets and copper geometry are checked independently.
See [manufacturing](manufacturing.md) and [panelization](panelization.md).

These checks do not establish physical cable fit, assembly model rotations,
USB performance, current ratings or component allocation. The prototype
qualification items remain explicit in each manifest.
