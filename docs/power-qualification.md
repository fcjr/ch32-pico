# Rev E power qualification

The target is 3 A on a board with top-side assembly. No continuous-current
rating has been assigned. There are no assembled test boards yet. Simulation,
ERC and PCB DRC cannot close the measurements below.
Use 0-50 C ambient, unenclosed and in still air, as the initial development
target. This is a test envelope, not a released operating specification.

Use a current-limited bench supply, a PD source/analyzer, electronic load,
oscilloscope with suitable differential probes, thermocouples and the actual
carrier contacts and cables. Record PCB revision/hash, BOM lots, ambient,
airflow, source/cable, connector/contact type and instrument settings with every run.
Do not start with a motor or an unknown load.

## Bring-up sequence

1. Inspect polarity, solder bridges and hidden joints on U3, Q1, D5 and D6.
   Check resistance between each supply and ground before applying power.
2. Start at 5 V with a 100 mA bench limit and pin 40 disabled. Verify 3.3 V,
   PD_ENABLE low, SHDN low, and no unexpected voltage at VSYS or PD_OUT.
   Characterize control-supply consumption before increasing the limit.
3. Exercise USB attach in both orientations, USB ISP and SDI recovery.
   Retain reset/debug option bytes. Firmware must leave the output disabled
   during boot, download, reset, watchdog timeout, detach and renegotiation.
4. Test the UV interlock independently of firmware. Sweep input slowly in both
   directions and capture a fast collapse. The calculation screens startup at
   4.665-4.883 V and falling thresholds at 4.630-4.765 V at VBUS. These are
   static corners, not measured propagation/overshoot limits. Repeat at temperature.
5. Request only advertised fixed 5/9/12/15/20 V PDOs. With the output disabled,
   verify ACCEPT/PS_RDY ordering and ADC voltage accuracy. Reject unsupported
   voltages, absent 12 V, PPS, AVS and EPR. Never apply more than 5 V to the
   example 5 V motor.
6. Start into a small resistive load, then test disabled-driver capacitive loads.
   Capture VBUS, PD_INPUT, PD_OUT, SHDN, FLT, current, and Q1 gate/charge-pump
   voltage relative to VBUS. Determine charge-pump settling time at cold attach
   before allowing the application to arm a load. Nominal 20 V rise is
   8.73 ms. Establish an actual external-capacitance and startup-load limit.
7. Calibrate VBUS/PDOUT ADC dividers and IMON. IMON is nominal 0.260 V/A above 2 A,
   with gain, R25, ADC/reference and filter errors. Use conservative bounds
   for protection. Do not infer current from R17.

## Continuous-load matrix

For each supported fixed PDO, step through 0.25, 0.5, 1, 1.5, 2, 2.5 A and
the intended final budget. A 3 A input contract with the minimum 100 mA reserve
allows only 2.9 A at pin 40. To test a full 3 A output target independently,
use a bench supply and include control-supply current in its setting.

At each step, wait for temperatures to stabilize, log voltage drops and input
and output power at 25 C, then repeat at 50 C in still air. Check startup and
fault recovery at 0 C as well. An enclosure or a wider ambient range needs a
new test envelope.
Measure U3, Q1, USB contacts, input/output necks, vias, pin-40 contacts and ground
returns. Also test sustained overload up to the measured upper current-limit
threshold and hardware retry cycling; the engineering screen reaches 4.31 A.
A generic 2.54 mm header is not automatically qualified for that fault envelope.
Specify and test the actual contact pair and carrier, including protection delay. Record the operating ambient with the assigned rating. Conservative
initial stop criteria are a 30 C contact rise, 80 C accessible contact temperature,
estimated junction above 125 C, unstable output, unexpected faults or heating
that has not plateaued. These are development stop criteria, not certification limits.
Junction estimates require a validated measurement method; do not substitute the
JEDEC theta-JA value for this small board.
The exposed-pad ground escapes use adjacent vias rather than drilled holes
under the solder land. Check this thermal bottleneck explicitly. If it misses
the current/ambient target, revise heat spreading or specify filled/capped
thermal vias and obtain a new fabrication quote before assigning a rating.

Repeat 5 V with low source voltage and worst intended cable resistance. Record
the load at which UV shutdown occurs. The board must fail off safely; it is not
promised to deliver 3 A from every 5 V source/cable combination.

## Faults and inductive loads

After resistive tests pass, test hot plug, abrupt load removal, hard short,
source current limiting, cable disconnect, source collapse, reset, watchdog,
3.3 V shutdown and output powered externally. Capture reverse current and all
supply pin extremes. Exercise firmware fault latching and deliberate recovery. MX26631 hardware auto-retries;
measure repeated-retry heating with a stalled MCU and verify watchdog shutdown.
Do not auto-rearm the application.
Check input inrush and the capacitance seen at USB attach separately. The 10 uF
buck input capacitor plus added bypass capacitors exceed a simple 10 uF nominal
attach-capacitance budget. Measure compliance; do not claim USB attach/inrush
compliance from this schematic. If it fails, add controlled charging for the
control rail or revise capacitance with buck stability/ripple validation.

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
