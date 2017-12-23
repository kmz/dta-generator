#ifndef SYNC_ENFORCER
#define SYNC_ENFORCER
#define SIZE 4


#include <math.h>

int good_act[SIZE];
int num_good_acts = 0;

int good_out_act[SIZE];
int num_good_out_acts = 0;

// def editI(phiI, qI):
void editI(SDTA *phiI) {


    int input_act = 0;
    int output_act = 0;
    int loc, i;

    for (input_act = 0; input_act < (phiI->num_alphabet / 2); input_act++) {
        
        phiI->set_input_event(&phiI->transdata, input_act);

        for (output_act = 0; output_act < (phiI->num_alphabet / 2); output_act++) {
            
            phiI->set_output_event(&phiI->transdata, output_act);
            
            loc = phiI->transfunc(0, phiI->current_location, &phiI->transdata);
            
            // if not loc == phiI.lv:
            if(loc != phiI->trap_location) {

                // if not act in goodAct:
                    // goodAct.append(act)

                for (i = 0; i < SIZE; i++) {
                    if (i < num_good_acts) {
                        if(good_act[i] == input_act) {
                            break;
                        }            
                    }
                    else {
                        good_act[i] = input_act;
                        num_good_acts++;
                        break;
                    }
                    
                }
            }
        }
    }
    // return goodAct
}

// def min_editI(actions, event):
int min_editI(int event, int signal_length) {



    int val = 0;
    int min_diff = 0xffffffff;
    int min_index = -1;
    int act;
    int distance = 0;

    // Iterate through actions
    for(int i = 0; i < num_good_acts; i++) {

        act = good_act[i];

        val = act ^ event;

        distance = 0;

        // Count Hamming distance
        for(int j = 0; j < signal_length; j++) 
        {   
            // if val[j] == 1
            if(val) 
            {
                distance++;
            }

            val = val >> 1;
        }

        // Find min Hamming distance
        if (distance < min_diff) {
            
            min_diff = distance;
            min_index = i;
        }

    }

    // return actions[random.choice(min_indexes)]
    return good_out_act[min_index];
}

/*def editO(phi, q, x):

    for act in phi.S:
        if not (act[1] in outAct):
            outAct.append(act[1])
    for act in outAct:
        loc = phi.d(q,(x,act), phi.V, do_clks = False)
        if not loc == phi.lv:
            if not act in goodOutAct:
                goodOutAct.append(act)
    return goodOutAct
*/

void editO(SDTA *phi,int x) {
    /*
    Returns all actions that lead to a location that is not 
        non-accepting given an automaton, current location, 
        and the input action
        
    Inputs: phi - automaton
            q   - location the automaton is in
            x   - input action
    Output: goodOutAct - list of allowable actions
    */

    int output_act = 0;
    int loc, i;

    
    phi->set_input_event(&phi->transdata, x);

    // for act in outAct:
    for (output_act = 0; output_act < (phi->num_alphabet / 2); output_act++) {
        
        phi->set_output_event(&phi->transdata, output_act);
        
        // loc = phi.d(q,(x,act), phi.V, do_clks = False)
        loc = phi->transfunc(1, phi->current_location, &phi->transdata);
        
        // if not loc == phi.lv:
        if(loc != phi->trap_location) {

            // if not act in goodOutAct:
            //     goodOutAct.append(act)

            for (i = 0; i < SIZE; i++) {
                if (i < num_good_out_acts) {
                    if(good_out_act[i] == output_act) {
                        break;
                    }            
                }
                else {
                    good_out_act[i] = output_act;
                    num_good_out_acts++;
                    break;
                }
                
            }
        }
    }
    // return goodOutAct
}

