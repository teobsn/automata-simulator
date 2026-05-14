#!/usr/bin/env python3


# Standard libraries
# import os
# from pprint import pprint
import sys

# Project modules
import parser

# DFA
import dfa_process
import dfa_logic
import dfa_output

# NFA
import nfa_process
import nfa_logic
import nfa_output

# PDA
import pda_process
import pda_logic
import pda_output

import output
import cli


def main():
    # Parse command-line arguments
    args = cli.parse_args(sys.argv[1:])

    # Parse the file to get the automaton data
    parsed_data = parser.parse(args.automaton_data)

    if args.automaton_type in ["DFA", "dfa"]:
        # Process the parsed file into proper data
        output_data = dfa_process.process_data(parsed_data)

        if args.interactive:
            dfa_logic.simulate_interactive(output_data)
            return

        if not args.input_list_file:
        # Simulate the automaton with the input string
            result = dfa_logic.simulate(
                output_data, args.input_string, write_intermediary=args.write_intermediary
            )

            # Write the result to the output file or print it
            output.write_output(dfa_output.interpret_result(result), args.output_file)
        else:
            with open(args.input_list_file, "r") as f:
                input_list = f.read().splitlines()

            # Create a blank file first, as we are going to append to it 
            if args.output_file is not None:
                output.blank_file(args.output_file)

            for input_str in input_list:
                result = dfa_logic.simulate(
                    output_data, input_str, write_intermediary=args.write_intermediary, show_input=True
                )

                output.write_output(
                    dfa_output.interpret_result(result), args.output_file, append=True
                )
    elif args.automaton_type in ["NFA", "nfa"]:
        output_data = nfa_process.process_data(parsed_data)

        if not args.input_list_file:
            result = nfa_logic.simulate(
                output_data, args.input_string, write_intermediary=args.write_intermediary
            )

            # Write the result to the output file or print it
            output.write_output(nfa_output.interpret_result(result), args.output_file)
        else:
            with open(args.input_list_file, "r") as f:
                input_list = f.read().splitlines()

            # Create a blank file first, as we are going to append to it 
            if args.output_file is not None:
                output.blank_file(args.output_file)

            for input_str in input_list:
                result = nfa_logic.simulate(
                    output_data, input_str, write_intermediary=args.write_intermediary, show_input=True
                )
                output.write_output(
                    nfa_output.interpret_result(result), args.output_file, append=True
                )
    elif args.automaton_type in ["PDA", "pda"]:
        output_data = pda_process.process_data(parsed_data)

        if not args.input_list_file:
            result = pda_logic.simulate(
                output_data, args.input_string, write_intermediary=args.write_intermediary
            )

            output.write_output(pda_output.interpret_result(result), args.output_file)
        else:
            with open(args.input_list_file, "r") as f:
                input_list = f.read().splitlines()

            if args.output_file is not None:
                output.blank_file(args.output_file)

            for input_str in input_list:
                result = pda_logic.simulate(
                    output_data, input_str, write_intermediary=args.write_intermediary, show_input=True
                )
                output.write_output(
                    pda_output.interpret_result(result), args.output_file, append=True
                )
    else:
        raise ValueError(
            f"Automaton type '{args.automaton_type}' is not supported. Currently only 'DFA', 'NFA' and 'PDA' are supported."
        )


if __name__ == "__main__":
    main()

