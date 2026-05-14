# Find next states from transitions map
def next_states(state, symbol, transitions, settings=[]):
    if state in transitions:
        if symbol in transitions[state]:
            return transitions[state][symbol]

    if "RemainInCurrentStateOnUndefinedTransition" in settings:
        return [state]

    return "Hang"

def epsilon_transition_closure(state, transitions, visited=None):
    """
    Finds all states reachable from the given state using only epsilon (&) transitions.
    """
    if visited is None:
        visited = set()
    
    if state in visited:
        return set()
    
    visited.add(state)
    closure = {state}
    
    if state in transitions and '&' in transitions[state]:
        for next_st in transitions[state]['&']:
            closure.update(epsilon_transition_closure(next_st, transitions, visited))
            
    return closure

def simulate(automaton, input_string, write_intermediary=False, show_input=False):
    # Initialize result data
    results = {}

    # Check alphabet
    for symbol in input_string:
        if symbol not in automaton['alphabet'] and symbol != '&':
            raise ValueError(f"Symbol '{symbol}' not in automaton alphabet.")

    # Add the input string to the result 
    if show_input:
        results['input_string'] = input_string

    # Start simulation
    results['branch'] = simulate_start(automaton, input_string, write_intermediary)

    return results

def simulate_start(automaton, input_string, write_intermediary=False):
    # Initialize the current state to the start state
    current_state = automaton['initial_state']

    # Start recursive simulation
    branch = simulate_next(automaton, current_state, input_string, 0, write_intermediary)

    return branch

def simulate_next(automaton, state, input_string, index, write_intermediary):
    import concurrent.futures

    # At any point, we can take epsilon transitions (&)
    # To avoid infinite loops, we only check epsilon closure once per symbol consumption
    # This might prove to be a limitation in regards to some NFAs :(
    possible_states = epsilon_transition_closure(state, automaton['transitions'])

    # Base case: if we've reached the end of the input string
    if index == len(input_string):
        return any(s in automaton['accept_states'] for s in possible_states)

    symbol = input_string[index]
    
    # Collect all possible next states for the current symbol from all epsilon-reachable states
    next_state_list = set()
    for s in possible_states:
        targets = next_states(s, symbol, automaton['transitions'], automaton.get('settings', []))
        if targets != "Hang":
            next_state_list.update(targets)

    # Transmit hang if no paths are possible
    if not next_state_list:
        return False

    # Use a ThreadPoolExecutor to manage threads efficiently
    # Python is not multi-threaded, so this will not have performance benefits
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
                return True

    return False
