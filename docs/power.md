> **Rev A reference.** The [current Rev C design](revision-c.md) supersedes the circuit, pinout, costs and manufacturing status below.

# Power review

USB VBUS feeds VSYS through D1, with its cathode at VSYS. Header pin 39 is
VSYS and pin 40 is VBUS. U4 supplies the programmer and header pin 36 at
3.3 V. U5 supplies the target on TARGET_3V3. Both regulators are
ME6211C33M5G-N, C82942, with local 1 uF input/output capacitors.

The provisional supply range is USB 5 V or external VSYS 4.3–5.5 V.
This does not reproduce Pico low-voltage battery operation. Do not power the
board through 3V3_OUT: it does not feed U5's input, and LDO reverse-current
behavior is not qualified. External GPIOs can back-power an unpowered target.

Pulling header pin 37 low disables U4. A 100k pull-down on U5 enable then
holds the target off when the programmer is blank or unpowered. The probe
firmware enables U5 at startup for standalone operation and can cycle it
during programming. PC1/PC2 release SWIO before power-off. R12 discharges
the target rail through 1k, consuming 3.3 mA when powered. The nominal 2.1 uF
rail gives a 2.1 ms RC time constant. Firmware waits 20 ms while off and 2 ms
after re-enabling. Measure the actual rail waveform during bring-up.

`make power-review` writes first-order LDO heat estimates. At 5.5 V input,
50 mA output dissipates about 110 mW in one regulator's pass element;
100 mA dissipates 220 mW. These exclude ground current and thermal derating.
The regulator's headline current specification is not a safe board rating.

The USB descriptor declares 100 mA for the complete board. A 50 mA external
header load is a test goal, not an assigned rating. Measure programmer and
target consumption before choosing the usable header budget. USB startup,
configuration, suspend and hot-plug current remain qualification items.

Begin with a current-limited 5 V supply and no external GPIO/header loads.
Check both 3.3 V rails, enable behavior, USB/VSYS backfeed and regulator
heating. Then test programmer flash/readback, target power cycling and
standalone operation. Sweep input/load only after these checks pass.
Record voltage at regulator pins, ripple, current and component temperature.
