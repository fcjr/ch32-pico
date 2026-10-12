# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Electrical safety contracts for the low-cost board."""
from .circuit import COMPONENTS
from .design import HEADER

COMPONENTS_LOWCOST = COMPONENTS


def verify(components=COMPONENTS_LOWCOST):
    from .library import load_library, validate_library
    validate_library(components,load_library())
    c={x.ref:x for x in components}
    expected={
        'U1':{'7':'GND','9':'TARGET_3V3'},
        'U2':{'1':'PROBE_DP','2':'USB_DPU','4':'PROBE_RUN','7':'GND','9':'3V3_OUT',
              '11':'PROBE_SWIO','12':'PROBE_SWIO','16':'VBUS_N','18':'PROBE_BOOT_SWIO','19':'TARGET_EN','20':'PROBE_DM'},
        'U4':{'1':'VSYS','2':'GND','3':'3V3_EN','4':None,'5':'3V3_OUT'},
        'U5':{'1':'VSYS','2':'GND','3':'TARGET_EN','4':None,'5':'TARGET_3V3'},
        'R2':{'1':'TARGET_EN','2':'GND'},'R12':{'1':'TARGET_3V3','2':'GND'},
        'R16':{'1':'PD1','2':'TARGET_3V3'},'R9':{'1':'USB_DPU','2':'USB_DM'},
    }
    for ref,pins in expected.items():
        for pin,net in pins.items():
            if c[ref].nets[pin]!=net:
                raise ValueError(f'Cost-down contract: {ref}.{pin} must be {net}')
    if c['U2'].part!='C5187096' or c['U4'].part!=c['U5'].part or c['U4'].part!='C82942':
        raise ValueError('Cost-down MCU/regulator selection changed')
    if c['J1'].nets!={str(p.number):None if p.proposed=='NC' else p.proposed for p in HEADER}:
        raise ValueError('Pico header allocation changed')
    # The GPIO only drives an enable input, not the MCU supply or its pull-up.
    enable_nodes={(x.ref,p) for x in components for p,n in x.nets.items() if n=='TARGET_EN'}
    if enable_nodes!={('U2','19'),('U5','3'),('R2','1')}:
        raise ValueError('Unexpected load on target enable GPIO')
    return {'status':'low-cost electrical contract checked; layout validated separately',
            'fitted_parts':sum(x.fitted for x in components),
            'unique_lcsc_parts':len({x.part for x in components if x.fitted})}
