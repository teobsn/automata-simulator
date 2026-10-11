# Find next states from transitions map
def next_states(state, symbol, stack_top, transitions, settings=[]):
    """
    Looks up possible next states in the transitions table.
    """
    if state in transitions:
        if symbol in transitions[state]:
            if stack_top in transitions[state][symbol]:
                return transitions[state][symbol][stack_top]

    # Optional setting to handle cases where no transition is defined
    if "RemainInCurrentStateOnUndefinedTransition" in settings:
        return [(state, "&")] # Remain in state, push nothing

    return "Hang"

from collections import deque


def epsilon_transition_closure(state, stack, transitions, visited=None):
    """
    Finds all configurations (state, stack) reachable from the given configuration
    using only epsilon (&) transitions.
    """
    initial_config = (state, tuple(stack))
    closure = {initial_config}
    stack_list = [initial_config]

    while stack_list:
        curr_state, curr_st = stack_list.pop()
        if curr_state in transitions and '&' in transitions[curr_state]:
            top_sym = curr_st[-1] if curr_st else None
            pop_candidates = ('&', top_sym) if top_sym is not None else ('&',)
            for pop_sym in pop_candidates:
                if pop_sym in transitions[curr_state]['&']:
                    for next_st, push_str in transitions[curr_state]['&'][pop_sym]:
                        next_stack = list(curr_st)
                        if pop_sym != '&':
                            next_stack.pop()
                        if push_str != '&':
                            for s in reversed(push_str.split()):
                                next_stack.append(s)
                        next_cfg = (next_st, tuple(next_stack))
                        if next_cfg not in closure:
                            closure.add(next_cfg)
                            stack_list.append(next_cfg)

    return closure


def simulate(automaton, input_string, show_input=False):
    """
    Main entry point for PDA simulation.
    """
    # Initialize result dictionary
    results = {}

    # Validate input against the defined alphabet (excluding &)
    alphabet_set = set(automaton['alphabet_states'])
    for symbol in input_string:
        if symbol not in alphabet_set and symbol != '&':
            raise ValueError(f"Symbol '{symbol}' not in automaton alphabet.")

    # Store input string in results if required
    if show_input:
        results['input_string'] = input_string

    # Start the actual simulation logic
    results['accepted'] = simulate_start(automaton, input_string)

    return results


def simulate_start(automaton, input_string):
    """
    Simulates the PDA on input_string using iterative breadth-first search.
    """
    transitions = automaton['transitions']
    accept_states = set(automaton['accept_states'])
    input_len = len(input_string)

    queue = deque([(automaton['initial_state'], (), 0)])
    visited = {(automaton['initial_state'], (), 0)}

    while queue:
        state, stack, index = queue.popleft()

        # Find all configurations reachable by epsilon transitions
        eps_configs = epsilon_transition_closure(state, stack, transitions)

        # Base case - Check acceptance if we've reached the end of the input string
        if index == input_len:
            if any(s in accept_states for s, _ in eps_configs):
                return True
            continue

        symbol = input_string[index]

        for s, st in eps_configs:
            stack_top = st[-1] if st else None
            pop_options = ('&', stack_top) if stack_top is not None else ('&',)

            if s in transitions and symbol in transitions[s]:
                for pop_sym in pop_options:
                    if pop_sym in transitions[s][symbol]:
                        for next_st, push_str in transitions[s][symbol][pop_sym]:
                            new_stack = list(st)
                            if pop_sym != '&':
                                new_stack.pop()

                            if push_str != '&':
                                for sym in reversed(push_str.split()):
                                    new_stack.append(sym)

                            next_item = (next_st, tuple(new_stack), index + 1)
                            if next_item not in visited:
                                visited.add(next_item)
                                queue.append(next_item)

    return False

