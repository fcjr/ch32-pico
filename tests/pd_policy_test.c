/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include "policy.h"
#define PDO(mv,ma) (((mv)/50u)<<10 | ((ma)/10u))
int main(void) {
    const uint32_t caps[]={PDO(5000,3000),PDO(9000,3000),PDO(15000,3000),PDO(20000,5000)};
    pd_policy p;pd_init(&p);assert(!p.gate);
    pd_select(&p,caps,4,12000,5000,100);assert(p.state==PD_OFF);
    uint32_t e=pd_select(&p,caps,4,20000,5000,100);
    assert(p.pdo_position==4 && p.load_budget_ma==4900);
    assert(!pd_arm(&p,20000,true));assert(!pd_ready(&p,e,20000));
    assert(!pd_can_request(&p,9000));assert(pd_can_request(&p,0));
    assert(!pd_ready(&p,e,20000)); /* PS_RDY before ACCEPT is invalid */
    assert(!pd_accepted(&p,e-1));assert(pd_accepted(&p,e));
    assert(!pd_accepted(&p,e));
    assert(!pd_ready(&p,e,9000));assert(!p.gate);
    assert(pd_ready(&p,e,20000));assert(!p.gate);
    assert(pd_arm(&p,20000,true));
    pd_monitor(&p,true,true,20000,4901);assert(!p.gate && p.state==PD_FAULT);
    assert(!pd_arm(&p,20000,true));
    e=pd_select(&p,caps,4,5000,3000,100);assert(!p.gate && p.load_budget_ma==2900);
    assert(pd_can_request(&p,800));assert(pd_accepted(&p,e));assert(pd_ready(&p,e,5000));assert(pd_arm(&p,5000,true));
    pd_invalidate(&p);assert(!p.gate);assert(!pd_ready(&p,e,5000));
    e=pd_select(&p,caps,4,20000,1500,100);assert(p.contract_ma==1500 && p.load_budget_ma==1400);
    assert(pd_can_request(&p,0));pd_invalidate(&p);assert(!pd_ready(&p,e,20000));
    e=pd_select(&p,caps,4,9000,5000,100);assert(p.contract_ma==3000);
    assert(pd_can_request(&p,0));assert(pd_accepted(&p,e));assert(pd_ready(&p,e,9000));assert(pd_arm(&p,9000,true));
    pd_monitor(&p,false,true,9000,0);assert(!p.gate && p.state==PD_OFF);
    e=pd_select(&p,caps,4,9000,5000,100);assert(pd_can_request(&p,0));assert(pd_accepted(&p,e));assert(pd_ready(&p,e,9000));
    assert(!pd_arm(&p,9000,false));assert(p.state==PD_FAULT);
    pd_select(&p,caps,4,20000,6000,100);assert(p.state==PD_OFF);
    const uint32_t bad[]={PDO(20000,6000),0xc0000000u|PDO(20000,5000)};
    pd_select(&p,bad,2,20000,5000,100);assert(p.state==PD_OFF);
    pd_select(&p,caps,4,20000,100,100);assert(p.state==PD_OFF);
    pd_select(&p,caps,4,20000,4999,100);
    assert(p.contract_ma==4990 && p.load_budget_ma==4890);
    return 0;
}
