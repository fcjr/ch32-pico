/* SPDX-License-Identifier: MIT */
#include "policy.h"

void pd_init(pd_policy *p,uint16_t carrier_max_mv) {
    *p=(pd_policy){.state=PD_OFF,.carrier_max_mv=carrier_max_mv};
}
void pd_invalidate(pd_policy *p) {
    *p=(pd_policy){.state=PD_OFF,.epoch=p->epoch+1,.carrier_max_mv=p->carrier_max_mv};
}
static bool voltage_allowed(const pd_policy *p,uint16_t mv) {
    return (mv==5000 || mv==9000 || mv==12000 || mv==15000 || mv==20000) && mv<=p->carrier_max_mv;
}
static bool voltage_matches(const pd_policy *p,uint16_t mv) {
    return p->target_mv && (uint32_t)mv*100>=p->target_mv*95u
           && (uint32_t)mv*100<=p->target_mv*105u;
}
uint32_t pd_select(pd_policy *p,const uint32_t *caps,size_t count,
                   uint16_t mv,uint16_t board_limit_ma,uint16_t reserve_ma) {
    pd_invalidate(p); /* a bad command still abandons the previous contract */
    if (!caps || !voltage_allowed(p,mv) || !board_limit_ma || board_limit_ma>3000 || reserve_ma<100)
        return p->epoch;
    if (count>7) count=7; /* SPR Source_Capabilities has at most seven PDOs */
    for (size_t i=0;i<count;i++) {
        uint32_t raw=caps[i];
        if ((raw>>30)!=0 || (((raw>>10)&1023u)*50u)!=mv) continue;
        uint16_t ma=(raw&1023u)*10u;
        if (!ma || ma>5000) continue; /* reject malformed SPR capabilities */
        if (ma>board_limit_ma) ma=board_limit_ma;
        ma=(ma/10u)*10u; /* fixed-PDO RDO current has 10 mA resolution */
        if (ma<=reserve_ma || ma<=p->contract_ma) continue;
        p->target_mv=mv;p->contract_ma=ma;p->load_budget_ma=ma-reserve_ma;
        p->pdo_position=(uint8_t)i+1;p->state=PD_REQUEST;
    }
    return p->epoch;
}
bool pd_can_request(pd_policy *p) {
    if (p->state!=PD_REQUEST) return false;
    p->state=PD_WAIT_ACCEPT;return true;
}
bool pd_accepted(pd_policy *p,uint32_t epoch) {
    if (p->state!=PD_WAIT_ACCEPT || p->epoch!=epoch) return false;
    p->state=PD_WAIT_READY;return true;
}
bool pd_ready(pd_policy *p,uint32_t epoch,uint16_t measured_vbus_mv) {
    if (p->state!=PD_WAIT_READY || p->epoch!=epoch || !voltage_matches(p,measured_vbus_mv))
        return false;
    p->state=PD_READY;return true;
}
void pd_monitor(pd_policy *p,bool attached,uint16_t vbus_mv) {
    if (!attached || (p->state==PD_READY && !voltage_matches(p,vbus_mv))) pd_invalidate(p);
}
uint16_t pd_expected_mv(const pd_policy *p) {
    return p->state==PD_READY ? p->target_mv : 5000;
}
