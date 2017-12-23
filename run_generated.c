#include <stdio.h>
#include "output/generated.c"
#include "sync_enforcer.c"

#define RUN_CLOCKS ( 1 )

void diagnose(SDTA *sdta)
{
    printf("loc: %d\tGS: %d\tGP: %d\tv_grp: %d\tv_lri: %d\n",
        sdta->current_location, lri_get_GS(sdta), lri_get_GP(sdta),
        lri_get_v_lri(sdta), lri_get_v_grp(sdta)
    );
}


void execute_tick(SDTA *sdta, SDTA *sdta_I) 
{
    
    
    // int next_loc = sdta->transfunc(RUN_CLOCKS, sdta->current_location, &sdta->transdata); 
    // sdta->current_location = next_loc;

    
    int input = (lri_get_GS(sdta) << 1);
    int output = lri_get_GP(sdta);
    int enforced_input = enforce_input(sdta_I, input);
    enforce_output(sdta, sdta_I, enforced_input, output);
    
    diagnose(sdta);
    
}

int main(void) {
    SDTA sdta_lri;
    SDTA sdta_lri_I;
    
    init_sdta_lri(&sdta_lri);
    init_sdta_lri(&sdta_lri_I);
    
    init_enforcer();
    
    diagnose(&sdta_lri);
    printf("Begin\n");
    
    for (int i = 0; i < 10; i ++) {
        execute_tick(&sdta_lri, &sdta_lri_I);
    }
    
    
    return 0;
}
