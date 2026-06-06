#!/usr/bin/env python3

import argparse

from shared.common import ensure_input_file
from shared.visualization import (
    build_fa_dot,
    build_pda_dot,
    open_preview,
    render_svg,
)
from core import parser
from dfa import process as dfa_process
from nfa import process as nfa_process
from pda import process as pda_process


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description="Render an academic visualization for a DFA, NFA, or PDA."
    )
    arg_parser.add_argument("input_file", help="Path to the automaton or grammar file")
    arg_parser.add_argument(
        "automaton_type",
        choices=["DFA", "dfa", "NFA", "nfa", "PDA", "pda"],
        help="Type of structure to visualize",
    )
    arg_parser.add_argument(
        "--no-open",
        action="store_true",
        help="Render the SVG preview without opening it automatically",
    )
    return arg_parser.parse_args()


def main():
    args = parse_args()
    ensure_input_file(args.input_file)

    parsed_data = parser.parse(args.input_file)
    automaton_type = args.automaton_type.lower()

    if automaton_type == "dfa":
        automaton = dfa_process.process_data(parsed_data)
        dot = build_fa_dot(automaton, "dfa")
    elif automaton_type == "nfa":
        automaton = nfa_process.process_data(parsed_data)
        dot = build_fa_dot(automaton, "nfa")
    elif automaton_type == "pda":
        automaton = pda_process.process_data(parsed_data)
        dot = build_pda_dot(automaton)
    else:
        raise ValueError(f"Unsupported automaton type: {args.automaton_type}")

    svg_path = render_svg(dot)
    if not args.no_open:
        open_preview(svg_path)
    else:
        print(svg_path)


if __name__ == "__main__":
    main()
