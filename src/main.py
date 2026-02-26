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

    # Parse the file to get the automaton data
    parsed_data = parser.parse(args.automata_data)

    # Simulate the automaton with the input string
    result = logic.simulate(parsed_data, args.input_string, args.write_intermediary)

    # Write the result to the output file or print it
    output.write_output(output.interpret_result(result), args.output_file)

if __name__ == "__main__":
    main()