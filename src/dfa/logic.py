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

    alphabet_set = set(automaton['alphabet'])
    accept_states_set = set(automaton['accept_states'])
    settings_set = set(automaton.get('settings', []))
    transitions = automaton['transitions']

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
        if symbol not in alphabet_set:
            raise ValueError(f"Symbol '{symbol}' not in automaton alphabet.")

        # Update the current state based on the transitions
        current_state = next_state(current_state, symbol, transitions, settings_set)
        if current_state == "Hang":
            hang = True
            break

        # If we want to write intermediary steps, we add the current_state to the "steps" list
        if write_intermediary:
            results["steps"].append(current_state)

    # Check if the final state is an accepting state
    results['final_state'] = current_state
    if not hang:
        results['accepted'] = current_state in accept_states_set
    else:
        results['accepted'] = 'Hang'

    return results

def simulate_interactive(automaton):
    current_state = automaton['initial_state']
    alphabet_set = set(automaton['alphabet'])
    accept_states_set = set(automaton['accept_states'])
    settings_set = set(automaton.get('settings', []))
    transitions = automaton['transitions']
    print(f"Initial state: {current_state}")

    while True:
        try:
            symbol = input(f"Enter symbol: ").strip()
            if not symbol:
                continue

            # Allow exiting with common keywords if they aren't part of the alphabet
            if symbol.lower() in ["quit", "exit", "done"] and symbol not in alphabet_set:
                break

            if symbol not in alphabet_set:
                print(f"Error: Symbol '{symbol}' not in automaton alphabet.")
                continue

            current_state = next_state(current_state, symbol, transitions, settings_set)
            print(current_state)

            if current_state == "Hang":
                break
        except EOFError:
            print("\nSimulation ended.")
            break

    accepted = current_state in accept_states_set
    print(f"Final state: {current_state}")
    print(f"Accepted: {accepted}")