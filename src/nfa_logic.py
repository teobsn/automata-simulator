# Find next state from transitions map
def next_states(state, symbol, transitions, settings=[]):
    if state in transitions:
        if symbol in transitions[state]:
            return transitions[state][symbol]

    if "RemainInCurrentStateOnUndefinedTransition" in settings:
        return [state]

    return "Hang"

def simulate(automaton, input_string, write_intermediary=False, show_input=False):
    # Initialize result data
    results = {}

    # Check alphabet
    for symbol in input_string:
        if symbol not in automaton['alphabet']:
            raise ValueError(f"Symbol '{symbol}' not in automaton alphabet.")

    # Add the input string to the result 
    if show_input:
        results['input_string'] = input_string

    # Initialize the steps list if we want to write intermediary steps (to-do)
    # if write_intermediary:
        # results["steps"] = [current_state]

    results['branch'] = simulate_start(automaton, input_string, write_intermediary)

    return results

def simulate_start(automaton, input_string, write_intermediary=False):
    # Initialize the current state to the start state
    current_state = automaton['initial_state']

    branch = simulate_next(automaton, current_state, input_string, 0, write_intermediary)

    return branch

def simulate_next(automaton, state, input_string, index, write_intermediary):
    import concurrent.futures

    # Base case: if we've reached the end of the input string
    if index == len(input_string):
        return state in automaton['accept_states']

    symbol = input_string[index]
    next_state_list = next_states(state, symbol, automaton['transitions'], automaton.get('settings', []))

    # Transmit hang
    if next_state_list == "Hang":
        return False

    # Use a ThreadPoolExecutor to manage threads efficiently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map each next state to a future task
        futures = [
            executor.submit(simulate_next, automaton, next_st, input_string, index + 1, write_intermediary)
            for next_st in next_state_list
        ]

        # As each thread completes, check the result
        for future in concurrent.futures.as_completed(futures):
            if future.result() is True:
                # If one branch succeeds, we can stop and return True
                # Note: Other threads will continue until the executor context closes
                return True

    return False

def simulate_next_sequential(automaton, state, input_string, index, write_intermediary):
    symbol = input_string[index]

    next_state_list = next_states(state, symbol, automaton['transitions'], automaton.get('settings', []))

    # Transmit hang
    if next_state_list == "Hang":
        return "Hang"
    
    # This branch is taken if we are at the last symbol/char of the input string
    if index == len(input_string) - 1:
        for state in next_state_list:
            if state in automaton['accept_states']:
                return True
        return False

    # Recursively call every next state
    for state in next_state_list:
        result = simulate_next(automaton, state, input_string, index + 1, write_intermediary)
        if result == True:
            return True
    
    # If we get to this point, it means no "future" branch was accepted, so this
    # is not accepted either
    return False