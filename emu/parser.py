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



def parse(input_file):
    # Data dictionary
    data = {}

    # Open file
    f = open(input_file, 'r')

    current_section = None


    for line in f:
        line = line.strip()

        # Skip comments
        line = line.split('#')[0].strip()

        # Skip empty lines
        if not line:
            continue

        # Check for section headers
        if line.startswith('[') and line.endswith(']'):
            # Extract section name
            current_section = line[1:-1].strip()
            
            # Initialize section in data dictionary
            section_initialize(data, current_section)

        else:
            # Check if the data line is within a section
            if not current_section:
                raise ValueError("Parser: Data line found outside of any section.")


            ### Process line based on current section

            # Alphabet and states sections can have multiple entries, so we split the line into tokens and extend the list
            if current_section in ['alphabet', 'states', 'accept_states']:
                data[current_section].extend(line.split())

            # Initial state section should only have one entry, so we check if it is already set.
            elif current_section == 'initial_state':
                if 'initial_state' in data and data['initial_state']:
                    raise ValueError("Parser: Multiple initial states found in input file.")
                data[current_section] = line

            # Transitions section can only have one entry per line
            elif current_section == 'transitions':
                # Format line and extract components
                source_state, input_symbol, next_state = transition_process_line(line)

                # Add transition to data dictionary
                transition_add(data, source_state, input_symbol, next_state)
    
    # Check if data contains all required sections
    required_sections = ['alphabet', 'states', 'initial_state', 'accept_states', 'transitions']
    for section in required_sections:
        if section not in data:
            raise ValueError(f"Parser: Missing required section '{section}' in input file.")

    # Close file
    f.close()

    return data