# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""First-order LDO dissipation estimates; prototype limits remain unqualified."""
import json
from .library import ROOT


def report():
    examples=[]
    for voltage in (4.3,5.0,5.5):
        for current in (10,20,50,100):
            examples.append({'vsys_v':voltage,'single_ldo_output_ma':current,
                'pass_element_dissipation_mw':round((voltage-3.3)*current,1)})
    return {'status':'calculation only; no validated board current rating',
        'regulator':'ME6211C33M5G-N','topology':'separate main and target 3.3 V LDOs',
        'provisional_vsys_range_v':[4.3,5.5], 'load_examples':examples,
        'target_discharge_resistor_ohm':1000,'target_discharge_current_ma':3.3,
        'target_discharge_time_constant_us_with_2p1uF':2100,
        'usb_descriptor_max_ma':100,'external_header_current_test_goal_ma':50,
        'external_header_current_budget_ma':None,
        'exclusions':['LDO ground current, transient current and thermal derating',
            'Dropout variation, input-diode drop and copper voltage drops',
            'Target/probe firmware current and USB suspend requirements'],
        'bringup_checks':['Measure both rails and regulator temperature at 5.5 V VSYS',
            'Measure total USB current before assigning external header capacity',
            'Verify target rail falls below reset threshold during 20 ms power cycle',
            'Check USB/VSYS backfeed; do not power the board through pin 36',
            'Confirm assembled 1 uF capacitor effective capacitance and stability']}


def main():
    path=ROOT/'build/power-review.json'
    path.write_text(json.dumps(report(),indent=2)+'\n')
    print(f'Wrote {path}; current rating remains unassigned')


if __name__=='__main__':main()
