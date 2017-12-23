#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
 
 
#define MAX_NUM_LOCATIONS ( **MAX_NUM_LOCATIONS** )
#define MAX_NUM_ACCEPTING_LOCATIONS ( **MAX_NUM_ACCEPTING_LOCATIONS** )
#define MAX_ALPHABET_SIZE ( **MAX_ALPHABET_SIZE** )
#define MAX_NUM_SIGNALS ( **MAX_NUM_SIGNALS** )
#define MAX_NUM_CLOCKS ( **MAX_NUM_CLOCKS** )

**ENFORCER_LOCATION_DEFINES**
**ENFORCER_GETTER_DEFINES**
**ENFORCER_SETTER_DEFINES** 
**ENFORCER_CLOCK_GETTER_DEFINES**  

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


**ENFORCER_INNER_TRANS_FUNCTIONS**
**ENFORCER_TRANS_FUNCTIONS**
**ENFORCER_SET_INPUT_EVENT_FUNCTIONS**
**ENFORCER_SET_OUTPUT_EVENT_FUNCTIONS**
**ENFORCER_INIT_FUNCTIONS**

