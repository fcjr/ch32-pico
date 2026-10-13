# SPDX-License-Identifier: MIT
"""Current-revision first-order power estimates; no assigned prototype current rating."""
import json
from .library import ROOT
from .design import BOARD_REVISION


def report():
    return {
        'revision':BOARD_REVISION,'status':'calculation only; no qualified continuous current rating',
        'topology':'VBUS -> protected load switch -> pin 40; separate fixed 3.3 V buck',
        'input_pd_contract_goal_v':20,'input_pd_contract_goal_a':5,
        'output_continuous_rating_a':None,'3v3_header_bringup_limit_ma':50,
        'vsys_input_range_v':[4.3,5.5],
        'ovlo_v':{'nominal':round(1.2*(1+82000/4700),4),
                  'minimum_1percent_resistors':round(1.183*(1+82000*.99/(4700*1.01)),4),
                  'maximum_1percent_resistors':round(1.223*(1+82000*1.01/(4700*.99)),4),
                  'excludes':'pin leakage and dynamic overshoot; review on bench'},
        'ilm_resistance_ohm':600,'fault_current_threshold_nominal_a':round(3335/600,3),
        'fault_current_is_not_output_rating':True,
        'switch_dissipation_at_5a_w':{'typical_28p3_milliohm':.7075,
                                     'example_hot_45_milliohm':1.125},
        'adc_divider':{'top_ohm':100000,'bottom_ohm':10000,'at_20v':20/11,'at_24v':24/11},
        'shutdown_control':{'pin':37,'net':'3V3_EN','assert':'ground','release':'open',
            'unloaded_pin_voltage_max_v':None, 'external_driver':'dry contact or 35 V-rated open drain',
            'qualified':False, 'mcu_off_state_injection_verified':False},
        'bringup_checks':['Measure released EN voltage and low/release shutdown/restart at all supported inputs',
            'Test shutdown while PD_OUT is loaded and check onboard CC/sense and external GPIO/USB/debug back-power against WCH VDD+0.3 V limits','Validate copper, plated holes, contact and switch temperatures at load',
            'Measure board input current and subtract it from the negotiated output budget',
            'Check 5/9/12/15/20 V attach, detach, hard reset and renegotiation with output disabled',
            'Measure input inrush, 3.3 V ripple, short-circuit response and output discharge',
            'Verify no PD VBUS backfeed into VSYS or USB from PD_OUT',
            'Check OVLO tolerances/transients against 23 V switch operating limit',
            'Qualify ILM current sensing on supported X035 silicon lots'],
    }

def main():
    p=ROOT/'build/power-review.json';p.write_text(json.dumps(report(),indent=2)+'\n')
    print(f'Wrote {p}; continuous output rating remains unassigned')
if __name__=='__main__':main()
