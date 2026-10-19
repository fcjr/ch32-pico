# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Verify JLC model-frame CPL conversions for the fitted polarized parts."""
import unittest
from hardware.jlc_model_frames import cpl_adjustment


class JlcModelFrameTests(unittest.TestCase):
    def test_lqfp48_rotation_delta(self):
        self.assertEqual(cpl_adjustment('C29779902', 90), (0.0, 0.0, 0.0))

    def test_usblc6_rotation_delta(self):
        self.assertEqual(cpl_adjustment('C7519', 90), (0.0, 0.0, 0.0))

    def test_usb_connector_anchor_shift(self):
        rotation, dx, dy = cpl_adjustment('C963411', 180)
        self.assertEqual(rotation, 180.0)
        self.assertAlmostEqual(dx, 0.0)
        self.assertAlmostEqual(dy, -1.345)

    def test_frame_clone_footprints_keep_kicad_angles(self):
        # U4 (C2927130) copies JLC's SOT-23-6 frame: no delta, only normalization.
        self.assertEqual(cpl_adjustment('C2927130', -90), (270.0, 0.0, 0.0))

    def test_unknown_part_is_identity_with_normalized_rotation(self):
        self.assertEqual(cpl_adjustment('C2286', -90), (270.0, 0.0, 0.0))


if __name__ == '__main__':
    unittest.main()
