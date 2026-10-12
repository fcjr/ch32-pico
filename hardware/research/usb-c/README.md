# USB-C fit candidate

`USB_C_Receptacle_G-Switch_GT-USB-7010ASV.kicad_mod` is an unmodified
KiCad 10.0.6 library footprint, copied from `Connector_USB.pretty`.
Upstream: [KiCad footprints](https://gitlab.com/kicad/libraries/kicad-footprints).
License: [CC BY-SA 4.0 with the KiCad library exception](https://www.kicad.org/libraries/license/).

The candidate is G-Switch GT-USB-7010ASV, LCSC C2988369. The current
[manufacturer drawing, revision A0, 2023-02-04](https://datasheet.lcsc.com/datasheet/pdf/a1d5a66cf718dd88763ab794dba802b2.pdf?productCode=C2988369)
has SHA256 `fdb258c83ca4e678d2c834a233abecef2aa72dee45b36e3361fd7e8abb8fe54c`.
Its 1.85 mm after-mating clearance is a **reference dimension**, not a
guaranteed minimum. Its recommended PCB thickness is 0.80 mm; qualify
stake soldering and underside clearance on our 1.00 mm board.

`scripts/usb_candidate_fit.py` derives an isolated fit coupon from this file.
It merges the four duplicated common-contact lands, shifts the SMT row
25 um tailward within the drawing's 50 um land-pattern tolerance, and uses
a courtyard following the shell and stake lands with 0.10 mm allowance.
Drill sizes, mounting-hole coordinates and the Pico outline are unchanged.
The narrower courtyard does not establish screw-head clearance.

The unmodified footprint is retained as a provenance input. The derived
footprint is now selected in the main circuit. See
[the mechanical review](../../../docs/mechanical.md) for results and limits.
