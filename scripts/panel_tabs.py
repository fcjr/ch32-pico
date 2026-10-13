# SPDX-License-Identifier: MIT
"""KiKit tabs on the short ends, leaving the USB overhang unobstructed."""
from kikit.annotations import TabAnnotation
from kikit.plugin import TabsPlugin
from kikit.units import mm


class EdgeTabs(TabsPlugin):
    def buildTabAnnotations(self, panel):
        for substrate in panel.substrates:
            left, top, right, bottom = substrate.bounds()
            # A 5 mm tab starts at the left corner. Its right milling fillet
            # must clear the USB shell; panel_fit checks the final geometry.
            substrate.annotations.append(TabAnnotation(
                None, (left + 2.5 * mm, top), (0, 1), 5 * mm))
            substrate.annotations.append(TabAnnotation(
                None, ((left + right) / 2, bottom), (0, -1), 5 * mm))
