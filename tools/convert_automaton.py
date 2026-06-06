#!/usr/bin/env python3

import argparse
from collections import deque

from shared.common import (
    ensure_input_file,
    render_automaton_file,
    unique_preserve_order,
    write_text,
)
from core import parser
from nfa import process as nfa_process


def epsilon_closure(states, transitions):
    closure = set()
    stack = list(states)

    while stack:
        state = stack.pop()
        if state in closure:
            continue

        closure.add(state)

        for next_state in transitions.get(state, {}).get("&", []):
            if next_state not in closure:
                stack.append(next_state)

    return closure


def move(states, symbol, automaton):
    targets = set()
    transitions = automaton["transitions"]
    settings = automaton.get("settings", [])

    for state in states:
        symbol_targets = transitions.get(state, {}).get(symbol)

        if symbol_targets is None:
            if "RemainInCurrentStateOnUndefinedTransition" in settings:
                symbol_targets = [state]
            else:
                continue

        for next_state in symbol_targets:
            targets.add(next_state)

    return targets


def determinize(nfa_automaton):
    alphabet = unique_preserve_order(list(nfa_automaton["alphabet"]))
    transition_map = nfa_automaton["transitions"]
    initial_subset = frozenset(
        epsilon_closure({nfa_automaton["initial_state"]}, transition_map)
    )

    subset_to_name = {initial_subset: "D0"}
    subset_order = [initial_subset]
    queue = deque([initial_subset])
    transitions = {}
    accept_states = []

    while queue:
        subset = queue.popleft()
        state_name = subset_to_name[subset]
        transitions[state_name] = {}

        if any(state in nfa_automaton["accept_states"] for state in subset):
            accept_states.append(state_name)

        for symbol in alphabet:
            next_subset = frozenset(
                epsilon_closure(move(subset, symbol, nfa_automaton), transition_map)
            )

            if next_subset not in subset_to_name:
                subset_to_name[next_subset] = f"D{len(subset_to_name)}"
                subset_order.append(next_subset)
                queue.append(next_subset)

            transitions[state_name][symbol] = subset_to_name[next_subset]

    states = [subset_to_name[subset] for subset in subset_order]
    accept_states = unique_preserve_order(accept_states)

    comments = [
        "Determinized DFA generated from the input automaton.",
        "Subset mapping:",
    ]
    for subset in subset_order:
        name = subset_to_name[subset]
        members = ", ".join(sorted(subset))
        comments.append(f"{name} = {{{members}}}")

    return {
        "alphabet": alphabet,
        "states": states,
        "initial_state": "D0",
        "accept_states": accept_states,
        "transitions": transitions,
        "settings": [],
    }, comments


def reserialize_as_nfa(nfa_automaton):
    comments = [
        "Automaton rewritten in NFA-compatible ASL format.",
        "DFA transitions remain valid because each transition target is written as a singleton list.",
    ]

    return {
        "alphabet": unique_preserve_order(list(nfa_automaton["alphabet"])),
        "states": list(unique_preserve_order(nfa_automaton["states"])),
        "initial_state": nfa_automaton["initial_state"],
        "accept_states": list(unique_preserve_order(nfa_automaton["accept_states"])),
        "transitions": nfa_automaton["transitions"],
        "settings": list(nfa_automaton.get("settings", [])),
    }, comments


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert an automaton file between DFA and NFA representations."
    )
    parser.add_argument("input_file", help="Path to the source automaton file")
    parser.add_argument("output_file", help="Path to the generated automaton file")
    parser.add_argument(
        "--to",
        choices=["dfa", "nfa"],
        default="dfa",
        help="Target automaton representation",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_input_file(args.input_file)

    parsed = nfa_process.process_data(parser.parse(args.input_file))

    if args.to == "dfa":
        automaton, comments = determinize(parsed)
        rendered = render_automaton_file(
            automaton,
            comments=comments,
            as_nfa=False,
            transition_order=automaton["states"],
        )
    else:
        automaton, comments = reserialize_as_nfa(parsed)
        rendered = render_automaton_file(
            automaton,
            comments=comments,
            as_nfa=True,
            transition_order=automaton["states"],
        )

    write_text(args.output_file, rendered)


if __name__ == "__main__":
    main()
