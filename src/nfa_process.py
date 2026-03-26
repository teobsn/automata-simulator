import parser


def section_initialize(data, section_name):
    # Check for duplicate sections
    if section_name in data:
        raise ValueError(
            f"Parser: Duplicate section '{section_name}' found in input file."
        )

    if section_name in ["alphabet", "states", "accept_states"]:
        data[section_name] = []
    elif section_name == "transitions":
        data[section_name] = {}
    elif section_name == "initial_state":
        data[section_name] = None
    else:
        raise ValueError(f"Parser: Unknown section '{section_name}' in input file.")


def transition_add(data, source_state, input_symbols, next_states):
    if source_state not in data["transitions"]:
        data["transitions"][source_state] = {}

    for input_symbol in input_symbols:
        data["transitions"][source_state][input_symbol] = data["transitions"][source_state].get(input_symbol, []) + next_states


def transition_process_line(line):
    # Format is expected to be one of: 
    # current_state, input_symbol -> next_state
    # current_state, (input_symbol1, input_symbol2, ...) -> next_state
    # current_state, ipnut_symbol -> next_states

    for sep in ["->"]:
        if sep not in line:
            raise ValueError(f"Parser: Invalid transition format in line: '{line}'")

    # Split the line into components
    combo, next_states_text = line.split("->")

    split_combo = combo.split(",", 1)
    source_state = split_combo[0]
    input_symbols_text = split_combo[1]

    # Strip whitespace from components
    source_state = source_state.strip()
    input_symbols_text = input_symbols_text.strip()
    next_states_text = next_states_text.strip()

    # Process input symbols
    if input_symbols_text.startswith("(") and input_symbols_text.endswith(")"):
        input_symbols = [s.strip() for s in input_symbols_text[1:-1].split(",")]
    else:
        input_symbols = [input_symbols_text]

    # Process next states
    next_states = [s.strip() for s in next_states_text.split(",")]

    return source_state, input_symbols, next_states


def process_data(input_data):
    # Data dictionary
    output_data = {}

    # Check if data contains all required sections
    required_sections = [
        "alphabet",
        "states",
        "initial_state",
        "accept_states",
        "transitions",
    ]
    section_list = parser.get_section_list(input_data)
    for section in required_sections:
        if section not in section_list:
            raise ValueError(
                f"NFA Processor: Missing required section '{section}' in input file."
            )

    # Process each section in input data
    for section in parser.get_section_list(input_data):
        # Initialize section in data dictionary
        section_initialize(output_data, section)

    # Alphabet and states sections can have multiple entries, so we split the data line into tokens and extend the list
    for section in ["alphabet", "states", "accept_states"]:
        for line in parser.get_section_from_data(input_data, section):
            output_data[section].extend(line.split())

    # Initial state section should only have one entry, so we check if it is already set.
    for line in parser.get_section_from_data(input_data, "initial_state"):
        if "initial_state" in output_data and output_data["initial_state"]:
            raise ValueError(
                "NFA Processor: Multiple initial states found in input file."
            )
        output_data["initial_state"] = line

    # Transitions section can only have one entry per line
    for line in parser.get_section_from_data(input_data, "transitions"):
        # Format line and extract components
        source_state, input_symbols, next_states = transition_process_line(line)

        # Add transition to data dictionary
        transition_add(output_data, source_state, input_symbols, next_states)

    return output_data

