# Power qualification

The target is 3 A on a board with top-side assembly. No continuous-current
rating has been assigned. There are no assembled test boards yet. Simulation,
ERC and PCB DRC cannot close the measurements below.
Use 0-50 C ambient, unenclosed and in still air, as the initial development
target. This is a test envelope, not a released operating specification.

Pin 40 is USB VBUS with no switch, current limit or reverse blocking, as on
the Pico. The USB source's own protection is the only short-circuit limit.

Use a current-limited bench supply, a PD source/analyzer, electronic load,
oscilloscope with suitable differential probes, thermocouples and the actual
carrier contacts and cables. Record PCB revision/hash, BOM lots, ambient,
airflow, source/cable, connector/contact type and instrument settings with every run.
Do not start with a motor or an unknown load.

## Bring-up sequence

1. Inspect polarity, solder bridges and hidden joints on D5 and U4.
   Check resistance between each supply and ground before applying power.
2. Start at 5 V with a 100 mA bench limit and nothing on pin 40. Verify 3.3 V,
   VSNS and no unexpected voltage at VSYS. Characterize control-supply
   consumption before increasing the limit.
3. Exercise USB attach in both orientations, USB ISP and SDI recovery.
   Retain reset/debug option bytes. Confirm the board stays at 5 V through
   boot, download, reset, watchdog timeout and detach.
4. Hot-plug into sources already at 20 V, with short and long cables. Scope
   VBUS at D5 and U4. The peak must stay below U4's 32 V operating limit.
   Repeat with representative carrier capacitance on pin 40.
5. Request only advertised fixed 5/9/12/15/20 V PDOs. Verify ACCEPT/PS_RDY
   ordering and VSNS ADC accuracy. Reject unsupported voltages, absent 12 V,
   PPS, AVS and EPR. Never apply more than 5 V to the example 5 V motor.
6. Start into a small resistive load, then capacitive loads. Capture VBUS and
   current at attach and during each PD voltage change. Establish which sources
   reset with large carrier capacitance and document a capacitance limit.

## Continuous-load matrix

For each supported fixed PDO, step through 0.25, 0.5, 1, 1.5, 2, 2.5 A and
the intended final budget. A 3 A input contract with the minimum 100 mA reserve
allows only 2.9 A at pin 40. To test a full 3 A output target independently,
use a bench supply and include control-supply current in its setting.

At each step, wait for temperatures to stabilize, log voltage drops and input
and output power at 25 C, then repeat at 50 C in still air. Check startup at
0 C as well. An enclosure or a wider ambient range needs a new test envelope.
Measure USB contacts, the four VBUS vias, the 0.9 mm bar, the 1.2 mm pin 40
trunk, pin-40 contacts and ground returns.
A generic 2.54 mm header is not automatically qualified for this current.
Specify and test the actual contact pair and carrier. Record the operating
ambient with the assigned rating. Conservative initial stop criteria are a
30 C contact rise, 80 C accessible contact temperature, unstable output or
heating that has not plateaued. These are development stop criteria, not
certification limits.

Repeat 5 V with low source voltage and worst intended cable resistance. Record
pin 40 voltage at load; the board does not promise 3 A from every 5 V
source/cable combination.

## Faults and inductive loads

After resistive tests pass, test abrupt load removal, a hard short on pin 40
at each PDO, cable disconnect, source collapse, reset, watchdog and 3.3 V
shutdown. Confirm each source shuts down on a short before copper or contacts
overheat; record which sources do not. A hung MCU leaves the negotiated
voltage on pin 40, so firmware must request a higher PDO only when the carrier
tolerates it. Never power pin 40 externally while USB is connected.
Check input inrush and the capacitance seen at USB attach separately. The 10 uF
buck input capacitor and any carrier capacitance on pin 40 exceed a simple
10 uF nominal attach-capacitance budget. Measure compliance; do not claim USB
attach/inrush compliance from this schematic.

TVS2200's 35 A 8/20 us test waveform is not a motor-energy rating. Use a known
external driver with local recirculation/flyback for each motor/relay/coil. Keep
the driver off throughout startup and voltage changes. Establish stall current,
inductance/energy, repetitive switching rate, cable inductance and any regenerative
braking requirement. Test worst-case stop/reversal only after defining those bounds.
The example AliExpress 24BYJ48 listing says 5 V and 20 ohm windings, implying
about 0.25 A per winding before driver losses, but its actual variant and winding
resistance must be checked. Pin 40 supplies a driver; it is not a motor GPIO.

Release a current/ambient/load rating only after this evidence passes review.
Record failures and reduce the rating or revise the hardware before ordering
production quantities. Factory preview, exact MCU availability and a usable
board firmware image are separate release requirements.
