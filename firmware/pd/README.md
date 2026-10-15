# Rev E PD firmware

`policy.c` is MIT-licensed, platform-independent code. It is not a flashable
application. Run `python3 -m unittest discover -s tests -p test_pd_policy.py`
to compile and execute its contract-change and fault tests with sanitizers.

The board's native USB bootloader can load the eventual application through
open-source host tools such as wchisp. USB CDC, ADC sampling, watchdog setup
and the native PD transport are not integrated yet. Do not use the upstream
PD example unchanged to control this board's load switch.

## Transport review

The candidate is ch32fun's MIT `examples_x035/usbpd_sink/usbpd.h`, pinned to
`1e4887e11d4bfa739ed5604524b69f5be9f9275b`. Review found these integration gaps:

- The reset interrupt clears `IF_RX_RESET` without invalidating the current
  contract or switching off an external load.
- Cable detection runs in the idle state; the application must also detect
  detach after a contract is established.
- `USBPD_SelectPDO` requests the source PDO's maximum current. It needs an
  explicit current argument bounded by the qualified board/connection rating.
- The parser accepts PS_RDY by message type. Contract completion must also
  check the request state and generation, and require the matching ACCEPT.
- ADC conversion must use the actual supply/reference and divider tolerances.
  MX26631 IMON gain is 19–26 µA/A at 0.6–2 A and
  23–29 µA/A at 2–5 A; a nominal-gain conversion alone
  can underestimate load current. Include gain, resistance and ADC error in
  the trip budget.

## Required application behavior

Drive PB2/PD_ENABLE low before initializing USB or PD. Configure the hardware
watchdog and keep the external 10 kΩ pulldown fitted. A normal USB ISP session
must leave the output off.

Disable the physical gate before calling `pd_select`. Wait until the PD_OUT
ADC reports discharge before sending the new request. Apply the selected
PDO position and contract current to the RDO. Call `pd_accepted` on the
matching ACCEPT, then `pd_ready` on PS_RDY for that request with valid measured
VBUS. PS_RDY before ACCEPT is rejected by the policy. A
separate explicit arm command may then call `pd_arm`.

Apply `policy.gate` to PB2 on every policy transition. Reset, detach, fault,
protocol error or timeout must drive PB2 low immediately and invalidate the
request generation. Polling must not delay that action behind USB console
output. Do not automatically re-arm after a reset or reconnection.

The policy rejects board limits above 3 A and reserves at least 100 mA for the
board. A 3 A contract therefore permits at most 2.9 A at pin 40 with that reserve.
Use a larger measured reserve for additional 3.3 V header loads. The caller must
supply the qualified assembly/contact limit; no continuous rating is assigned yet.

Rev E uses MX26631DL with R17 = 11 kΩ, formula-derived nominal fault threshold
3.636 A. Its table and formula disagree at 24 kΩ; the ±15% engineering
screen at 11 kΩ is not a guaranteed bound. Qualify the purchased lot over temperature.
R25 = 10 kΩ converts the separate IMON output to nominal 0.260 V/A above 2 A. R17 must
never be used for ADC current conversion. Include minimum monitor gain,
resistor tolerance/drift, ADC/reference error and filter delay. Calibration below
0.6 A is required. The fault threshold is deliberately above the 3 A target;
it does not authorize that current from a weaker PD source.

A separate TPS3701 UV interlock needs about 4.76 V nominal at VBUS to start.
MX26631 automatically retries after faults. The application must latch PB2 low
on FAULT, independently of USB traffic, and require an explicit re-arm. Validate
repeated-retry heating if the MCU stalls before its watchdog resets it. This
circuit has no hardware latch-off guarantee.

Weak 5 V supplies or cable losses may keep the output off or cause dropout.
Measure PD_OUT and wait for it to stabilize before enabling an external motor
driver. The portable policy has no driver-enable or output-ramp feedback hooks;
implement those in the board application. Use only 5 V for the example 24BYJ48
motor, with a suitable external driver and local flyback paths. No automatic
re-arm after faults. An absent 12 V PDO is an error, never substitute a voltage.

Bench validation must include both cable orientations, 3 A and 5 A cables,
missing voltage steps, charger-only sources, USB data hosts, hard/soft reset,
detach while loaded, stalled firmware, voltage changes, short circuits and
thermal operation. No continuous output-current rating has been released.
