def check_path(path):
    import os
    if not os.path.isfile(path):
        raise ValueError(f"File '{path}' does not exist.")
    return path

def parse_args(args):
    import argparse

    parser = argparse.ArgumentParser(description="Simulate a finite automaton based on input data.")
    parser.add_argument('automata_data', type=check_path, help='Path to the automaton data file')
    parser.add_argument('input_string', type=str, help='Input string to process with the automaton')
    parser.add_argument('output_file', nargs='?', default=None, help='Optional output file to write results to')

    parser.add_argument('--write-intermediary', action='store_true', help='Write intermediary states to the output')


    return parser.parse_args(args)