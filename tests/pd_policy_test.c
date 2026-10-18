/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include "policy.h"
#define PDO(mv,ma) (((mv)/50u)<<10 | ((ma)/10u))
int main(void) {
    const uint32_t caps[]={PDO(5000,3000),PDO(9000,3000),PDO(15000,3000),PDO(20000,5000)};
    pd_policy p;pd_init(&p,20000);assert(pd_expected_mv(&p)==5000);
    pd_select(&p,caps,4,12000,3000,100);assert(p.state==PD_OFF); /* absent PDO is never substituted */
    uint32_t e=pd_select(&p,caps,4,20000,3000,100);
    assert(p.pdo_position==4 && p.load_budget_ma==2900 && p.state==PD_REQUEST);
    assert(pd_expected_mv(&p)==5000); /* still at the source default */
    assert(!pd_ready(&p,e,20000));assert(!pd_accepted(&p,e));
    assert(pd_can_request(&p));assert(!pd_can_request(&p)); /* one RDO per request */
    assert(!pd_ready(&p,e,20000)); /* PS_RDY before ACCEPT is invalid */
    assert(!pd_accepted(&p,e-1));assert(pd_accepted(&p,e));
    assert(!pd_accepted(&p,e));
    assert(!pd_ready(&p,e,9000));assert(pd_ready(&p,e,20000));
    assert(p.state==PD_READY && pd_expected_mv(&p)==20000);
    pd_monitor(&p,true,20100);assert(p.state==PD_READY);
    pd_monitor(&p,true,15000);assert(p.state==PD_OFF && pd_expected_mv(&p)==5000); /* contract lost */
    e=pd_select(&p,caps,4,5000,3000,100);assert(p.load_budget_ma==2900);
    assert(pd_can_request(&p));assert(pd_accepted(&p,e));assert(pd_ready(&p,e,5000));
    pd_invalidate(&p);assert(!pd_ready(&p,e,5000));assert(p.carrier_max_mv==20000);
    e=pd_select(&p,caps,4,20000,1500,100);assert(p.contract_ma==1500 && p.load_budget_ma==1400);
    assert(pd_can_request(&p));pd_invalidate(&p);assert(!pd_accepted(&p,e));
    e=pd_select(&p,caps,4,9000,3000,100);assert(p.contract_ma==3000);
    assert(pd_can_request(&p));assert(pd_accepted(&p,e));assert(pd_ready(&p,e,9000));
    pd_monitor(&p,false,9000);assert(p.state==PD_OFF);
    pd_select(&p,caps,4,20000,6000,100);assert(p.state==PD_OFF);
    const uint32_t bad[]={PDO(20000,6000),0xc0000000u|PDO(20000,5000)};
    pd_select(&p,bad,2,20000,3000,100);assert(p.state==PD_OFF);
    pd_select(&p,caps,4,20000,100,100);assert(p.state==PD_OFF);
    pd_select(&p,caps,4,20000,2999,100);
    assert(p.contract_ma==2990 && p.load_budget_ma==2890);
    pd_select(&p,caps,4,20000,3001,100);assert(p.state==PD_OFF);
    pd_select(&p,caps,4,5000,3000,0);assert(p.state==PD_OFF);
    /* A 5 V-only carrier never sees a higher request. */
    pd_policy q;pd_init(&q,5000);
    pd_select(&q,caps,4,9000,3000,100);assert(q.state==PD_OFF);
    pd_select(&q,caps,4,5000,3000,100);assert(q.state==PD_REQUEST);
    return 0;
}
