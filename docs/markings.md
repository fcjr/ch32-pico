# Silkscreen review

The silkscreen matches the CH32X035 circuit. All 40 header labels are
on the back, beside their corresponding physical header row. GPIO labels use
the X035 names, not Pico GPIO numbers. Corner numbers
1, 20, 21 and 40 establish orientation. The back artwork is mirrored in PCB
coordinates so it reads normally when the board is turned over.

Pin 30 reads `RST`, pin 35 reads `PC7*`, pin 37 reads `EN`, and pin 40 reads `VBUS`.
The asterisk identifies the optional connection through the normally open
`SJ1` jumper, labeled on the front beside it. TP7 reads `PB4`, a free GPIO.
Labels `PA3`, `VBUS`, `GND`, `VSNS`, `PB1`, `CC1`, `CC2`, `PB2` and `PB3`
identify the nine underside contacts; PA3, PB1 and PB2 are free GPIOs. `D+` and `D-` identify
the two inline USB probe contacts on the front. Their pad-to-net assignments
and exact label positions are checked from `hardware/diagnostics.py`. A short
leader identifies the raw VBUS contact around the USB locating hole.
The back also carries `VBUS 5-20V`, `REV A`, `ch32-pico` and the Left Shift
Logical logo. The voltage legend matters: pin 40 follows any higher PD contract.

Recovery pads and controls are on the front, with their labels on the same
side. The five original front service-pad labels sit below their respective pads.

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
| SJ1 | SJ1 | Normally open solder jumper; bridge to connect header 35 to PC7 |

There is one MCU and no onboard programmer. SDIO/SDCK use the X035 two-wire
debug interface.

`hardware/markings.py` checks each header label against the through-hole and
castellated pad nets, and follows each named GPIO to its actual U1 package
pad. It checks all eight service labels for their net, board side, distance
and orientation. The five front service-pad labels must be closest to their intended pad;
diagnostic legends must match their separately specified coordinates.
The eight expansion pads have matching back-side legends. The audit follows
PB4 through TP7 to U1 pin 24, and pin 40 to the USB VBUS contact. It checks SJ1
for distinct GPIO35/PC7 nets, back-side access, its label and no paste.
All text is at least 1.0 mm high with at least 0.15 mm strokes.

The fault tests reject swapped service labels, a label on the wrong side,
incorrect GPIO names or MCU connections, missing labels and incorrect back
mirroring. KiCad DRC checks silk-to-mask, hole and text clearance. Panel checks
compare every copy's text and logo with the reviewed single board.

The populated front/back CAD render was inspected for label association,
readability and component-body obstruction. There are no mounting holes. Eight back labels identify TP6–TP13,
and eleven additional diagnostic labels identify TP14–TP24. Printed legibility and physical
component fit still need a prototype check. The full audit is under `checks.silkscreen` in
[validation.json](../hardware/review/validation.json).

![Front and back silkscreen](images/ch32-pico.png)
