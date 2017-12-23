from graphviz import Source
import argparse
import os


def readfile(filename):
    content = []
    with open(filename) as openfile:
        content = openfile.readlines()
    return content

    
def writefile(filename, content):
    with open(filename, 'w') as openfile:
        openfile.write(content)
    
    
class Transition:
    def __init__(self, start, end, cond, clk_resets):
        self.start = start
        self.end = end
        self.cond = cond
        self.clk_resets = clk_resets
        
    def __str__(self):
        return_str = '{} -> {} if {}'.format(self.start, \
            self.end, self.cond)
        if self.clk_resets != []:
            return_str += ';'
            for clk in self.clk_resets:
                return_str += clk + ' = 0,'
            return_str = return_str.rstrip(',')
        return return_str + '\n'
    

class SDTA:
    def __init__(self, input_filename):
        self.input_filename = input_filename
        self.locs = []
        self.init_loc = ''
        self.trap_loc = ''
        self.alphabet = []
        self.clks = []
        self.transitions = []
        self.acc_locs = []
        self.name = ''
        self.source = []
        self.priority = 0
    
    def __str__(self):
        name_str = '*** {} ***\n'.format(self.name)
        priority = 'Priority: {}\n'.format(str(self.priority))
        locs_str = 'Locations:{}\n'.format(self.locs)
        acc_locs_str = 'Accepting Locs:{}\n'.format(self.acc_locs)
        init_loc_str = 'Initial Loc:{}\n'.format(self.init_loc)
        trap_loc_str = 'Trap Loc:{}\n'.format(self.trap_loc)
        alphabet_str = 'Alphabet:{}\n'.format(self.alphabet)
        clks_str = 'Clks:{}\n'.format(self.clks)
        return_str = name_str + priority + locs_str + acc_locs_str + init_loc_str + \
            trap_loc_str + alphabet_str + clks_str + 'Transitions:\n'
        for transition in self.transitions:
            return_str += str(transition)
        
        return return_str
        
    def parse_node(self, line_clean):
        node_name = line_clean.split(']')[1].strip()
        if '__init' in node_name:
            return 
        self.locs.append(node_name)
        
        if 'doublecircle' in line_clean:
            self.acc_locs.append(node_name)
        elif 'dashed' in line_clean:
            self.trap_loc = node_name

    def parse_transition(self, line_clean):
        start = line_clean.split('->')[0].strip()
        end = line_clean.split('->')[1].split('[')[0].strip()
        if '__init' in start:
            self.init_loc = end
            return
        
        label_content = line_clean.split('\"')[1].split(';')
        label_content = [s.strip() for s in label_content if s != '']
        
        cond = label_content[0]
        
        if len(label_content) == 1:
            transition = Transition(start,end, cond, [])
        else:
            clk_resets = label_content[1].strip(';').split(',')
            clk_resets = [c.split('=')[0].strip() for c in clk_resets]
            transition = Transition(start,end, cond, clk_resets)
        self.transitions.append(transition)
        
    def parse_alphabet(self, line_clean):
        alphabet_content = line_clean.split('[')[1].split(']')[0].split(',')
        alphabet_content = [s.strip() for s in alphabet_content]
        self.alphabet = alphabet_content
        
    def parse_clocks(self, line_clean):
        clocks_content = line_clean.split('[')[1].split(']')[0].split(',')
        clocks_content = [s.strip() for s in clocks_content]
        self.clks = clocks_content
        
    def parse_sdta_name(self, line_clean):
        sdta_name = line_clean.strip('digraph').strip('{').strip()
        self.name = sdta_name

    def parse_priority(self, line_clean):
        priority_str = line_clean.strip('//__priority').strip()
        self.priority = int(priority_str)
        
        
class ArraySizes:
    max_num_locations = 0
    max_num_accepting_locations = 0
    max_alphabet_size = 0
    max_num_signals = 0
    max_num_clocks = 0
    
  
def clean_line(line):
    return line.strip().rstrip(';')
    
    
def generate_trans_func_signature(sdta):
    signature = 'int transfunc_inner_{}(int do_clks, int current_loc, '.format(sdta.name)
    for signal in sdta.alphabet:
        signature += 'int {}, '.format(signal)
    for clk in sdta.clks:
        signature += 'int *{}, '.format(clk)
    signature = signature.rstrip(', ')
    signature += ') {\n'
    return signature
    
    
def generate_clk_reset_definitions(sdta):
    clk_reset_definitions = ''
    for clk in sdta.clks:
        clk_reset_definitions += '\tint do_reset_{} = 0;\n'.format(clk)
    return clk_reset_definitions
    
    
