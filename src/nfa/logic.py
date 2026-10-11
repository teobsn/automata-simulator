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
    return epsilon_closure({state}, transitions)

def epsilon_closure(states, transitions):
    """
    Finds all states reachable from the given states using only epsilon (&) transitions.
    """
    closure = set(states)
    stack = list(states)

    while stack:
        state = stack.pop()
        if state in transitions and '&' in transitions[state]:
            for next_st in transitions[state]['&']:
                if next_st not in closure:
                    closure.add(next_st)
                    stack.append(next_st)

    return closure

def simulate(automaton, input_string, show_input=False):
    # Initialize result data
    results = {}

    # Check alphabet
    alphabet_set = set(automaton['alphabet'])
    for symbol in input_string:
        if symbol not in alphabet_set and symbol != '&':
            raise ValueError(f"Symbol '{symbol}' not in automaton alphabet.")

    # Add the input string to the result 
    if show_input:
        results['input_string'] = input_string

    # Start simulation
    results['branch'] = simulate_start(automaton, input_string)

    return results

def simulate_start(automaton, input_string):
    transitions = automaton['transitions']
    settings = automaton.get('settings', [])
    accept_states = set(automaton['accept_states'])
    remain_on_undefined = "RemainInCurrentStateOnUndefinedTransition" in settings

    # Start with initial state and all states reachable through epsilon transitions
    current_states = epsilon_closure({automaton['initial_state']}, transitions)

    for symbol in input_string:
        next_states_set = set()
        for state in current_states:
            targets = next_states(state, symbol, transitions, settings)
            if targets != "Hang":
                next_states_set.update(targets)

        current_states = epsilon_closure(next_states_set, transitions)
        if not current_states:
            return False

    return any(s in accept_states for s in current_states)

