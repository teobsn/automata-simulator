def check_path(path):
    import os
    if not os.path.isfile(path):
        raise ValueError(f"File '{path}' does not exist.")
    return path

def parse_args(args):
    import argparse

    parser = argparse.ArgumentParser(description="Simulate a finite automaton based on input data.")
    parser.add_argument('automaton_type',   type=str,                             help='Type of automaton to simulate. Currently only "DFA" is supported')
    parser.add_argument('automaton_data',   type=check_path,                      help='Path to the automaton data file')
    parser.add_argument('input_string',     type=str, nargs='?', default=None,    help='Input string to process with the automaton')
    
    parser.add_argument('--output-file',        nargs='?', default=None,          help='Optional output file to write results to')
    parser.add_argument('--write-intermediary', action='store_true',              help='Write intermediary states to the output')
    parser.add_argument('--input-list-file',    type=check_path,                  help='Path to the file containing the list of inputs')

    parsed_args = parser.parse_args(args)

    # Universal (regardless of automaton type) argument checks
    if parsed_args.input_string is None and parsed_args.input_list_file is None:
        parser.error("At least one of 'input_string' or '--input-list-file' must be provided.")

    return parsed_args