def generate_clk_update_statements(sdta):
    clk_update_statements = '\tif (do_clks) {\n'
    for clk in sdta.clks:
        clk_update_statements += '\t\tif (do_reset_' + clk + \
            ') {\n \t\t\t*' + clk + ' = 0; \n \t\t} else { \n \t\t\t*' + clk + ' += 1; \n\t\t}\n'
   
    clk_update_statements += '\n\t}\n'
    return clk_update_statements
    
    
def generate_transition_function(sdta):
    signature = 'int transfunc_{0}(int do_clks, int current_location, SDTA_transdata *transdata) {{\n'.format(sdta.name)
    body = '\treturn transfunc_inner_{}(do_clks, current_location, '.format(sdta.name)
    for i,signal in enumerate(sdta.alphabet):
        body += 'transdata->signals[{}], '.format(i)
    
    for i, clk in enumerate(sdta.clks):
        body += '&(transdata->clocks[{}]), '.format(i)
    body = body.rstrip(', ')
    body += ');\n}'
    return signature + body
    
    
def generate_set_input_event(sdta):
    signature = 'void set_input_event_{}(SDTA_transdata *transdata, int input_event) {{\n'.format(sdta.name)
    body = ''
    for i, signal in enumerate(sdta.alphabet):
        if i >= len(sdta.alphabet) / 2:
            break
        body += '\ttransdata->signals[{}] = input_event >> {};\n'.format(i, len(sdta.alphabet) -1 -i)
    body += '}\n'
    
    return signature + body
    
    
def generate_set_output_event(sdta):
    signature = 'void set_output_event_{}(SDTA_transdata *transdata, int output_event) {{\n'.format(sdta.name)
    body = ''
    for i, signal in enumerate(sdta.alphabet):
        if i < len(sdta.alphabet) / 2:
            continue
        body += '\ttransdata->signals[{}] = output_event >> {};\n'.format(i, len(sdta.alphabet) -1 -i)
    body += '}\n'
    
    return signature + body
    

def generate_transition_function_inner(sdta):
    signature = generate_trans_func_signature(sdta)
    clk_reset_definitions = generate_clk_reset_definitions(sdta)
    clk_update_statements = generate_clk_update_statements(sdta)
    next_loc_definition = '\tint next_loc = current_loc;\n'
    transition_body = ''
    return_statement = '\treturn next_loc;\n'
    for i, transition in enumerate(sdta.transitions):
        fixed_cond = transition.cond
        for clk in sdta.clks:
            fixed_cond = fixed_cond.replace(clk, '*' + clk)
        fixed_cond = fixed_cond.replace('and', '&&')
        fixed_cond = fixed_cond.replace('or', '||')
        fixed_cond = fixed_cond.replace('not', '!')
        fixed_cond = fixed_cond.replace('true', '1')
        fixed_cond = fixed_cond.replace('false', '0')
            
        if i == 0:
            transition_body += '\tif ('
            transition_body += '(current_loc == LOC_{}_{}) && ('.format(sdta.name.upper(), transition.start)
            transition_body += '{})) {{\n'.format(fixed_cond)
        else:
            transition_body += '\t} else if ('
            transition_body += '(current_loc == LOC_{}_{}) && ('.format(sdta.name.upper(), transition.start)
            transition_body += '{})) {{\n'.format(fixed_cond)
        transition_body += '\t\tnext_loc = LOC_{}_{};\n'.format(sdta.name.upper(), transition.end)
        for clk_reset in transition.clk_resets:
            transition_body += '\t\tdo_reset_{} = 1;\n'.format(clk_reset)
    transition_body += '\t}\n'
    
    transition_function = signature + next_loc_definition + clk_reset_definitions + \
        transition_body + clk_update_statements + return_statement + '}\n'
        
    return transition_function
    
    
def parse_gv(sdta, source):
    seen_digraph = False
    for i, line in enumerate(source):
        line_clean = clean_line(line)
        
        if line_clean.startswith('node'):
            sdta.parse_node(line_clean)
        elif '->' in line_clean:
            sdta.parse_transition(line_clean)
        elif line_clean.startswith('//__alphabet'):
            sdta.parse_alphabet(line_clean)
            source[i]=''
        elif line_clean.startswith('//__clocks'):
            sdta.parse_clocks(line_clean)
            source[i]=''
        elif line_clean.startswith('//__priority'):
            sdta.parse_priority(line_clean)
            source[i] = ''            
        elif line_clean.startswith('digraph'):
            if seen_digraph:
                raise Exception
            seen_digraph = True
            sdta.parse_sdta_name(line_clean)           
    sdta.source = source
    return sdta
            
    
