
# Remember current state
current_state = None

# Find next state from transitions map
def next_state(state, symbol, transitions):
    if state in transitions:
        if symbol in transitions[state]:
            return transitions[state][symbol]
        print(f"State '{state}' not in symbol '{symbol}' transition list.")
    else:
        print(f"state '{state}' not in transitions list.")
        return "Hang"

def simulate(automaton, input_string, write_intermediary=False):
    # Initialize result data
    results = {}
    hang = False

    # Initialize the current state to the start state
    current_state = automaton['initial_state']

    # Process each symbol in the input string
    for symbol in input_string:
        if symbol not in automaton['alphabet']:
            raise ValueError(f"Symbol '{symbol}' not in automaton alphabet.")
        
        # Update the current state based on the transitions
        current_state = next_state(current_state, symbol, automaton['transitions'])
        if current_state == "Hang":
            hang = True
            break

        if write_intermediary:
            results["steps"] = results.get("steps", []) + [current_state]

    # Check if the final state is an accepting state
    results['final_state'] = current_state
    if not hang:
        results['accepted'] = current_state in automaton['accept_states']
    else:
        results['accepted'] = 'Hang'

    return results