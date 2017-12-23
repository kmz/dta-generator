#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
 
 
#define MAX_NUM_LOCATIONS ( 2 )
#define MAX_NUM_ACCEPTING_LOCATIONS ( 1 )
#define MAX_ALPHABET_SIZE ( 4 )
#define MAX_NUM_SIGNALS ( 2 )
#define MAX_NUM_CLOCKS ( 2 )


//*** Locations for lri
#define LOC_LRI_l0 ( 0 ) 
#define LOC_LRI_lv ( 1 ) 


//*** Getters for lri
#define lri_get_GS(sdta) ( sdta->transdata.signals[0] )
#define lri_get_GP(sdta) ( sdta->transdata.signals[1] )


//*** Setters for lri
#define lri_set_GS(sdta, x) ( sdta->transdata.signals[0] = x ) 
#define lri_set_GP(sdta, x) ( sdta->transdata.signals[1] = x ) 
 

//*** Clock getters for lri
#define lri_get_v_lri(sdta) ( sdta->transdata.clocks[0] ) 
#define lri_get_v_grp(sdta) ( sdta->transdata.clocks[1] ) 
  

typedef struct SDTA_transdata
{
    int signals[MAX_NUM_SIGNALS];
    int clocks[MAX_NUM_CLOCKS];
} SDTA_transdata;
   
typedef struct SDTA
{
    int num_locations;
    int num_accepting_locations;
    int num_alphabet;
    int num_signals;
    int num_clocks;
    int initial_location;
    int trap_location;
    int current_location;
    int locations[MAX_NUM_LOCATIONS];
    int accepting_locations[MAX_NUM_ACCEPTING_LOCATIONS];
    int alphabet[MAX_ALPHABET_SIZE];

    SDTA_transdata transdata;

    int (*transfunc) (int, int, SDTA_transdata *);
    void (*set_input_event) (SDTA_transdata *, int);
    void (*set_output_event) (SDTA_transdata *, int);
    
    int priority;
    
} SDTA;


void init_alphabet(int *alphabet, int len) {
    for (int i = 0; i < len; i++) {
        alphabet[i] = i;
    }
}


void init_transdata(int *array, int len) {
    for (int i = 0; i < len; i++) {
        array[i] = 0;
    }
}



//*** Inner transition function for lri
int transfunc_inner_lri(int do_clks, int current_loc, int GS, int GP, int *v_lri, int *v_grp) {
	int next_loc = current_loc;
	int do_reset_v_lri = 0;
	int do_reset_v_grp = 0;
	if ((current_loc == LOC_LRI_l0) && ((GS || GP) && *v_grp < 0)) {
		next_loc = LOC_LRI_l0;
	} else if ((current_loc == LOC_LRI_l0) && ((GS || GP) && *v_grp >= 0)) {
		next_loc = LOC_LRI_l0;
		do_reset_v_lri = 1;
		do_reset_v_grp = 1;
	} else if ((current_loc == LOC_LRI_l0) && (*v_lri > 5)) {
		next_loc = LOC_LRI_lv;
	} else if ((current_loc == LOC_LRI_lv) && (1)) {
		next_loc = LOC_LRI_lv;
	}
	if (do_clks) {
		if (do_reset_v_lri) {
 			*v_lri = 0; 
 		} else { 
 			*v_lri += 1; 
		}
		if (do_reset_v_grp) {
 			*v_grp = 0; 
 		} else { 
 			*v_grp += 1; 
		}

	}
	return next_loc;
}


//*** Transition function for lri
int transfunc_lri(int do_clks, int current_location, SDTA_transdata *transdata) {
	return transfunc_inner_lri(do_clks, current_location, transdata->signals[0], transdata->signals[1], &(transdata->clocks[0]), &(transdata->clocks[1]));
}

//*** Set input event function for lri
void set_input_event_lri(SDTA_transdata *transdata, int input_event) {
	transdata->signals[0] = input_event >> 1;
}


//*** Set output event function for lri
void set_output_event_lri(SDTA_transdata *transdata, int output_event) {
	transdata->signals[1] = output_event >> 0;
}


//*** Initialization function for lri
void init_sdta_lri(SDTA *sdta) {
	sdta->num_locations = 2;
	sdta->num_accepting_locations = 1;
	sdta->num_alphabet = 4;
	sdta->num_signals = 2;
	sdta->num_clocks = 2;
	sdta->initial_location = LOC_LRI_l0;
	sdta->current_location = LOC_LRI_l0;
	sdta->trap_location = LOC_LRI_lv;
	sdta->locations[0] = LOC_LRI_l0;
	sdta->locations[1] = LOC_LRI_lv;
	sdta->accepting_locations[0] = LOC_LRI_l0;
	init_alphabet(sdta->alphabet, sdta->num_alphabet);
	sdta->transfunc = transfunc_lri;
	sdta->set_input_event = set_input_event_lri;
	sdta->set_output_event = set_output_event_lri;
	sdta->priority = 5;
	init_transdata(sdta->transdata.signals, sdta->num_signals);
	init_transdata(sdta->transdata.clocks, sdta->num_clocks);
}