def read_all_sdtas(input_filenames):
    sdtas =[]
    for input_filename in input_filenames:
        sdta = SDTA(input_filename)
        content = readfile(input_filename)
        sdta = parse_gv(sdta, content)
        sdtas.append(sdta)
        
    return sdtas
    
    
def get_array_sizes(sdtas):
    max_num_locations = 0
    max_num_accepting_locations = 0
    max_alphabet_size = 0
    max_num_signals = 0
    max_num_clocks = 0 
    
    array_sizes = ArraySizes()
    
    for sdta in sdtas:
        max_num_locations = max(max_num_locations, len(sdta.locs))
        max_num_accepting_locations = max(max_num_accepting_locations, 
            len(sdta.acc_locs))
        max_alphabet_size = max(max_alphabet_size, 2 ** len(sdta.alphabet))
        max_num_signals = max(max_num_signals, len(sdta.alphabet))
        max_num_clocks = max(max_num_clocks, len(sdta.clks))
        
    array_sizes.max_num_locations = max_num_locations
    array_sizes.max_num_accepting_locations = max_num_accepting_locations
    array_sizes.max_alphabet_size = max_alphabet_size
    array_sizes.max_num_signals = max_num_signals
    array_sizes.max_num_clocks = max_num_clocks
    
    return array_sizes
    
    
def generate_initialization(sdta):
    signature = 'void init_sdta_{}(SDTA *sdta) {{\n'.format(sdta.name)
    body = '\tsdta->num_locations = {};\n'.format(len(sdta.locs))
    body += '\tsdta->num_accepting_locations = {};\n'.format(len(sdta.acc_locs))
    body += '\tsdta->num_alphabet = {};\n'.format(2 ** len(sdta.alphabet))
    body += '\tsdta->num_signals = {};\n'.format(len(sdta.alphabet))
    body += '\tsdta->num_clocks = {};\n'.format(len(sdta.clks))
    
    location_defines = ''
    locations_init = ''
    getter_defines = ''
    setter_defines = ''
    accepting_locations_init = ''
    clock_getter_defines = ''
     
    for i, loc in enumerate(sdta.locs):
        locations_init += '\tsdta->locations[{}] = LOC_{}_{};\n'.format(i, sdta.name.upper(), loc)
        location_defines += '#define LOC_{}_{} ( {} ) \n'.format(sdta.name.upper(), loc, i)
        if loc == sdta.trap_loc:
            body += '\tsdta->trap_location = LOC_{}_{};\n'.format(sdta.name.upper(), loc)
        if loc == sdta.init_loc:
            body += '\tsdta->initial_location = LOC_{}_{};\n'.format(sdta.name.upper(), loc)
            body += '\tsdta->current_location = LOC_{}_{};\n'.format(sdta.name.upper(), loc)
        if loc in sdta.acc_locs:
            accepting_locations_init += '\tsdta->accepting_locations[{}] = LOC_{}_{};\n'.format(i, sdta.name.upper(), loc)
    
    body += locations_init + accepting_locations_init
    
    for i, signal in enumerate(sdta.alphabet):
        getter_defines += '#define {0}_get_{1}(sdta) ( sdta->transdata.signals[{2}] )\n'.format(sdta.name, signal, i)
        setter_defines += '#define {0}_set_{1}(sdta, x) ( sdta->transdata.signals[{2}] = x ) \n'.format(sdta.name, signal, i)
        
    for i, clock in enumerate(sdta.clks):
        clock_getter_defines += '#define {0}_get_{1}(sdta) ( sdta->transdata.clocks[{2}] ) \n'.format(sdta.name, clock, i)
    
    alphabet_init = '\tinit_alphabet(sdta->alphabet, sdta->num_alphabet);\n'
    body += alphabet_init
    body += '\tsdta->transfunc = transfunc_{};\n'.format(sdta.name)
    body += '\tsdta->set_input_event = set_input_event_{};\n'.format(sdta.name)
    body += '\tsdta->set_output_event = set_output_event_{};\n'.format(sdta.name)
    body += '\tsdta->priority = {};\n'.format(sdta.priority)
    body += '\tinit_transdata(sdta->transdata.signals, sdta->num_signals);\n'
    body += '\tinit_transdata(sdta->transdata.clocks, sdta->num_clocks);\n'
    body += '}'
    init_function = signature + body
    
    return init_function, location_defines, getter_defines, setter_defines, clock_getter_defines
    

