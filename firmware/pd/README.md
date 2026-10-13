# Rev B PD firmware

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
  ILM current-monitor gain is 165–200 µA/A; a nominal-gain conversion alone
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

The output budget is the negotiated input current less a conservative reserve
for the MCU and fixed 3.3 V output. Rev E uses R17 = 4.7 kΩ in parallel with
R18 = 1.5 kΩ, giving 1,137 Ω and a nominal 2.93 A eFuse threshold. Use this
resistance for ILM current conversion. The application must pass a qualified
board/connection limit below the minimum eFuse threshold, including tolerance,
and never use the old 5 A goal. The current design target is at most 3 A;
continuous operation remains unqualified. Lower source capability must reduce
the budget further. An absent 12 V
PDO is an error. Do not silently substitute another voltage.

Bench validation must include both cable orientations, 3 A and 5 A cables,
missing voltage steps, charger-only sources, USB data hosts, hard/soft reset,
detach while loaded, stalled firmware, voltage changes, short circuits and
thermal operation. No continuous output-current rating has been released.
