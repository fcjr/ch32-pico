# SPDX-License-Identifier: MIT
set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

kicad_python := env('KICAD_PYTHON', '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3')

# List available project commands.
default:
    @just --list

# Install the locked Python tools and the KiCad-compatible KiKit environment.
setup: panel-dependencies
    uv sync --locked

# Generate the complete JLCPCB fabrication bundle from the checked board.
jlcpcb: manufacturing-preview panel-preview order-review
    uv run --locked python -m hardware.jlcpcb

# Generate checked single-board Gerbers, drill, BOM and placement files.
manufacturing-preview: check
    uv run --locked python -m hardware.manufacturing

generate:
    uv run --locked python -m hardware.generate
    uv run --locked python -m hardware.outputs

schematic: generate
    uv run --locked python -m hardware.schematic

electrical-check: schematic
    kicad-cli sch erc --exit-code-violations --severity-all --format json -o build/electrical-erc.json build/ch32-pico.kicad_sch
    kicad-cli sch export netlist --format kicadxml -o build/ch32-pico.net.xml build/ch32-pico.kicad_sch
    uv run --locked python -m hardware.verify

placement: schematic
    "{{kicad_python}}" -m hardware.pcb

placement-check: placement
    kicad-cli pcb drc --severity-all --format json -o build/placement-drc.json build/ch32-pico-placed.kicad_pcb
    uv run --locked python -m hardware.verify_placement

# Run ERC, circuit/placement checks and regression tests.
check: electrical-check placement-check
    "{{kicad_python}}" -m hardware.critical_routes
    uv run --locked python -m unittest discover -s tests -v
    kicad-cli pcb drc --exit-code-violations --severity-all --format json -o build/mechanical-drc.json build/ch32-pico-mechanical.kicad_pcb

# Compare the pinned routers on a complete fresh board.
route: placement-check
    uv run --locked python scripts/router_dependencies.py
    uv run --locked python -m hardware.routing --kicad-python "{{kicad_python}}"

# Reproduce the current Rev E incremental routing from the Rev D checkpoint.
route-jumper: check
    uv run --locked python -m hardware.jumper_routing

# Retained Rev D migration, gated to that revision.
route-enable: check
    uv run --locked python scripts/router_dependencies.py
    uv run --locked python -m hardware.enable_routing

# Check and save the routed board and layer previews in hardware/review/.
review:
    uv run --locked python -m hardware.review

# Render the checked PCB front and back for the README.
render:
    uv run --locked python scripts/render_board.py

preview: placement
    kicad-cli pcb export svg --mode-single --layers F.Cu,F.Fab,Edge.Cuts --fit-page-to-board --exclude-drawing-sheet -o build/placement.svg build/ch32-pico-placed.kicad_pcb
    kicad-cli sch export svg -o build/schematic-svg build/ch32-pico.kicad_sch

# Use KiCad's native Python for pcbnew/wx; install only into a local environment.
panel-dependencies:
    uv venv --no-project --allow-existing --system-site-packages --python "{{kicad_python}}" build/kikit-venv
    uv pip sync --require-hashes --python build/kikit-venv/bin/python scripts/kikit-requirements.txt

panel-preview: panel-dependencies
    uv run --locked python -m hardware.panel

order-review:
    uv run --locked python -m hardware.order_review
    uv run --locked python -m hardware.assembly_review

procurement:
    uv run --locked python scripts/procurement.py

cost-review:
    uv run --locked python -m hardware.cost_review

power-review:
    uv run --locked python -m hardware.power_review

usb-review:
    uv run --locked python -m hardware.usb_review

# Retained Rev A tools; revision guards prevent use on the X035 board.
dependencies:
    uv run --locked python scripts/lowcost_firmware.py

firmware: lowcost-firmware

lowcost-firmware:
    uv run --locked python scripts/lowcost_firmware.py

lowcost-review:
    uv run --locked python scripts/lowcost_review.py

target-demo:
    uv run --locked python scripts/target_demo.py
