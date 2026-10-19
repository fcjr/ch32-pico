# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Convert KiCad placement angles to JLC model-frame CPL values.

Verified against JLC's own component-library footprints on 2026-10-13.
Our U4, D1, D4, D3, D5, switch, inductor and passive footprints copy JLC's
frames, so their KiCad angles translate directly. The entries below correct
footprints drawn in KiCad's standard conventions or anchored differently:

- C29779902 (U1, LQFP-48): KiCad's footprint has pin 1 top-left; JLC's
  LQFP-48_L7.0-W7.0-P0.50-LS9.0-BL frame has pin 1 bottom-left, a -90 deg
  delta.
- C7519 (D2, SOT-23-6): the same top-left versus bottom-left delta against
  SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BL.
- C963411 (J2, USB-C): JLC's model origin sits 1.345 mm closer to the
  signal-pad row than our body-center anchor (their pads at local
  -2.37 mm, ours at -3.715 mm), along the footprint's local Y axis.

Rotations are emitted in [0, 360) so parsers never see a negative angle.
These values convert coordinates; JLC's online placement preview must still
confirm U1, D2, J2 and U4 before any order release.
"""
import math

# LCSC part code -> (rotation delta in degrees, anchor offset in footprint-local mm)
FRAME_DELTAS = {
    'C29779902': (-90.0, (0.0, 0.0)),
    'C7519': (-90.0, (0.0, 0.0)),
    'C963411': (0.0, (0.0, -1.345)),
}


def cpl_adjustment(part, angle_deg):
    """Return (rotation, dx, dy) for a CPL row of `part` at a KiCad angle.

    dx/dy translate the placement from our footprint origin to the JLC model
    origin in CPL coordinates (X right, Y up).
    """
    delta, (ax, ay) = FRAME_DELTAS.get(part, (0.0, (0.0, 0.0)))
    rotation = (angle_deg + delta) % 360
    theta = math.radians(angle_deg)
    # JLC model origin in board coordinates (X right, Y down), then negate Y
    # for the CPL frame.
    board_dx = ax * math.cos(theta) + ay * math.sin(theta)
    board_dy = -ax * math.sin(theta) + ay * math.cos(theta)
    return rotation, board_dx, -board_dy
