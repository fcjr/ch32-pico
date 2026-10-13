# SPDX-License-Identifier: MIT
"""KiKit tabs on the short ends, leaving the USB overhang unobstructed."""
from kikit.annotations import TabAnnotation
from kikit.plugin import TabsPlugin
from kikit.units import mm


class EdgeTabs(TabsPlugin):
    def buildTabAnnotations(self, panel):
        for substrate in panel.substrates:
            left, top, right, bottom = substrate.bounds()
            # The tab ends at X=4.75 mm. Reserve room for the 1 mm
            # milling fillet before the connector starts at X=6.03 mm.
            substrate.annotations.append(TabAnnotation(
                None, (left + 3.5 * mm, top), (0, 1), 2.5 * mm))
            substrate.annotations.append(TabAnnotation(
                None, ((left + right) / 2, bottom), (0, -1), 3 * mm))
