> **Rev A reference.** This document describes the former CH32V003 board.
> See [Revision C](revision-c.md) for the current X035/PD design.

# USB routing review

The programmer uses rv003usb low-speed USB HID, at 1.5 Mbit/s. D+ terminates
at programmer PD4 through 47 ohms; D- terminates at PD3 through 47 ohms.
A 1.5k D- pull-up is driven by PD5. The connector has independent 5.1k CC
pull-downs for both orientations. The target has no native USB connection.

ST USBLC6-2P6, C15999, provides ESD protection close to the connector.
Its SOT-666 land pattern is generated from ST DS4260 Rev 7, Figure 21.
Both orientations' USB contacts join locally, then flow through the ESD lands.
The two traces separate toward the TSSOP programmer's opposite-side pins.
The route is not a uniformly coupled or length-matched transmission line.

The explicit traces remain on F.Cu without signal vias, over the In1.Cu
GND reference. The 0.1537 mm trace width comes from the JLC stackup
calculation; that calculation does not establish impedance for these fanouts.
The four-layer stackup remains JLC04101H-3313.

`just usb-review` measures actual copper centerline paths and samples filled
reference copper at trace centers and edges at no more than 0.05 mm intervals.
The selected route has GND under all 1,716 samples. Native via keepouts
protect the reference below the USB traces. Router output
fails review if any sample lacks ground, any USB signal changes layer, or any
protected source segment is lost. Sampling does not prove continuous return
width or USB compliance, and the reported lengths omit pad/package spreading.

Test cable insertion, both connector orientations, enumeration, program/verify,
suspend, detach and recovery on assembled boards. The G-Switch drawing gives
only reference cable-housing clearance. See [mechanical fit](mechanical.md).
Sources: [ST USBLC6-2 datasheet](https://www.st.com/resource/en/datasheet/usblc6-2.pdf),
[rv003usb](https://github.com/cnlohr/rv003usb), and
[JLC calculator](https://jlcpcb.com/pcb-impedance-calculator).
