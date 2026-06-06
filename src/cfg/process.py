from core import parser
import re

def section_initialize(data, section_name):
    """
    Initializes a specific section within the internal grammar data structure.
    Checks for duplicates to ensure consistent data integrity.
    """
    if section_name in data:
        raise ValueError(
            f"CFG Parser: Duplicate section '{section_name}' detected."
        )

    if section_name in ["variables", "terminals"]:
        data[section_name] = []
    elif section_name == "rules":
        data[section_name] = {}
    elif section_name == "start_variable":
        data[section_name] = None
    else:
        raise ValueError(f"CFG Parser: Unexpected section '{section_name}' encountered.")

def rule_add(data, variable, expansion):
    """
    Appends a new derivation rule to the internal rule mapping.
    Validates that the non-terminal variable has been properly defined.
    """
    if variable not in data["variables"]:
        raise ValueError(f"CFG Parser: Non-terminal '{variable}' is used in a rule but not defined in [variables].")
    
    if variable not in data["rules"]:
        data["rules"][variable] = []
    
    # Tokenize the expansion string; white-space is used as the standard delimiter
    symbols = expansion.split()
    if symbols not in data["rules"][variable]:
        data["rules"][variable].append(symbols)

def rule_process_line(line):
    """
    Parses a single production line which may contain multiple expansions.
    Format expected: V -> expansion1 | expansion2 | ...
    """
    if "->" not in line:
        raise ValueError(f"CFG Parser: Incorrect rule syntax in line: '{line}'")

    variable, right_side = line.split("->")
    variable = variable.strip()
    
    # Split by the alternative operator '|' and strip whitespace from each resulting expansion
    expansions = [e.strip() for e in right_side.split("|")]
    
    return variable, expansions

def process_data(input_data):
    """
    Processes the raw parsed section data into a structured grammar dictionary.
    Performs validation on required sections and start variable definitions.
    """
    output_data = {}

    # Define the set of sections strictly required for a valid CFG definition
    required_sections = [
        "variables",
        "terminals",
        "start_variable",
        "rules",
    ]
    
    section_list = parser.get_section_list(input_data)
    for section in required_sections:
        if section not in section_list:
            raise ValueError(
                f"CFG Processor: Missing mandatory section '{section}'."
            )

    # Initialize each found section in the output structure
    for section in section_list:
        section_initialize(output_data, section)

    # Extract non-terminal variables
    for line in parser.get_section_from_data(input_data, "variables"):
        output_data["variables"].extend(line.split())

    # Extract terminal symbols
    for line in parser.get_section_from_data(input_data, "terminals"):
        output_data["terminals"].extend(line.split())

    # Resolve and validate the start variable definition
    for line in parser.get_section_from_data(input_data, "start_variable"):
        if output_data.get("start_variable"):
            raise ValueError("CFG Processor: Only one start variable is permitted.")
        
        start_var = line.strip()
        if start_var not in output_data["variables"]:
            raise ValueError(f"CFG Processor: Start variable '{start_var}' not found in variable list.")
        
        output_data["start_variable"] = start_var

    # Parse and register all production rules
    for line in parser.get_section_from_data(input_data, "rules"):
        variable, expansions = rule_process_line(line)
        for expansion in expansions:
            rule_add(output_data, variable, expansion)

    return output_data
