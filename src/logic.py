
# Remember current state
current_state = None

# Find next state from transitions map
def next_state(state, symbol, transitions):
    return transitions[state][symbol]

def simulate(automaton, input_string, write_intermediary=False):
    # Initialize result data
    results = {}

    # Initialize the current state to the start state
    current_state = automaton['initial_state']

    # Process each symbol in the input string
    for symbol in input_string:
        if symbol not in automaton['alphabet']:
            raise ValueError(f"Symbol '{symbol}' not in automaton alphabet.")
        
        # Update the current state based on the transitions
        current_state = next_state(current_state, symbol, automaton['transitions'])
        if write_intermediary:
            results["steps"] = results.get("steps", []) + [current_state]

    # Check if the final state is an accepting state
    results['final_state'] = current_state
    results['accepted'] = current_state in automaton['accept_states']
    
    return results