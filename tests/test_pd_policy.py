# SPDX-License-Identifier: MIT
import subprocess
import tempfile
import unittest
from pathlib import Path

class PDPolicyTests(unittest.TestCase):
    def test_faults_and_contract_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'policy-test'
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                '-Ifirmware/pd','firmware/pd/policy.c','tests/pd_policy_test.c','-o',str(out)],check=True)
            subprocess.run([str(out)],check=True)
