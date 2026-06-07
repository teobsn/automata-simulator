def check_path(path):
    import os
    if not os.path.isfile(path):
        raise ValueError(f"File '{path}' does not exist.")
    return path

def parse_args(args):
    import argparse

    parser = argparse.ArgumentParser(description="Simulate a finite automaton or grammar based on input data.")
    parser.add_argument('automaton_type',   type=str,                             help='Type of model (DFA, NFA, PDA, CFG)')
    parser.add_argument('automaton_data',   type=check_path,                      help='Path to the definition file')
    parser.add_argument('input_string',     type=str, nargs='?', default=None,    help='Input string to process (optional for CFG generation)')
    
    parser.add_argument('--output-file',        nargs='?', default=None,          help='Optional output file to write results to')
    parser.add_argument('--write-intermediary', action='store_true',              help='Write intermediary states to the output (DFA only)')
    parser.add_argument('--input-list-file',    type=check_path,                  help='Path to the file containing the list of inputs')
    parser.add_argument('-i', '--interactive',  action='store_true',              help='Enable interactive mode for input symbols')
    parser.add_argument('--verify',             action='store_true',              help='Verify if input_string belongs to the CFG')
    parser.add_argument('--count',              type=int, default=1,              help='Number of strings to generate (for CFG default mode)')
    parser.add_argument('--cfg-max-expansions', type=int, default=None,          help='Maximum expansion steps per generated CFG derivation; use 0 to disable the safety limit.')

    parsed_args = parser.parse_args(args)

    # Context-aware validation
    is_cfg_generation = parsed_args.automaton_type.upper() == 'CFG' and not parsed_args.verify

    # Universal argument checks
    if not is_cfg_generation and not parsed_args.interactive and parsed_args.input_string is None and parsed_args.input_list_file is None:
        parser.error("At least one of 'input_string', '--input-list-file', or '--interactive' must be provided.")

    if parsed_args.write_intermediary and parsed_args.automaton_type.upper() != 'DFA':
        parser.error("--write-intermediary is only supported for DFA.")

    if parsed_args.cfg_max_expansions is not None and not is_cfg_generation:
        parser.error("--cfg-max-expansions is only supported for CFG generation mode.")

    return parsed_args
