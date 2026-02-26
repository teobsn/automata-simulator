#!/usr/bin/env python3


# Standard libraries
import os
from pprint import pprint
import sys

# Project modules
import parser
import logic
import output
import cli

def main():
    # Parse command-line arguments
    args = cli.parse_args(sys.argv[1:])
    
    input_file = args.automata_data
    input_string = args.input_string
    output_file = args.output_file

    # Parse the file to get the automaton data
    parsed_data = parser.parse(input_file)

    # Simulate the automaton with the input string
    result = logic.simulate(parsed_data, input_string, args.write_intermediary)

    # Write the result to the output file or print it
    output.write_output(output.interpret_result(result), output_file)

if __name__ == "__main__":
    main()