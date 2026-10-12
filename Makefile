# SPDX-License-Identifier: MIT
PYTHON ?= python3
KICAD_CLI ?= kicad-cli
KICAD_PYTHON ?= /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3

.PHONY: generate check preview dependencies firmware schematic electrical-check placement placement-check route procurement review manufacturing-preview power-review usb-review panel-dependencies panel-preview cost-review

manufacturing-preview: check placement-check
	"$(KICAD_PYTHON)" -m hardware.critical_routes
	$(PYTHON) -m hardware.manufacturing

usb-review:
	$(PYTHON) -m hardware.usb_review

power-review:
	$(PYTHON) -m hardware.power_review

review:
	$(PYTHON) -m hardware.review

route: placement-check
	$(PYTHON) scripts/router_dependencies.py
	$(PYTHON) -m hardware.routing --kicad-python "$(KICAD_PYTHON)"

procurement:
	$(PYTHON) scripts/procurement.py

dependencies:
	$(PYTHON) scripts/lowcost_firmware.py

firmware: lowcost-firmware

generate:
	$(PYTHON) -m hardware.generate
	$(PYTHON) -m hardware.outputs

schematic: generate
	$(PYTHON) -m hardware.schematic

electrical-check: schematic
	$(KICAD_CLI) sch erc --exit-code-violations --severity-all --format json -o build/electrical-erc.json build/ch32-pico.kicad_sch
	$(KICAD_CLI) sch export netlist --format kicadxml -o build/ch32-pico.net.xml build/ch32-pico.kicad_sch
	$(PYTHON) -m hardware.verify

check: electrical-check
	$(PYTHON) -m unittest discover -s tests -v
	$(KICAD_CLI) pcb drc --exit-code-violations --severity-all --format json -o build/mechanical-drc.json build/ch32-pico-mechanical.kicad_pcb

placement: schematic
	"$(KICAD_PYTHON)" -m hardware.pcb

placement-check: placement
	$(KICAD_CLI) pcb drc --severity-all --format json -o build/placement-drc.json build/ch32-pico-placed.kicad_pcb
	$(PYTHON) -m hardware.verify_placement

preview: placement
	$(KICAD_CLI) pcb export svg --mode-single --layers F.Cu,F.Fab,Edge.Cuts --fit-page-to-board --exclude-drawing-sheet -o build/placement.svg build/ch32-pico-placed.kicad_pcb
	$(KICAD_CLI) sch export svg -o build/schematic-svg build/ch32-pico.kicad_sch

# The venv uses KiCad's Python and does not modify/sign the installed app.
panel-dependencies:
	"$(KICAD_PYTHON)" -m venv --system-site-packages build/kikit-venv
	build/kikit-venv/bin/python -m pip install -r scripts/kikit-requirements.txt

panel-preview:
	$(PYTHON) -m hardware.panel

cost-review:
	$(PYTHON) -m hardware.cost_review

.PHONY: order-review
order-review:
	$(PYTHON) -m hardware.order_review
	$(PYTHON) -m hardware.assembly_review

.PHONY: quote-package
quote-package:
	$(PYTHON) -m hardware.quote_package

.PHONY: lowcost-firmware lowcost-review
lowcost-firmware:
	$(PYTHON) scripts/lowcost_firmware.py

lowcost-review:
	$(PYTHON) scripts/lowcost_review.py

.PHONY: target-demo
target-demo:
	$(PYTHON) scripts/target_demo.py

.PHONY: render
render:
	$(PYTHON) scripts/render_board.py
