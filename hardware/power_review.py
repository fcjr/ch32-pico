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


def divider_corner(top,bottom,threshold,top_tol,bottom_tol,leakage,high):
    sign=1 if high else -1
    rt=top*(1+sign*top_tol);rb=bottom*(1-sign*bottom_tol)
    return threshold*(1+rt/rb)+sign*leakage*rt


def qualification_screen(components=COMPONENTS):
    c={item.ref:item for item in components}
    val=lambda ref:passive_value(c[ref].value)
    # MX26631 V12 gives 40/R_kohm in this region, but its 24k table
    # and formula disagree. +/-15% is an engineering screen, NOT a guaranteed
    # manufacturer limit at 11k. Lot/temperature qualification remains required.
    nominal=40000/val('R17');r_tol=.01+200e-6*100
    low,high=nominal*.85/(1+r_tol),nominal*1.15/(1-r_tol)
    slew=2.1e-6*24/val('C8')/1000
    precise=.001+25e-6*100
    top,bottom=val('R20'),val('R21')
    ovlo={'nominal':1.23*(1+top/bottom),
          'minimum':divider_corner(top,bottom,1.18,precise,precise,1e-6,False),
          'maximum':divider_corner(top,bottom,1.28,precise,precise,1e-6,True)}
    uv_top=val('R27');uv_bottom=val('R28')
    uv={'sense_net':'VBUS upstream of Q1; avoids shutdown/startup deadlock',
        'rising_nominal':.4055*(1+uv_top/uv_bottom),
        'rising_minimum':divider_corner(uv_top,uv_bottom,.400,precise,precise,25e-9,False),
        'rising_maximum':divider_corner(uv_top,uv_bottom,.413,precise,precise,25e-9,True),
        'falling_minimum':divider_corner(uv_top,uv_bottom,.397,precise,precise,25e-9,False),
        'falling_maximum':divider_corner(uv_top,uv_bottom,.403,precise,precise,25e-9,True),
        'assumptions':'Initial tolerances plus 100 C drift at 25 ppm/C; +/-25 nA sense leakage. Response delay/fast collapse must be measured.'}
    # Q1 gate drive can be only 8 V. Use its guaranteed 4.5 V/25 C RDS
    # with a provisional factor of two for temperature, not its 10 V hot spec.
    q1_hot_screen=.0133*2
    uv['input_at_trip_minimum_at_fault_screen_a']=uv['falling_minimum']-high*q1_hot_screen
    uv['q1_hot_resistance_screen_ohm']=q1_hot_screen
    modes=[]
    for voltage in (5,9,12,15,20):
        rise_s=voltage/slew/1000;capacitance=100e-6+val('C12')
        modes.append({'nominal_v':voltage,'engineering_upper_check_v':voltage*1.05,
            'continuous_rating_a':None,'qualification':'not tested',
            'nominal_rise_time_ms':round(rise_s*1000,3),
            'resistive_startup_example':{'final_load_a':3,'peak_switch_w':voltage*3/4,
                'switch_energy_j':round(voltage*3*rise_s/6,6),
                'assumption':'Ideal linear ramp into R=VIN/3 A. Drivers must remain disabled during ramp; no SOA guarantee.'},
            'provisional_capacitive_startup_example':{'external_capacitance_uf':100,
                'charging_current_a':round(capacitance*slew*1000,4),
                'switch_energy_j':round(.5*capacitance*voltage**2,6),
                'assumption':'Illustrative capacitance, not an approved external load envelope.'},
            'r8_power_at_upper_check_mw':round((voltage*1.05)**2/(val('R8')*.97)*1000,3),
            'nominal_discharge_20v_to_0p8v_s_at_100uf_external':round((1/(1/val('R8')+1/(val('R5')+val('R6'))))*capacitance*__import__('math').log(20/.8),3),
            'low_input_shutdown_possible':voltage==5})
    return {'status':'prototype design; no qualified current rating',
        'supported_fixed_voltage_modes_v':[5,9,12,15,20],
        'unsupported':'EPR 28/36/48 V and PPS/AVS; 12 V only if offered in a fixed source PDO',
        'physical_measurements_available':False,
        'ilm':{'resistance_ohm':val('R17'),'nominal_a':round(nominal,4),
            'screen_min_a':round(low,4),'screen_max_a':round(high,4),
            'resistor_screen_tolerance':r_tol,
            'excludes':'Transient overshoot and interpolation guarantee. Threshold is not a continuous rating.'},
        'ovlo_static_screen_v':{k:round(v,6) for k,v in ovlo.items()},
        'uvlo_static_screen_v':{k:round(v,6) if isinstance(v,float) else v for k,v in uv.items()},
        'dvdt_nominal_v_per_ms':slew,
        'imon':{'nominal_v_per_a':26e-6*val('R25'),
            'gain_ua_per_a_at_0p6_to_2a':[19,26],
            'gain_ua_per_a_at_2_to_5a':[23,29],
            'note':'Use minimum gain, minimum R25 and ADC uncertainty for conservative overcurrent conversion; below 0.6 A requires calibration.'},
        'mode_checks':modes,
        'steady_switch_examples':[{'load_a':i,'i_squared_r_loss_w':round(i*i*.050,4),
             'q1_hot_screen_loss_w':round(i*i*q1_hot_screen,4)} for i in (1,1.5,2,2.5,3)],
        'thermal_example_limit':'50 milliohm eFuse datasheet maximum; Q1 temperature allowance is an engineering screen. No board theta-JA or junction rise is established. Add copper, contacts, quiescent and neighbouring losses.',
        'transient_screen':{'tvs_standoff_v':22,'specified_hot_clamp_v':28.35,
            'tvs_test_pulse':'35 A, 8/20 us; not a continuous absorption or arbitrary motor-energy rating',
            'efuse_operating_max_v':40,'efuse_absolute_max_v':60,'q1_vds_v':60,'hv_capacitors_v':50,
            'negative_clamp':'PMEG4030ER-QX, 40 V; 50 A non-repetitive 8.3 ms half sine at 25 C. Wiring overshoot/negative pin voltage still require scope measurements.'},
        'bench_candidate_a':3,'bench_candidate_status':'staged test target only',
        'required_before_power_qualification':[
            'Measure connector, Q1, U3, copper, plated holes and actual pin-40/ground contacts at each fixed PDO, ambient and load step. Stop on excessive temperature or shutdown.',
            'Test 5 V startup/dropout with worst cable resistance; UV supervisor requires about 4.76 V nominal at VBUS to start. Do not promise 3 A from every 5 V source.',
            'Measure input inrush, loaded startup, hard short, hot plug, detach, reset and renegotiation; keep motor driver disabled until output stabilizes.',
            'Verify C12 effective capacitance >=1 uF at 21 V. Include tolerance, temperature and aging. Typical manufacturer bias curves are screening evidence only.',
            'Use external motor/coil drivers with local recirculation/flyback. No unknown inductive load or sustained regeneration is qualified by the TVS pulse rating.',
            'Test reverse current through Q1/Q2 and U3, loss of 3V3, SHDN interlock response, VSYS isolation and MCU back-power.',
            'MX26631 auto-retries after a fault; validate MCU fault latching, watchdog/default-off behavior and repeated-retry heating with stalled loads. Do not promise hardware latch-off.',
            'Verify BSS138 gate discharge at minimum DRV voltage and worst capacitance; the datasheet does not guarantee its 3 V switching time.',
            'Integrate native PD transport, calibrated ADC, watchdog and measured control-supply reserve. Portable policy tests do not establish flashable firmware readiness.',
            'Confirm actual purchased connector/contact and resistor temperature grades, including sustained overload up to the measured upper fault threshold and retry cycling; source current must cover both pin 40 and the board supply.'
        ],
        'sources':{'efuse':'https://www.maxinmicro.com/action/download?file=7',
            'blocking_fet':'https://www.aosmd.com/res/datasheets/AON7264E.pdf',
            'uv_supervisor':'https://www.ti.com/lit/ds/symlink/tps3701.pdf',
            'tvs':'https://www.ti.com/lit/ds/symlink/tvs2200.pdf',
            'negative_clamp':'https://assets.nexperia.com/documents/data-sheet/PMEG4030ER-Q.pdf',
            'thermal_metrics':'https://www.ti.com/lit/an/spra953d/spra953d.pdf'}}


