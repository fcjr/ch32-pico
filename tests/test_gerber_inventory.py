# SPDX-License-Identifier: MIT
"""A six-to-four-layer rebuild must not ship old inner-layer files."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from hardware.panel import validate_gerber_inventory


class GerberInventory(TestCase):
    def test_stale_layers_and_missing_current_layers_are_rejected(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            files=[{'Path':name,'FileFunction':f'Copper,L{i+1}'}
                   for i,name in enumerate(('front.gtl','inner1.g1','inner2.g2','back.gbl'))]
            (root/'board.gbrjob').write_text(json.dumps({
                'GeneralSpecs':{'LayerNumber':4},'FilesAttributes':files}))
            for f in files:(root/f['Path']).write_text('generated copper')
            (root/'holes.drl').write_text('generated drill')
            self.assertEqual(validate_gerber_inventory(root)['copper_layers'],4)
            stale=root/'old-inner3.g3';stale.write_text('obsolete copper')
            with self.assertRaisesRegex(ValueError,'Unexpected or missing'):
                validate_gerber_inventory(root)
            stale.unlink();(root/'inner2.g2').unlink()
            with self.assertRaisesRegex(ValueError,'Unexpected or missing'):
                validate_gerber_inventory(root)
