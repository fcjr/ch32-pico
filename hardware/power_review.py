# SPDX-License-Identifier: MIT
"""Current-revision first-order power estimates; no assigned prototype current rating."""
import json
from .circuit import COMPONENTS
from .library import ROOT
from .design import BOARD_REVISION


def passive_value(value):
    token=value.split()[0].removesuffix('F')
    scales={'k':1e3,'M':1e6,'u':1e-6,'n':1e-9,'p':1e-12}
    return float(token[:-1])*scales[token[-1]] if token[-1] in scales else float(token)


def qualification_screen(components=COMPONENTS):
    """Analytical screening only. No measured temperatures or released rating."""
    c={item.ref:item for item in components}
    r17,r18=(passive_value(c[ref].value) for ref in ('R17','R18'))
    resistance=1/(1/r17+1/r18)
    nominal=3334/resistance
    # TI specifies +/-10% for ILIM >1 A; external resistors add +/-1%.
    low,high=nominal*.9/1.01,nominal*1.1/.99
    slew=2000/(passive_value(c['C8'].value)*1e12)  # TI equation 4, V/ms
    top,bottom=(passive_value(c[ref].value) for ref in ('R20','R21'))
    ovlo_high=1.223*(1+top*1.01/(bottom*.99))+0.1e-6*top*1.01
    bleed=passive_value(c['R8'].value)
    component_findings=[]
    if passive_value(c['C8'].value)>10e-9 and 'PD_DVDT' in c['C8'].nets.values():
        component_findings.append('C8 exceeds 10 nF directly on dVdt. Add the TI-recommended 100 ohm series resistor, or redesign slew timing and validate loaded startup.')
    if passive_value(c['C12'].value)<1e-6:
        component_findings.append('C12 is below TI recommended >=1 uF output bypass; include DC-bias loss and load/cable inductance.')
    modes=[]
    for voltage in (5,9,12,15,20):
        rise_s=voltage/slew/1000
        modes.append({
            'nominal_v':voltage,'engineering_upper_check_v':voltage*1.05,
            'continuous_rating_a':None,'qualification':'not tested',
            'nominal_rise_time_ms':round(rise_s*1000,1),
            'resistive_startup_example':{
                'final_load_a':2,'peak_switch_w':voltage*2/4,
                'switch_energy_j':round(voltage*2*rise_s/6,4),
                'assumption':'ideal linear ramp into R=VIN/2 A; excludes capacitive load, foldback and thermal shutdown'},
            'r8_power_at_upper_check_mw':round((voltage*1.05)**2/(bleed*.99)*1000,3),
        })
    return {
        'status':'not qualified; pre-fabrication issues remain',
        'supported_fixed_voltage_modes_v':[5,9,12,15,20],
        'unsupported':'EPR 28/36/48 V and PPS/AVS requests; this is not an all-USB-PD-voltage design',
        'voltage_sweep_note':'+5% is an engineering screening point, not a USB-PD compliance test',
        'physical_measurements_available':False,
        'ilm':{'resistance_ohm':round(resistance,3),'nominal_a':round(nominal,4),
               'screen_min_a':round(low,4),'screen_max_a':round(high,4),
               'excludes':'resistor temperature drift, parasitics, ADC/firmware error and transient overshoot'},
        'ovlo_high_with_1percent_resistors_and_100na_leakage_v':round(ovlo_high,6),
        'ovlo_headroom_below_23v_operating_limit_v':round(23-ovlo_high,6),
        'dvdt_nominal_v_per_ms':slew,
        'mode_checks':modes,
        'steady_switch_examples':[
            {'load_a':i,'i_squared_r_loss_w':round(i*i*.045,4),
             'jedec_74p5_c_per_w_rise_c':round(i*i*.045*74.5,2)}
            for i in (1,1.5,2,2.5,3)],
        'thermal_example_limit':'45 milliohm conduction only; JEDEC theta-JA is not this PCB thermal resistance. Excludes quiescent loss and neighbouring heat.',
        'bench_candidate_a':2,
        'bench_candidate_status':'target for staged testing after resolving design issues; not an approved load or firmware limit',
        'required_before_power_qualification':component_findings+[
            'Review input positive/output negative transients. No VBUS TVS or output flyback clamp is fitted; OVLO disconnect does not clamp U3 IN.',
            'R20/R21 OVLO worst-case leaves essentially no margin below 23 V after static tolerance/leakage; include temperature drift and transients.',
            'Qualify unequal current sharing, connector/U3 necks, vias, return plane and solder joints; no current rating follows from DRC or summed widths.',
            'Specify the actual pin-40 contact/carrier and ground return. J1 is bare PCB pads, not a purchased rated connector.',
            'Review the long PD_ILM route and remote R17/R18/R24 against TI placement and <50 pF parasitic guidance.',
            'Verify shutdown/back-power, 5 V cable-drop startup, R8 temperature/power derating, MLCC effective capacitance and control-rail load.',
            'Integrate PD transport, calibrated ADC thresholds, watchdog and load budgeting; the standalone policy still permits callers to supply a 5 A limit.',
        ],
        'sources':{
            'efuse':'https://www.ti.com/lit/ds/symlink/tps25947.pdf',
            'thermal_metrics':'https://www.ti.com/lit/an/spra953d/spra953d.pdf',
            'buck':'https://www.diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf',
        },
    }


def report():
    screen=qualification_screen()
    return {
        'revision':BOARD_REVISION,'status':'calculation only; no qualified continuous current rating',
        'topology':'VBUS -> protected load switch -> pin 40; separate fixed 3.3 V buck',
        'input_pd_contract_goal_v':20,'input_pd_contract_goal_a':3,
        'output_continuous_rating_a':None,'3v3_header_bringup_limit_ma':50,
        'vsys_input_range_v':[4.3,5.5],
        'ovlo_v':{'nominal':round(1.2*(1+82000/4700),4),
                  'minimum_1percent_resistors':round(1.183*(1+82000*.99/(4700*1.01)),4),
                  'maximum_1percent_resistors':round(1.223*(1+82000*1.01/(4700*.99)),4),
                  'excludes':'pin leakage and dynamic overshoot; review on bench'},
        'ilm_resistance_ohm':round(1/(1/4700+1/1500),3),
        'ilm_resistors_ohm':{'R17':4700,'R18':1500},
        'fault_current_threshold_nominal_a':round(3334*(1/4700+1/1500),3),
        'fault_current_tolerance':'Nominal only; IC and 1% resistor tolerances permit more than 3 A',
        'fault_current_is_not_output_rating':True,
        'qualification_screen':screen,
        'switch_dissipation_at_3a_w':{'typical_28p3_milliohm':.2547,
                                     'example_hot_45_milliohm':.405},
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
