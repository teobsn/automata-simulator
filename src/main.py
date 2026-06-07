#!/usr/bin/env python3

import sys
import os

# Add the current directory to sys.path to allow absolute imports of packages
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core modules
from core import parser, output, cli, runner

# Automaton type components mapping
import dfa.process as dfa_process, dfa.logic as dfa_logic, dfa.output as dfa_output
import nfa.process as nfa_process, nfa.logic as nfa_logic, nfa.output as nfa_output
import pda.process as pda_process, pda.logic as pda_logic, pda.output as pda_output
import cfg.process as cfg_process, cfg.logic as cfg_logic, cfg.output as cfg_output

HANDLERS = {
    "DFA": (dfa_process, dfa_logic, dfa_output),
    "NFA": (nfa_process, nfa_logic, nfa_output),
    "PDA": (pda_process, pda_logic, pda_output),
    "CFG": (cfg_process, cfg_logic, cfg_output),
}

def main():
    # Parse command-line arguments
    args = cli.parse_args(sys.argv[1:])
    automaton_type = args.automaton_type.upper()

    if automaton_type not in HANDLERS:
        supported = ", ".join(HANDLERS.keys())
        raise ValueError(f"Automaton type '{args.automaton_type}' not supported. Supported: {supported}")

    # Get respective modules for the selected type
    proc, logic, out_fmt = HANDLERS[automaton_type]

    # Parse the raw file data
    parsed_data = parser.parse(args.automaton_data)
    
    # Process data into structured format
    automaton_data = proc.process_data(parsed_data)

    # Handle Special Case: DFA Interactive Mode
    if automaton_type == "DFA" and args.interactive:
        logic.simulate_interactive(automaton_data)
        return

    # Handle Special Case: CFG Generation Mode
    if automaton_type == "CFG" and not args.verify:
        result = logic.generate(
            automaton_data,
            count=args.count,
            max_expansions=100 if args.cfg_max_expansions is None else args.cfg_max_expansions,
        )
        output.write_output(out_fmt.interpret_result(result), args.output_file)
        return

    # Standard Case: Simulation/Verification (Single or Batch)
    # This covers DFA (normal), NFA, PDA, and CFG (verify)
    extra_args = {}
    if automaton_type == "DFA":
        extra_args['write_intermediary'] = args.write_intermediary

    runner.run_simulation(
        logic.simulate, 
        out_fmt.interpret_result, 
        automaton_data, 
        args, 
        **extra_args
    )

if __name__ == "__main__":
    main()
