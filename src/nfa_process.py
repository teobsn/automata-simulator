import parser
import re


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

    expanded_symbols = []
    for symbol in input_symbols:
        if symbol == "*":
            expanded_symbols.extend(data["alphabet"])
        else:
            expanded_symbols.append(symbol)

    for input_symbol in expanded_symbols:
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
    suitable for NFA simulation.
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
                f"NFA Processor: Missing required section '{section}' in input file."
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
    # Ensure only one start state is defined
    for line in parser.get_section_from_data(input_data, "initial_state"):
        if "initial_state" in output_data and output_data["initial_state"]:
            raise ValueError(
                "NFA Processor: Multiple initial states found in input file."
            )
        output_data["initial_state"] = line

    # Transitions section can only have one entry per line
    # Each line is parsed to extract (source_state, symbols, next_states).
    # Supports '*' as a wildcard in the symbol list, expanding to all alphabet symbols.
    for line in parser.get_section_from_data(input_data, "transitions"):
        source_state, input_symbols, next_states = transition_process_line(line)
        transition_add(output_data, source_state, input_symbols, next_states)

    return output_data

