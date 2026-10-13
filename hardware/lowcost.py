# SPDX-License-Identifier: MIT
"""Compatibility entry point for the electrical contract check.

The Rev A implementation is preserved in the pre-migration archive. New code
should import hardware.verify.verify_contract directly.
"""
from .circuit import COMPONENTS as COMPONENTS_LOWCOST

def verify(components=COMPONENTS_LOWCOST):
    from .verify import verify_contract
    verify_contract(components)
    return {'status':'CH32X035 circuit contract; prototype power rating pending',
            'fitted_parts':sum(c.fitted for c in components),
            'unique_lcsc_parts':len({c.part for c in components if c.fitted})}
