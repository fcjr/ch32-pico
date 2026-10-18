# PD sink policy

`policy.c` is MIT-licensed, platform-independent code. It is not a flashable
application. Run `python3 -m unittest discover -s tests -p test_pd_policy.py`
to compile and execute its contract-change tests with sanitizers.

The board's native USB bootloader can load the eventual application through
open-source host tools such as wchisp. USB CDC, ADC sampling, watchdog setup
and the native PD transport are not integrated yet.

## What the hardware does

Header pin 40 is USB VBUS with no switch, current limit or reverse blocking,
as on the Pico. It carries 5 V from the moment a source attaches, and the
voltage this policy negotiates afterwards. The MCU cannot turn it off. PB0
(VSNS) reads VBUS / 11 through R1/R2 so firmware can confirm the contract.

## Transport review

The candidate is ch32fun's MIT `examples_x035/usbpd_sink/usbpd.h`, pinned to
`1e4887e11d4bfa739ed5604524b69f5be9f9275b`. Review found these integration gaps:

- The reset interrupt clears `IF_RX_RESET` without invalidating the current
  contract. After a hard reset the source returns to 5 V; the policy must be
  invalidated so the application stops assuming a higher voltage.
- Cable detection runs in the idle state; the application must also detect
  detach after a contract is established.
- `USBPD_SelectPDO` requests the source PDO's maximum current. It needs an
  explicit current argument bounded by the qualified board/connection rating.
- The parser accepts PS_RDY by message type. Contract completion must also
  check the request state and generation, and require the matching ACCEPT.
- ADC conversion must use the actual supply/reference and divider tolerances.

## Required application behavior

Call `pd_init` with the highest voltage the attached carrier tolerates on
pin 40. The policy never requests above it, so a 5 V-only carrier passes
5000 and is never exposed to a higher contract. Choosing that value is the
application's responsibility; the hardware cannot protect a carrier from a
voltage the firmware asks for.

Call `pd_select` with the source's received fixed PDOs, the wanted voltage,
the qualified board limit and the board reserve. Send one RDO when
`pd_can_request` returns true. Call `pd_accepted` on the matching ACCEPT, then
`pd_ready` on PS_RDY for that request with valid measured VBUS. PS_RDY before
ACCEPT is rejected. `pd_expected_mv` then reports the contract voltage; until
then, and after any invalidation, it reports the 5 V default.

Run `pd_monitor` continuously with the attach state and measured VBUS. Detach
or a VBUS reading outside the contract drops the policy to OFF; the
application must then assume pin 40 is at whatever the source supplies.
Reset, detach, protocol error or timeout must call `pd_invalidate`
immediately, before any USB console output. Do not automatically renegotiate
after a reset or reconnection.

The policy rejects board limits above 3 A and reserves at least 100 mA for the
board. A 3 A contract therefore permits at most 2.9 A at pin 40 with that
reserve. Use a larger measured reserve for additional 3.3 V header loads. The
caller must supply the qualified assembly/contact limit; no continuous rating
is assigned yet. There is no on-board current limit: the USB source's own
protection is the only short-circuit limit.

A hung MCU leaves the negotiated voltage on pin 40 until the source resets or
the cable is removed. Configure the hardware watchdog so a stalled application
resets and, through the PD hard reset that follows, returns the source to 5 V.

Measure VBUS and wait for it to settle before enabling an external motor
driver. Use only 5 V for the example 24BYJ48 motor, with a suitable external
driver and local flyback paths. An absent 12 V PDO is an error, never
substitute a voltage.

Bench validation must include both cable orientations, 3 A and 5 A cables,
missing voltage steps, charger-only sources, USB data hosts, hard/soft reset,
detach while loaded, stalled firmware, voltage changes, short circuits and
thermal operation. No continuous output-current rating has been released.
