# Rev C silkscreen review

The silkscreen matches the CH32X035 Rev C circuit. All 40 header labels are
on the back, beside their corresponding physical header row. GPIO labels use
the X035 names, not the old V003 names or Pico GPIO numbers. Corner numbers
1, 20, 21 and 40 establish orientation. The back artwork is mirrored in PCB
coordinates so it reads normally when the board is turned over.

Pin 30 reads `RST`, pins 35 and 37 read `NC`, and pin 40 reads `PDOUT`.
The front also carries `PDOUT 5-20V`, `REV C`, `ch32-pico` and the Left Shift
Logical logo. The voltage legend matters: pin 40 is no longer a fixed 5 V pin.

Recovery pads and controls are on the front, with their labels on the same
side. The test-pad labels are below their respective pads.

| Label | Part | Connection / location |
|---|---|---|
| SDIO | TP1 | PC18, U1 pin 34; left of the bottom three-pad group |
| SDCK | TP2 | PC19, U1 pin 37; middle of the bottom group |
| 3V3 | TP3 | Fixed 3.3 V; right of the bottom group |
| GND | TP4 | Ground pad near the lower-right corner |
| RST | TP5 | PA21, U1 pin 7; near the lower-left corner |
| RESET | SW1 | Left button; shorts PA21 to ground |
| BOOT | SW2 | Right button; pulls USB D+ high through 4.7 kΩ for factory ISP entry |
| LED | D3 | PB3 application LED through R11 |

The old `PROBE`, `PROBE SWIO` and programmer/target markings are absent.
There is one MCU and no onboard programmer. SDIO/SDCK use the X035 two-wire
debug interface, not the V003 single-wire SWIO protocol.

`hardware/markings.py` checks each header label against the through-hole and
castellated pad nets, and follows each named GPIO to its actual U1 package
pad. It checks all eight service labels for their net, board side, distance
and orientation. Test-pad labels must be closest to their intended pad.
The eight expansion pads have matching back-side legends.
All text is at least 0.8 mm high with at least 0.1 mm strokes.

The fault tests reject swapped service labels, a label on the wrong side,
incorrect GPIO names or MCU connections, missing labels and incorrect back
mirroring. KiCad DRC checks silk-to-mask, hole and text clearance. Panel checks
compare every copy's text and logo with the reviewed single board.

The populated front/back CAD render was inspected for label association,
readability and component-body obstruction. The labels moved with the Rev C
components and the four mounting holes were removed. Eight additional back
labels identify TP6–TP13, the expansion pads. Printed legibility and physical
component fit still need a prototype check. The full audit is under `checks.silkscreen` in
[validation.json](../hardware/review/validation.json).

![Rev C front and back silkscreen](images/ch32-pico.png)
