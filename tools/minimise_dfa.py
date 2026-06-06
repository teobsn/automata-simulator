#!/usr/bin/env python3

import argparse
from collections import deque

from shared.common import ensure_input_file, render_automaton_file, unique_preserve_order, write_text
from core import parser
from dfa import process as dfa_process


def transition_for_state(state, symbol, automaton, sink_state):
    transitions = automaton["transitions"]
    settings = automaton.get("settings", [])

    if state in transitions and symbol in transitions[state]:
        return transitions[state][symbol]

    if "RemainInCurrentStateOnUndefinedTransition" in settings:
        return state

    return sink_state


def build_total_transition_map(automaton):
    alphabet = unique_preserve_order(list(automaton["alphabet"]))
    states = unique_preserve_order(list(automaton["states"]))
    sink_state = "__sink__"

    needs_sink = False
    total_map = {}

    for state in states:
        total_map[state] = {}
        for symbol in alphabet:
            next_state = transition_for_state(state, symbol, automaton, sink_state)
            total_map[state][symbol] = next_state
            if next_state == sink_state:
                needs_sink = True

    if needs_sink:
        total_map[sink_state] = {symbol: sink_state for symbol in alphabet}
        states.append(sink_state)

    return states, total_map, sink_state if needs_sink else None


def reachable_states(initial_state, states, transitions, alphabet):
    seen = set()
    order = []
    queue = deque([initial_state])

    while queue:
        state = queue.popleft()
        if state in seen:
            continue

        seen.add(state)
        order.append(state)

        for symbol in alphabet:
            next_state = transitions[state][symbol]
            if next_state not in seen:
                queue.append(next_state)

    return order


def refine_partitions(states, accept_states, transitions, alphabet):
    partitions = []

    accepting = [state for state in states if state in accept_states]
    non_accepting = [state for state in states if state not in accept_states]

    if accepting:
        partitions.append(accepting)
    if non_accepting:
        partitions.append(non_accepting)

    while True:
        state_to_partition = {}
        for index, block in enumerate(partitions):
            for state in block:
                state_to_partition[state] = index

        refined = []
        changed = False

        for block in partitions:
            groups = {}
            for state in block:
                signature = tuple(
                    state_to_partition[transitions[state][symbol]] for symbol in alphabet
                )
                groups.setdefault(signature, []).append(state)

            if len(groups) == 1:
                refined.append(block)
                continue

            changed = True
            for signature in sorted(groups.keys()):
                refined.append(groups[signature])

        partitions = refined
        if not changed:
            break

    return partitions


def minimize(dfa_automaton):
    alphabet = unique_preserve_order(list(dfa_automaton["alphabet"]))
    states, transitions, _ = build_total_transition_map(dfa_automaton)

    reachable = reachable_states(
        dfa_automaton["initial_state"], states, transitions, alphabet
    )
    reachable_set = set(reachable)
    accept_states = unique_preserve_order(
        [state for state in dfa_automaton["accept_states"] if state in reachable_set]
    )

    reachable_transitions = {state: transitions[state] for state in reachable}
    partitions = refine_partitions(reachable, accept_states, reachable_transitions, alphabet)

    state_to_partition = {}
    for index, block in enumerate(partitions):
        for state in block:
            state_to_partition[state] = index

    minimized_states = [f"M{i}" for i in range(len(partitions))]
    minimized_transitions = {}
    minimized_accept_states = []
    comments = [
        "Minimized DFA generated from the input automaton.",
        "Partition mapping:",
    ]

    initial_partition = state_to_partition[dfa_automaton["initial_state"]]
    ordered_partition_indexes = [initial_partition] + [
        index for index in range(len(partitions)) if index != initial_partition
    ]

    partition_name = {}
    for new_index, partition_index in enumerate(ordered_partition_indexes):
        partition_name[partition_index] = f"M{new_index}"

    minimized_states = [partition_name[index] for index in ordered_partition_indexes]
    ordered_partitions = [partitions[index] for index in ordered_partition_indexes]

    for index, block in zip(ordered_partition_indexes, ordered_partitions):
        name = partition_name[index]
        members = ", ".join(sorted(block))
        comments.append(f"{name} = {{{members}}}")

        minimized_transitions[name] = {}
        representative = block[0]
        for symbol in alphabet:
            target_state = transitions[representative][symbol]
            target_partition = state_to_partition[target_state]
            minimized_transitions[name][symbol] = partition_name[target_partition]

        if any(state in dfa_automaton["accept_states"] for state in block):
            minimized_accept_states.append(name)

    minimized_accept_states = unique_preserve_order(minimized_accept_states)

    return {
        "alphabet": alphabet,
        "states": minimized_states,
        "initial_state": "M0",
        "accept_states": minimized_accept_states,
        "transitions": minimized_transitions,
        "settings": [],
    }, comments


def parse_args():
    parser = argparse.ArgumentParser(
        description="Minimize a DFA file and write the resulting automaton to disk."
    )
    parser.add_argument("input_file", help="Path to the DFA source file")
    parser.add_argument("output_file", help="Path to the minimized DFA file")
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_input_file(args.input_file)

    parsed = dfa_process.process_data(parser.parse(args.input_file))
    minimized, comments = minimize(parsed)

    rendered = render_automaton_file(
        minimized,
        comments=comments,
        as_nfa=False,
        transition_order=minimized["states"],
    )

    write_text(args.output_file, rendered)


if __name__ == "__main__":
    main()
