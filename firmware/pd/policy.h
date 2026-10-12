/* SPDX-License-Identifier: MIT */
#ifndef CH32_PICO_PD_POLICY_H
#define CH32_PICO_PD_POLICY_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Platform-independent policy only. The USB-PD transport and GPIO/ADC driver
 * must call these hooks; this file is not flashable board firmware. */
typedef enum { PD_OFF, PD_WAIT_DISCHARGE, PD_WAIT_ACCEPT, PD_WAIT_READY, PD_READY, PD_FAULT } pd_state;
typedef struct {
    pd_state state;
    uint32_t epoch;
    uint16_t target_mv, contract_ma, load_budget_ma;
    uint8_t pdo_position;
    bool gate;
} pd_policy;

void pd_init(pd_policy *p);
/* Returns a fresh epoch; unsupported voltage/no current budget leaves OFF.
 * caps are the source's received fixed SPR PDOs, not guessed charger ratings.
 * Source is responsible for restricting advertised current to its cable rating.
 * board_limit_ma must be the qualified assembly/connection rating, <= 5000.
 */
uint32_t pd_select(pd_policy *p, const uint32_t *caps, size_t count,
                   uint16_t mv, uint16_t board_limit_ma, uint16_t reserve_ma);
/* Caller may send the RDO only when this returns true. */
bool pd_can_request(pd_policy *p, uint16_t measured_output_mv);
/* Invoke only for ACCEPT matching the outstanding request. */
bool pd_accepted(pd_policy *p, uint32_t epoch);
/* Invoke only on PS_RDY for this request, never on ACCEPT alone. */
bool pd_ready(pd_policy *p, uint32_t epoch, uint16_t measured_vbus_mv);
bool pd_arm(pd_policy *p, uint16_t measured_vbus_mv, bool fault_n);
/* Run continuously while armed; any error latches off. Hardware watchdog and
 * direct reset/detach hooks must also drive PD_ENABLE low, without waiting here. */
void pd_monitor(pd_policy *p, bool attached, bool fault_n,
                uint16_t vbus_mv, uint16_t output_ma);
void pd_invalidate(pd_policy *p); /* detach, hard/soft reset, timeout, watchdog */
#endif
