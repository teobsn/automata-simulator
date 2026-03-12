#!/usr/bin/env python3


# Standard libraries
import os
from pprint import pprint
import sys

# Project modules
import parser
import dfa_process
import dfa_logic
import output
import cli

def main():
    # Parse command-line arguments
    args = cli.parse_args(sys.argv[1:])

    # Parse the file to get the automaton data
    parsed_data = parser.parse(args.automaton_data)

    # Simulate the automaton with the input string
    if args.automaton_type in ['DFA', 'dfa']:
        output_data = dfa_process.process_data(parsed_data)

        if not args.input_list_file:
            result = dfa_logic.simulate(output_data, args.input_string, args.write_intermediary)

            # Write the result to the output file or print it
            output.write_output(output.interpret_result(result), args.output_file)
        else:
            with open(args.input_list_file, 'r') as f:
                input_list = f.read().splitlines()

            for input_str in input_list:
                result = dfa_logic.simulate(output_data, input_str, args.write_intermediary)
                output.write_output(output.interpret_result(result), args.output_file, append=True)
    else:
        raise ValueError(f"Automaton type '{args.automaton_type}' is not supported. Currently only 'DFA' is supported.")


if __name__ == "__main__":
    main()