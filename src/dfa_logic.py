# Find next state from transitions map
def next_state(state, symbol, transitions, settings=[]):
    if state in transitions:
        if symbol in transitions[state]:
            return transitions[state][symbol]

    if "RemainInCurrentStateOnUndefinedTransition" in settings:
        return state

    return "Hang"

def simulate(automaton, input_string, write_intermediary=False, show_input=False):
    # Initialize result data
    results = {}
    hang = False

    # Initialize the current state to the start state
    current_state = automaton['initial_state']

    # Add the input string to the result 
    if show_input:
        results['input_string'] = input_string

    # Initialize the steps list if we want to write intermediary steps
    if write_intermediary:
        results["steps"] = [current_state]

    # Process each symbol in the input string
    for symbol in input_string:
        if symbol not in automaton['alphabet']:
            raise ValueError(f"Symbol '{symbol}' not in automaton alphabet.")

        # Update the current state based on the transitions
        current_state = next_state(current_state, symbol, automaton['transitions'], automaton.get('settings', []))
        if current_state == "Hang":
            hang = True
            break

        # If we want to write intermediary steps, we add the current_state to the "steps" list
        if write_intermediary:
            results["steps"].append(current_state)

    # Check if the final state is an accepting state
    results['final_state'] = current_state
    if not hang:
        results['accepted'] = current_state in automaton['accept_states']
    else:
        results['accepted'] = 'Hang'

    return results