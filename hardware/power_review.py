# SPDX-License-Identifier: MIT
"""Analytical power screening. Never assigns a measured continuous rating."""
import json
from .circuit import COMPONENTS
from .library import ROOT
from .design import BOARD_REVISION


def passive_value(value):
    token=value.split()[0].removesuffix('F')
    scales={'k':1e3,'M':1e6,'u':1e-6,'n':1e-9,'p':1e-12}
    return float(token[:-1])*scales[token[-1]] if token[-1] in scales else float(token)


def qualification_screen(components=COMPONENTS):
    c={item.ref:item for item in components}
    val=lambda ref:passive_value(c[ref].value)
    ratio=val('R2')/(val('R1')+val('R2'))
    buck_operating_max_v,buck_absolute_max_v,tvs_hot_clamp_v=32,34,28.35
    modes=[]
    for voltage in (5,9,12,15,20):
        upper=voltage*1.05
        modes.append({'nominal_v':voltage,'engineering_upper_check_v':upper,
            'pin40_v':voltage,'continuous_rating_a':None,'qualification':'not tested',
            'sense_adc_v':round(upper*ratio,4),
            'sense_divider_power_mw':round(upper**2/(val('R1')+val('R2'))*1000,3),
            'carrier_must_tolerate_v':upper,
            'default_on_attach':voltage==5})
    return {'status':'prototype design; no qualified current rating',
        'supported_fixed_voltage_modes_v':[5,9,12,15,20],
        'unsupported':'EPR 28/36/48 V and PPS/AVS; 12 V only if offered in a fixed source PDO',
        'physical_measurements_available':False,
        'pin40':{'net':'VBUS','switched':False,'default_v':5,
            'current_limit':'USB source only; no on-board fuse, eFuse or reverse blocking',
            'note':'Matches the Pico: pin 40 is the USB VBUS rail. It rises only when firmware requests a higher PD contract.'},
        'vbus_sense':{'ratio':round(ratio,6),'at_20v':round(20*ratio,4),
            'at_hot_clamp_v':round(tvs_hot_clamp_v*ratio,4)},
        'mode_checks':modes,
        'transient_screen':{'tvs_standoff_v':22,'specified_hot_clamp_v':tvs_hot_clamp_v,
            'tvs_test_pulse':'35 A, 8/20 us; not a continuous absorption or arbitrary motor-energy rating',
            'buck_operating_max_v':buck_operating_max_v,'buck_absolute_max_v':buck_absolute_max_v,
            'clamp_margin_to_buck_operating_v':round(buck_operating_max_v-tvs_hot_clamp_v,2),
            'hv_capacitors_v':50,
            'purpose':'Hot-plug into a source already at 20 V can ring toward twice the supply; D5 keeps that below the AP63203 limit.'},
        'bench_candidate_a':3,'bench_candidate_status':'staged test target only',
        'required_before_power_qualification':[
            'Scope VBUS at U4 and D5 while hot-plugging into sources already at 20 V, with short and long cables. Confirm the peak stays below 32 V.',
            'Measure connector, copper, plated holes and the actual pin-40/ground contacts at each fixed PDO, ambient and load step. Stop on excessive temperature.',
            'Measure plug-in inrush and PD voltage transitions with representative carrier capacitance; some sources may reset with large bulk capacitance.',
            'Confirm source shutdown on a pin-40 short at each PDO. The board has no current limit of its own.',
            'Firmware must request a higher PDO only when the attached carrier tolerates it; a hung MCU leaves the negotiated voltage on pin 40.',
            'Do not drive pin 40 from an external supply while USB is connected; nothing blocks backfeed into the USB source.',
            'Use external motor/coil drivers with local recirculation/flyback. No unknown inductive load or sustained regeneration is qualified by the TVS pulse rating.',
            'Integrate native PD transport, calibrated ADC and watchdog. Portable policy tests do not establish flashable firmware readiness.',
        ],
        'sources':{'tvs':'https://www.ti.com/lit/ds/symlink/tvs2200.pdf',
            'buck':'https://www.diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf'}}


def report():
    screen=qualification_screen()
    return {'revision':BOARD_REVISION,'status':'calculation only; no qualified continuous current rating',
        'topology':'USB-C VBUS -> pin 40 directly, as on the Pico; TVS2200 input clamp; diode-OR into a separate fixed 3.3 V buck',
        'input_pd_contract_goal_v':20,'input_pd_contract_goal_a':3,
        'output_continuous_rating_a':None,'3v3_header_bringup_limit_ma':50,
        'vsys_input_range_v':[4.3,5.5],'qualification_screen':screen,
        'adc_divider':{'top_ohm':100000,'bottom_ohm':10000,'at_20v':20/11,'at_28p35v':28.35/11},
        'shutdown_control':{'pin':37,'net':'3V3_EN','assert':'ground','release':'open',
            'external_driver':'dry contact or 35 V-rated open drain','qualified':False}}


def main():
    p=ROOT/'build/power-review.json';p.write_text(json.dumps(report(),indent=2)+'\n')
    print(f'Wrote {p}; continuous output rating remains unassigned')
if __name__=='__main__':main()
