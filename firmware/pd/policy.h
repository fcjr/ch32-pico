/* SPDX-License-Identifier: MIT */
#ifndef CH32_PICO_PD_POLICY_H
#define CH32_PICO_PD_POLICY_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Platform-independent sink policy. Header pin 40 is USB VBUS with no
 * switch: it carries 5 V from attach, and whatever contract this policy
 * negotiates afterwards. The USB-PD transport and ADC driver call these
 * hooks; this file is not flashable board firmware. */
typedef enum { PD_OFF, PD_REQUEST, PD_WAIT_ACCEPT, PD_WAIT_READY, PD_READY } pd_state;
typedef struct {
    pd_state state;
    uint32_t epoch;
    uint16_t target_mv, contract_ma, load_budget_ma, carrier_max_mv;
    uint8_t pdo_position;
} pd_policy;

/* carrier_max_mv is the highest voltage the attached carrier tolerates on
 * pin 40. Nothing above it is ever requested; 5 V is always present. */
void pd_init(pd_policy *p, uint16_t carrier_max_mv);
/* Returns a fresh epoch; an unsupported, over-carrier or budget-less request
 * leaves the policy OFF at the source's default 5 V.
 * caps are the source's received fixed SPR PDOs, not guessed charger ratings.
 * board_limit_ma must be the qualified assembly/connection rating, <= 3000.
 * reserve_ma must be at least 100 mA and include all 3V3 loads. */
uint32_t pd_select(pd_policy *p, const uint32_t *caps, size_t count,
                   uint16_t mv, uint16_t board_limit_ma, uint16_t reserve_ma);
/* Caller may send the RDO exactly once, when this returns true. */
bool pd_can_request(pd_policy *p);
/* Invoke only for ACCEPT matching the outstanding request. */
bool pd_accepted(pd_policy *p, uint32_t epoch);
/* Invoke only on PS_RDY for this request, never on ACCEPT alone. */
bool pd_ready(pd_policy *p, uint32_t epoch, uint16_t measured_vbus_mv);
/* Run continuously. Detach or a measured VBUS outside the contract drops the
 * policy to OFF; the caller must then treat pin 40 as the source default. */
void pd_monitor(pd_policy *p, bool attached, uint16_t vbus_mv);
/* Nominal pin 40 voltage the policy currently expects while attached. */
uint16_t pd_expected_mv(const pd_policy *p);
void pd_invalidate(pd_policy *p); /* detach, hard/soft reset, timeout, watchdog */
#endif
