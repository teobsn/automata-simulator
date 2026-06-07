from core import parser
import re


def section_initialize(data, section_name):
    # Check for duplicate sections
    if section_name in data:
        raise ValueError(
            f"PDA Parser: Duplicate section '{section_name}' found in input file."
        )

    if section_name in ["alphabet_states", "alphabet_stack", "states", "accept_states"]:
        data[section_name] = []
    elif section_name == "transitions":
        data[section_name] = {}
    elif section_name == "initial_state":
        data[section_name] = None
    elif section_name == "settings":
        data[section_name] = []
    else:
        raise ValueError(f"PDA Parser: Unknown section '{section_name}' in input file.")


def transition_add(data, source_state, input_symbols, stack_pop, next_state, stack_push):
    if source_state not in data["transitions"]:
        data["transitions"][source_state] = {}

    for input_symbol in input_symbols:
        if input_symbol not in data["transitions"][source_state]:
            data["transitions"][source_state][input_symbol] = {}

        if stack_pop not in data["transitions"][source_state][input_symbol]:
            data["transitions"][source_state][input_symbol][stack_pop] = []

        data["transitions"][source_state][input_symbol][stack_pop].append((next_state, stack_push))


def transition_process_line(line):
    # Format: source_state, input_symbol, stack_pop -> next_state, stack_push
    # Epsilon: &

    if "->" not in line:
        raise ValueError(f"PDA Parser: Invalid transition format in line: '{line}'")

    left, right = line.split("->")

    left_parts = [p.strip() for p in left.split(",")]
    if len(left_parts) != 3:
        raise ValueError(f"PDA Parser: Invalid transition left side: '{left}'")

    source_state, input_symbol_text, stack_pop = left_parts

    right_parts = [p.strip() for p in right.split(",")]
    if len(right_parts) != 2:
        raise ValueError(f"PDA Parser: Invalid transition right side: '{right}'")

    next_state, stack_push = right_parts

    # Process input symbols (could be a single symbol or a list in parentheses)
    if input_symbol_text.startswith("(") and input_symbol_text.endswith(")"):
        input_symbols = [s.strip() for s in input_symbol_text[1:-1].split(",")]
    else:
        input_symbols = [input_symbol_text]

    return source_state, input_symbols, stack_pop, next_state, stack_push


def expand_range(token):
    # Example: q[0-15] -> q0, q1, ..., q15
    match = re.match(r"(.*)\[(\d+)-(\d+)\]", token)
    if match:
        prefix = match.group(1)
        start = int(match.group(2))
        end = int(match.group(3))
        return [f"{prefix}{i}" for i in range(start, end + 1)]
    return [token]


def validate_structure(output_data):
    declared_states = set(output_data["states"])
    input_alphabet = set(output_data["alphabet_states"])
    stack_alphabet = set(output_data["alphabet_stack"])

    if output_data["initial_state"] not in declared_states:
        raise ValueError(
            f"PDA Processor: Initial state '{output_data['initial_state']}' is not declared in [states]."
        )

    undefined_accept_states = [state for state in output_data["accept_states"] if state not in declared_states]
    if undefined_accept_states:
        raise ValueError(
            "PDA Processor: Accept state(s) not declared in [states]: "
            + ", ".join(undefined_accept_states)
        )

    for source_state, by_symbol in output_data["transitions"].items():
        if source_state not in declared_states:
            raise ValueError(
                f"PDA Processor: Transition source state '{source_state}' is not declared in [states]."
            )

        for input_symbol, by_stack in by_symbol.items():
            if input_symbol != "&" and input_symbol not in input_alphabet:
                raise ValueError(
                    f"PDA Processor: Transition input symbol '{input_symbol}' is not declared in [alphabet_states]."
                )

            for stack_pop, transitions in by_stack.items():
                if stack_pop != "&" and stack_pop not in stack_alphabet:
                    raise ValueError(
                        f"PDA Processor: Transition stack symbol '{stack_pop}' is not declared in [alphabet_stack]."
                    )

                for next_state, stack_push in transitions:
                    if next_state not in declared_states:
                        raise ValueError(
                            f"PDA Processor: Transition target state '{next_state}' is not declared in [states]."
                        )
                    if stack_push != "&":
                        for symbol in stack_push.split():
                            if symbol not in stack_alphabet:
                                raise ValueError(
                                    f"PDA Processor: Transition stack push symbol '{symbol}' is not declared in [alphabet_stack]."
                                )


def process_data(input_data):
    """
    Processes the raw parsed data from the input file into a structured dictionary
    suitable for PDA simulation.
    """

    # Data dictionary
    output_data = {}

    # Check if data contains all required sections
    required_sections = [
        "alphabet_states",
        "alphabet_stack",
        "states",
        "initial_state",
        "accept_states",
        "transitions",
    ]
    section_list = parser.get_section_list(input_data)
    for section in required_sections:
        if section not in section_list:
            raise ValueError(
                f"PDA Processor: Missing required section '{section}' in input file."
            )

    # Process each section in input data
    for section in parser.get_section_list(input_data):
        section_initialize(output_data, section)

    # Alphabets
    for alphabet_type in ["alphabet_states", "alphabet_stack"]:
        for line in parser.get_section_from_data(input_data, alphabet_type):
            output_data[alphabet_type].extend(line.split())


    # States and accept_states
    for section in ["states", "accept_states"]:
        for line in parser.get_section_from_data(input_data, section):
            tokens = line.split()
            for token in tokens:
                output_data[section].extend(expand_range(token))

    # Initial state
    for line in parser.get_section_from_data(input_data, "initial_state"):
        if output_data.get("initial_state"):
            raise ValueError(
                "PDA Processor: Multiple initial states found in input file."
            )
        output_data["initial_state"] = line.strip()

    # Transitions
    for line in parser.get_section_from_data(input_data, "transitions"):
        source_state, input_symbols, stack_pop, next_state, stack_push = transition_process_line(line)

        if source_state not in output_data["states"]:
            raise ValueError(
                f"PDA Processor: Transition source state '{source_state}' is not declared in [states]."
            )
        for input_symbol in input_symbols:
            if input_symbol != "&" and input_symbol not in output_data["alphabet_states"]:
                raise ValueError(
                    f"PDA Processor: Transition input symbol '{input_symbol}' is not declared in [alphabet_states]."
                )
        if stack_pop != "&" and stack_pop not in output_data["alphabet_stack"]:
            raise ValueError(
                f"PDA Processor: Transition stack symbol '{stack_pop}' is not declared in [alphabet_stack]."
            )
        if next_state not in output_data["states"]:
            raise ValueError(
                f"PDA Processor: Transition target state '{next_state}' is not declared in [states]."
            )
        if stack_push != "&":
            for symbol in stack_push.split():
                if symbol not in output_data["alphabet_stack"]:
                    raise ValueError(
                        f"PDA Processor: Transition stack push symbol '{symbol}' is not declared in [alphabet_stack]."
                    )

        transition_add(output_data, source_state, input_symbols, stack_pop, next_state, stack_push)

    # Settings
    if "settings" in input_data:
        for line in parser.get_section_from_data(input_data, "settings"):
            output_data["settings"].extend(line.split())
    else:
        output_data["settings"] = []

    validate_structure(output_data)

    return output_data

