# ch32-pico development plan

The current implementation uses two CH32V003F4P6 devices, a G-Switch
GT-USB-7010ASV USB-C socket and two ME6211C33M5G-N 3.3 V LDOs.
The application MCU has a dedicated switched supply. The programmer runs
source-built rv003usb firmware and controls target power through the second
regulator's enable input. A GPIO does not supply target current.

## Fixed requirements

- Preserve the Pico's 21 x 51 x 1 mm outline, all header/castellation positions,
  power and ground pin positions, and all four 2.1 mm mounting holes.
- Match useful peripheral positions without duplicating GPIOs into unused pins.
- USB-C power and ordinary target programming through the same cable.
- Fully open programmer firmware, exact LCSC parts and JLC assembly outputs.
- Minimize component and assembly cost. Five KiKit panels carry four boards each.
- Keep circuit, placement, routing constraints and generated outputs reproducible.

The user accepted USB/5 V-oriented LDO power, one-time external flashing of
the onboard programmer, and a minichlink debug console instead of a CDC
serial bridge. Initial programmer provisioning and recovery use test pads.
Routine application updates use USB HID. The two target UART pins remain free.

## Engineering workflow

The RestoreKit reference established the approach: code defines the electrical
model and placement; KiCad independently checks generated files; actual
router output determines which route is kept. The current design has one
circuit source and one checked board checkpoint.

1. Check every source pin against the exported schematic netlist and run ERC.
2. Generate placement and verify source pad nets, fixed Pico geometry and DRC.
3. Add explicit USB and local supply paths. Keep their geometry protected.
4. Route both engines from the same prepared input and compare KiCad results.
5. Save only a route with zero DRC violations and zero open connections.
6. Export single-board and four-board panel previews, checking BOM/CPL coverage,
   placement angles, panel translations and preserved copper geometry.
7. Review JLC rotations, order-specific stock/attrition, fabrication options,
   assembly cost and panel handling before placing an order.
8. Qualify prototypes for cable fit, rail behavior, USB power states,
   programmer provisioning, flash/readback, reset recovery and header functions.

The current layout uses the checked four-layer JLC04101H-3313 stackup.
A two-layer version could lower fabrication cost but would need a separate
routing and ground-return review. Do not advertise current component cost as
an assembled-board quote or claim untested hardware compatibility.
