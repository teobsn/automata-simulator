import parser

def section_initialize(data, section_name):
    # Check for duplicate sections
    if section_name in data:
        raise ValueError(f"Parser: Duplicate section '{section_name}' found in input file.")

    if section_name in ['alphabet', 'states', 'accept_states']:
        data[section_name] = []
    elif section_name == 'transitions':
        data[section_name] = {}
    elif section_name == 'initial_state':
        data[section_name] = None
    else:
        raise ValueError(f"Parser: Unknown section '{section_name}' in input file.")

def transition_add(data, source_state, input_symbol, next_state):
    if source_state not in data['transitions']:
        data['transitions'][source_state] = {}

    data['transitions'][source_state][input_symbol] = next_state

def transition_process_line(line):
    # Format is expected to be: current_state, input_symbol -> next_state
    for sep in ['->', ',']:
        if sep not in line:
            raise ValueError(f"Parser: Invalid transition format in line: '{line}'")

    # Split the line into components
    combo, next_state = line.split('->')
    source_state, input_symbol = combo.split(',')
    
    # Strip whitespace from components
    source_state = source_state.strip()
    input_symbol = input_symbol.strip()
    next_state = next_state.strip()

    return source_state, input_symbol, next_state

def process_data(input_data):
    # Data dictionary
    output_data = {}

    # Check if data contains all required sections
    required_sections = ['alphabet', 'states', 'initial_state', 'accept_states', 'transitions']
    section_list = parser.get_section_list(input_data)
    for section in required_sections:
        if section not in section_list:
            raise ValueError(f"DFA Processor: Missing required section '{section}' in input file.")

    # Process each section in input data
    for section in input_data:
        # Initialize section in data dictionary
        section_initialize(output_data, section)

    # Alphabet and states sections can have multiple entries, so we split the data line into tokens and extend the list
    for section in ['alphabet', 'states', 'accept_states']:
        for line in input_data[section]:
            output_data[section].extend(line.split())

    # Initial state section should only have one entry, so we check if it is already set.
    for line in input_data['initial_state']:
        if 'initial_state' in output_data and output_data['initial_state']:
            raise ValueError("DFA Processor: Multiple initial states found in input file.")
        output_data['initial_state'] = line

    # Transitions section can only have one entry per line
    for line in input_data['transitions']:
        # Format line and extract components
        source_state, input_symbol, next_state = transition_process_line(line)

        # Add transition to data dictionary
        transition_add(output_data, source_state, input_symbol, next_state)

    return output_data