def apply_array_sizes(array_sizes, template):
    template = template.replace('**MAX_NUM_LOCATIONS**', str(array_sizes.max_num_locations))
    template = template.replace('**MAX_NUM_ACCEPTING_LOCATIONS**', str(array_sizes.max_num_accepting_locations))
    template = template.replace('**MAX_ALPHABET_SIZE**', str(array_sizes.max_alphabet_size))
    template = template.replace('**MAX_NUM_SIGNALS**', str(array_sizes.max_num_signals))
    template = template.replace('**MAX_NUM_CLOCKS**', str(array_sizes.max_num_clocks))
    return template

    
def generate_c(sdtas, template_lines):
    template = ''.join(template_lines)
    array_sizes = get_array_sizes(sdtas)
    template = apply_array_sizes(array_sizes, template)
    
    all_location_defines = ''
    all_getter_defines = ''
    all_setter_defines = ''
    all_init_func_defines = ''
    all_inner_trans_func_defines = ''
    all_trans_func_defines = ''
    all_set_input_event_functions = ''
    all_set_output_event_functions = ''
    all_clock_getter_defines = ''
    
    for sdta in sdtas:
        all_location_defines += '\n//*** Locations for {}\n'.format(sdta.name)
        all_getter_defines += '\n//*** Getters for {}\n'.format(sdta.name)
        all_setter_defines += '\n//*** Setters for {}\n'.format(sdta.name)
        all_init_func_defines += '\n//*** Initialization function for {}\n'.format(sdta.name)
        all_inner_trans_func_defines += '\n//*** Inner transition function for {}\n'.format(sdta.name)
        all_trans_func_defines += '\n//*** Transition function for {}\n'.format(sdta.name)
        
        all_set_input_event_functions += '\n//*** Set input event function for {}\n'.format(sdta.name)
        all_set_output_event_functions += '\n//*** Set output event function for {}\n'.format(sdta.name) 
        all_clock_getter_defines += '\n//*** Clock getters for {}\n'.format(sdta.name)
               
        init_function, location_defines, getter_defines, setter_defines, clock_getter_defines = generate_initialization(sdta)
        
        all_location_defines += location_defines 
        all_getter_defines += getter_defines 
        all_setter_defines += setter_defines 
        all_clock_getter_defines += clock_getter_defines
        all_init_func_defines += init_function
        
        all_set_input_event_functions += generate_set_input_event(sdta)
        all_set_output_event_functions += generate_set_output_event(sdta)
        
        trans_func = generate_transition_function(sdta)
        trans_func_inner = generate_transition_function_inner(sdta)
        
        all_inner_trans_func_defines += trans_func_inner 
        all_trans_func_defines += trans_func 
        
    template = template.replace('**ENFORCER_LOCATION_DEFINES**', all_location_defines)
    template = template.replace('**ENFORCER_GETTER_DEFINES**', all_getter_defines)
    template = template.replace('**ENFORCER_SETTER_DEFINES**', all_setter_defines)
    template = template.replace('**ENFORCER_CLOCK_GETTER_DEFINES**', all_clock_getter_defines)
    template = template.replace('**ENFORCER_TRANS_FUNCTIONS**', all_trans_func_defines)
    template = template.replace('**ENFORCER_INNER_TRANS_FUNCTIONS**', all_inner_trans_func_defines)
    template = template.replace('**ENFORCER_INIT_FUNCTIONS**', all_init_func_defines)
    
    template = template.replace('**ENFORCER_SET_INPUT_EVENT_FUNCTIONS**', all_set_input_event_functions)
    template = template.replace('**ENFORCER_SET_OUTPUT_EVENT_FUNCTIONS**', all_set_output_event_functions)
    
    return template
    
    
def parse_args():
    parser = argparse.ArgumentParser(description='Generate enforceable properties in C using specification files based on DOT language.')
    parser.add_argument('output', help="the folder where all visualizations and generated code will be generated")
    parser.add_argument('--visualize', action='store_true', help='generate Graphviz outputs for all properties')
    parser.add_argument('source', metavar='S', type=str, nargs='+',
                       help='a DOT language source file containing a single property')
      
    parsed_args = parser.parse_args()
    return parsed_args
      
      
def main():
    parsed_args = parse_args()
    sdtas = read_all_sdtas(parsed_args.source)
    
    template_filename = '__sdta_template.c'
    output_filename = 'generated.c'
       
    template_lines = readfile(template_filename)
    generated_c = generate_c(sdtas, template_lines)
    
    if not os.path.exists(parsed_args.output):
        os.makedirs(parsed_args.output)
        
    writefile(parsed_args.output + '/generated.c', generated_c)
    if parsed_args.visualize:
        for sdta in sdtas: 
            src_graph = Source(''.join(sdta.source))
            output_location =  parsed_args.output + '/' + sdta.input_filename.strip('.gv')
            src_graph.render(output_location, view=False)  
    
    return
    
    
if __name__ == '__main__':
    main()
        
