# USB-C and Pico mechanical fit

## Connector and footprint

The design retains the 21 x 51 x 1 mm Pico board, all
40 header positions and castellations, and **all four 2.1 mm mounting
holes at their original coordinates**. Removing or moving the upper
holes is not an accepted cost reduction.

The current circuit and its isolated fit coupon use **G-Switch GT-USB-7010ASV, C2988369**.
[JLC's exact-part listing](https://jlcpcb.com/partdetail/C2988369) returned
$0.0878 each for 1–49 pieces and 85,205 reported stock on 2026-10-12 UTC.
This is the component price, excluding assembly and shipping. Stock is not
reserved; the complete order and any pre-purchase minimum still need checking.
The latest dated observation is in `hardware/procurement-observation.json`.

At (10.5, 4.825) mm, rotated 180 degrees, its mouth is **1.15 mm behind
the board edge**. The coupon preserves the full Pico header and hole pattern
and passes KiCad DRC with zero violations under the existing manufacturing
rules, including 0.30 mm plated-hole-to-copper and 0.45 mm plated-hole spacing.
No DRC exclusions were added. A flush-mouth control placement fails ten checks,
including shell-pad collisions with the upper mounting holes.

Reproduce the coupon with KiCad's Python, then check it:

```sh
"$KICAD_PYTHON" scripts/usb_candidate_fit.py
kicad-cli pcb drc --exit-code-violations --severity-all --format json \
  -o build/usb-fit/gswitch-drc.json build/usb-fit/gswitch.kicad_pcb
```

The coupon establishes placement feasibility. The full board has separate
routing and source-parity gates.
The [manufacturer drawing](https://datasheet.lcsc.com/datasheet/pdf/a1d5a66cf718dd88763ab794dba802b2.pdf?productCode=C2988369)
shows **1.85 mm reference** clearance between the receptacle mouth and a
mated plug housing, leaving 0.70 mm nominally at this placement. It does not
specify a guaranteed minimum, so the calculation cannot establish cable fit.
Check plug insertion, connector/board tolerances, the 1 mm PCB stake joint,
and underside clearance on prototypes before manufacturing release.

The wider USB-C shell still restricts ordinary M2 heads at the upper holes:
the nominal KiCad shell outline leaves only 0.18 mm beside each drill.
Keeping the hole pattern does not guarantee compatibility with every Pico
standoff or enclosure. This limitation must remain visible in compatibility
claims; the requirement to keep every hole remains fixed.

## Mounting compatibility limits

The upper mounting holes remain in their Pico positions, but the USB-C shell
is only 0.18 mm from each drill edge nominally. A head wider than 2.46 mm
would touch the nominal shell even before tolerance allowances. **Ordinary
M2 screw heads, nuts and top-side standoffs are not supported at these two
holes.** Use the headers/castellations for mounting; a carrier using locating
pins needs its own tolerance review. The lower holes are not near the socket.

The connector's retention stakes should remain within the board thickness;
the locating pegs and solder fillets still need an underside fit check before
soldering the module directly onto a carrier. All populated components remain
on top. USB-C also needs a different enclosure opening from a Pico's micro-USB.

## Footprint adjustments and sourcing

The vendored KiCad 10.0.6 G-Switch footprint keeps the manufacturer's pad sizes,
drills and pin locations except for a 0.025 mm tailward shift of the SMT row.
That shift is within the drawing's +/-0.05 mm land-pattern tolerance and
raises locating-hole-to-copper clearance above our 0.20 mm floor. The front
shell courtyard allowance is 0.10 mm to accommodate the existing mounting
drills. This does not declare clearance for screw heads. Common power/ground
lands have explicit aliases in the source netlist; both SBU lands are NC.

The selected part is [C2988369](https://jlcpcb.com/partdetail/C2988369).
Availability is not reserved. Check its orientation and shell-tab soldering
in the factory assembly preview before ordering.
