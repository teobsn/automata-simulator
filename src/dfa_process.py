import parser
import re


def section_initialize(data, section_name):
    # Check for duplicate sections
    if section_name in data:
        raise ValueError(
            f"DFA Parser: Duplicate section '{section_name}' found in input file."
        )

    if section_name in ["alphabet", "states", "accept_states"]:
        data[section_name] = []
    elif section_name == "transitions":
        data[section_name] = {}
    elif section_name == "initial_state":
        data[section_name] = None
    elif section_name == "settings":
        data[section_name] = []
    else:
        raise ValueError(f"DFA Parser: Unknown section '{section_name}' in input file.")


def transition_add(data, source_state, input_symbol, next_state):
    if source_state not in data["transitions"]:
        data["transitions"][source_state] = {}

    if input_symbol == "*":
        for sym in data["alphabet"]:
            data["transitions"][source_state][sym] = next_state
    else:
        data["transitions"][source_state][input_symbol] = next_state


def transition_process_line(line):
    # Format is expected to be: current_state, input_symbol -> next_state
    for sep in ["->", ","]:
        if sep not in line:
            raise ValueError(f"DFA Parser: Invalid transition format in line: '{line}'")

    # Split the line into components
    combo, next_state = line.split("->")
    source_state, input_symbol = combo.split(",")

    # Strip whitespace from components
    source_state = source_state.strip()
    input_symbol = input_symbol.strip()
    next_state = next_state.strip()

    return source_state, input_symbol, next_state


def expand_range(token):
    # Example: q[0-15] -> q0, q1, ..., q15
    match = re.match(r"(.*)\[(\d+)-(\d+)\]", token)
    if match:
        prefix = match.group(1)
        start = int(match.group(2))
        end = int(match.group(3))
        return [f"{prefix}{i}" for i in range(start, end + 1)]
    return [token]


def process_data(input_data):
    """
    Processes the raw parsed data from the input file into a structured dictionary
    suitable for DFA simulation.
    """
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
                f"DFA Processor: Missing required section '{section}' in input file."
            )

    # Process each section in input data
    # Initialize each section in the output dictionary based on its expected type
    for section in parser.get_section_list(input_data):
        section_initialize(output_data, section)

    # Alphabet
    # Split space-separated symbols from each line and add to list
    for line in parser.get_section_from_data(input_data, "alphabet"):
        output_data["alphabet"].extend(line.split())

    # States and accept_states
    # Supports both literal state names and range syntax (e.g., q[0-15]).
    for section in ["states", "accept_states"]:
        for line in parser.get_section_from_data(input_data, section):
            tokens = line.split()
            for token in tokens:
                # Range syntax is expanded into individual state names using expand_range().
                output_data[section].extend(expand_range(token))

    # Initial state section should only have one entry, so we check if it is already set.
    for line in parser.get_section_from_data(input_data, "initial_state"):
        if "initial_state" in output_data and output_data["initial_state"]:
            raise ValueError(
                "DFA Processor: Multiple initial states found in input file."
            )
        output_data["initial_state"] = line

    # Transitions section can only have one entry per line
    # Each line is parsed to extract (source_state, symbol, next_state).
    # Supports '*' as a wildcard for the symbol, which creates transitions for 
    # all symbols in the alphabet.
    for line in parser.get_section_from_data(input_data, "transitions"):
        # Format line and extract components
        source_state, input_symbol, next_state = transition_process_line(line)

        # Add transition to data dictionary
        transition_add(output_data, source_state, input_symbol, next_state)

    # Settings section
    if "settings" in input_data:
        for line in parser.get_section_from_data(input_data, "settings"):
            output_data["settings"].extend(line.split())
    else:
        output_data["settings"] = []

    return output_data