def report():
    screen=qualification_screen()
    return {'revision':BOARD_REVISION,'status':'calculation only; no qualified continuous current rating',
        'topology':'VBUS -> Q1/Q2 reverse blocker driven by MX26631 -> MX26631 auto-retry eFuse -> pin 40; independent upstream UV interlock; input/output TVS; separate fixed 3.3 V buck',
        'input_pd_contract_goal_v':20,'input_pd_contract_goal_a':3,
        'output_continuous_rating_a':None,'3v3_header_bringup_limit_ma':50,
        'vsys_input_range_v':[4.3,5.5],'ovlo_v':screen['ovlo_static_screen_v'],
        'ilm_resistance_ohm':screen['ilm']['resistance_ohm'],
        'fault_current_threshold_nominal_a':screen['ilm']['nominal_a'],
        'fault_current_is_not_output_rating':True,'qualification_screen':screen,
        'switch_dissipation_at_3a_w':{'typical_30_milliohm':.270,'datasheet_max_50_milliohm':.450},
        'adc_divider':{'top_ohm':100000,'bottom_ohm':10000,'at_20v':20/11,'at_28p35v':28.35/11},
        'shutdown_control':{'pin':37,'net':'3V3_EN','assert':'ground','release':'open',
            'external_driver':'dry contact or 35 V-rated open drain','qualified':False}}


def main():
    p=ROOT/'build/power-review.json';p.write_text(json.dumps(report(),indent=2)+'\n')
    print(f'Wrote {p}; continuous output rating remains unassigned')
if __name__=='__main__':main()