// def min_editO(actions, outEvent):
int min_editO(int outEvent, int signal_length) {
    /*diff_count = []
    for act in actions:
        count = 0
        u=zip(outEvent, act)
        for i,j in u:
            if not i==j:
                count = count+1
        diff_count.append(count)
    min_indexes = FuncLists.all_indices(min(diff_count), diff_count)
    return actions[random.choice(min_indexes)]*/
    int val = 0;
    int min_diff = 0xffffffff;
    int min_index = -1;
    int act, i , j, distance;

    // Iterate through actions
    for(i = 0; i < num_good_out_acts; i++) {

        act = good_out_act[i];

        val = act ^ outEvent;

        distance = 0;

        // Count Hamming distance
        for(j = 0; j < signal_length; j++) 
        {   
            // if val[j] == 1
            if(val) 
            {
                distance++;
            }

            val = val >> 1;
        }

        // Find min Hamming distance
        if (distance < min_diff) {
            
            min_diff = distance;
            min_index = i;
        }

    }//editO

    // return actions[random.choice(min_indexes)]
    return good_out_act[min_index];
}

// def enforce_input(SDTA *phiI, int x, qI):
int enforce_input(SDTA *phiI, int x) {
/*
    ##Initially output is empty.###
    ##Input automaton phiI from input-output automaton phi.##

    ## transformed input xNew, and transformed output yNew initialized to [] ##
    // xNew = "NONE"
*/
    int xNew = -1;

    int input_act = 0;
    int output_act = 0;
    int loc;

    // for act in phiI.get_S_input():
    //    for loc in phiI.d_input(qI, act):
    for (input_act = 0; input_act < (phiI->num_alphabet / 2); input_act++) {
        
        phiI->set_input_event(&phiI->transdata, input_act);

        for (output_act = 0; output_act < (phiI->num_alphabet / 2); output_act++) {
            
            phiI->set_output_event(&phiI->transdata, output_act);
            
            loc = phiI->transfunc(0, phiI->current_location, &phiI->transdata);
            
            // if not loc == phiI.lv:
            if(loc != phiI->trap_location) {

                //return xNew  
                return x;

            }
        }
    }

    num_good_acts = 0;
    // there is no transition in phiI from qI upon (x,-) to qIi that is not a non-accepting location
    editI(phiI);
    // if not allowed_inputs == []:
    if(num_good_acts > 0){

       xNew = min_editI(x, phiI->num_signals);
        
        // return xNew
        return xNew;
    } 
    else 
    {
        //## change to fail gracefully
        //# the property is unenforcable
        // return ()
        return -1;
    }
}

int enforce_output(SDTA *phi, SDTA *phiI, int xNew, int y) {


    int loc;
    int yNew;

    //## deterministic, therefore should only be one transition
    //# if there is a transition in phi from q with action (xNew,y) to a location qi that is not a non-accepting location
    
    phi->set_input_event(&phi->transdata, xNew);
    phi->set_output_event(&phi->transdata, y);

    loc = phi->transfunc(0, phi->current_location ,&phi->transdata);

    // if not phi.lv == q_next:
    if(loc != phi->trap_location) {

	// clock updates

        phi->current_location  = phi->transfunc(1, phi->current_location, &phi->transdata);

        phiI->set_input_event(&phiI->transdata, xNew);
        phiI->set_output_event(&phiI->transdata, y);
        phiI->current_location = phiI->transfunc(1, phiI->current_location, &phiI->transdata);

        return y;

    }
    else {
        // if there is a transition in phi from q upon action (xNew,y') to a location qi that is not a non-accepting location
        num_good_out_acts = 0;
        editO(phi, xNew);
        //if not allowed_actions == []:
        if(num_good_out_acts > 0){

            yNew = min_editO(y, phi->num_signals);

            //## update to use the transition state outputs as current state
            //# clock updates
            
            phi->set_output_event(&phi->transdata, yNew);
            phi->current_location  = phi->transfunc(1, phi->current_location, &phi->transdata);

            phiI->set_input_event(&phi->transdata, xNew);
            phiI->set_output_event(&phi->transdata, yNew);
            phiI->current_location = phiI->transfunc(1, phiI->current_location, &phiI->transdata);
            
            return yNew;
        }
        else 
        {

            // return ()
            return -1;
        }
    }

}

void init_enforcer(void) {
    int i;
    for(i = 0; i < SIZE; i++) {
        good_act[i] = 0;
        good_out_act[i] = 0;
	
    }

    return;

}


#endif
