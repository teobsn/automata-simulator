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

def epsilon_transition_closure(state, stack, transitions, visited=None):
    """
    Finds all configurations (state, stack) reachable from the given configuration
    using only epsilon (&) transitions. This allows the PDA to change states or 
    modify the stack without consuming input symbols.
    """
    if visited is None:
        visited = set()
    
    # Configuration is (state, stack_as_tuple) to ensure hashability
    config = (state, tuple(stack))
    
    # Base case for recursion: prevent infinite loops in epsilon cycles
    if config in visited:
        return set()
    
    visited.add(config)
    results = {config}
    
    # Check if the current state has any epsilon transitions defined
    if state in transitions and '&' in transitions[state]:
        # A PDA can pop a specific symbol or '&' (popping nothing)
        for pop_sym in transitions[state]['&']:
            if pop_sym == '&' or (stack and stack[-1] == pop_sym):
                for next_st, push_str in transitions[state]['&'][pop_sym]:
                    # Create a new stack for the next configuration
                    new_stack = list(stack)
                    
                    # Apply the pop operation
                    if pop_sym != '&':
                        new_stack.pop()
                    
                    # Apply the push operation
                    if push_str != '&':
                        # Multiple symbols are pushed in reverse order (standard PDA convention)
                        for s in reversed(push_str.split()):
                            new_stack.append(s)
                    
                    # Recursively find more epsilon-reachable configurations
                    results.update(epsilon_transition_closure(next_st, new_stack, transitions, visited))
                    
    return results

def simulate(automaton, input_string, show_input=False):
    """
    Main entry point for PDA simulation.
    """
    # Initialize result dictionary
    results = {}

    # Validate input against the defined alphabet (excluding &)
    for symbol in input_string:
        if symbol not in automaton['alphabet_states'] and symbol != '&':
            raise ValueError(f"Symbol '{symbol}' not in automaton alphabet.")

    # Store input string in results if required
    if show_input:
        results['input_string'] = input_string

    # Start the actual simulation logic
    results['accepted'] = simulate_start(automaton, input_string)

    return results

def simulate_start(automaton, input_string):
    """
    Prepares the initial state and stack before starting the recursive simulation.
    """
    # Initialize the current state to the start state and the stack as empty
    current_state = automaton['initial_state']
    current_stack = []

    # Start the multi-threaded recursive simulation
    branch = simulate_next(automaton, current_state, current_stack, input_string, 0)

    return branch

def simulate_next(automaton, state, stack, input_string, index):
    """
    Recursive function that explores all possible PDA computation branches.
    """
    import concurrent.futures

    # Find all configurations reachable by epsilon transitions before consuming a symbol
    possible_configs = epsilon_transition_closure(state, stack, automaton['transitions'])

    # Base case - Check acceptance if we've reached the end of the input string
    if index == len(input_string):
        # The PDA accepts if any reachable epsilon-config is in an accepting state
        return any(s in automaton['accept_states'] for s, st in possible_configs)

    # Step 3: Consume the next symbol from the input string
    symbol = input_string[index]
    
    # Collect all possible next configurations (state, stack) resulting from consuming the symbol
    next_configs = []
    for s, st in possible_configs:
        stack_top = st[-1] if st else '&'
        
        # We need to try both:
        # - Popping the top symbol of the stack
        # - Popping nothing (&)
        for pop_sym in ['&', stack_top]:
            if s in automaton['transitions'] and symbol in automaton['transitions'][s]:
                if pop_sym in automaton['transitions'][s][symbol]:
                    for next_st, push_str in automaton['transitions'][s][symbol][pop_sym]:
                        # Prepare the stack for the next state
                        new_stack = list(st)
                        if pop_sym != '&':
                            new_stack.pop()
                        
                        # Handle pushing new symbols onto the stack
                        if push_str != '&':
                            for sym in reversed(push_str.split()):
                                new_stack.append(sym)
                                
                        next_configs.append((next_st, new_stack))

    # If no paths are possible for this symbol, this branch fails (Hang)
    if not next_configs:
        return False

    # Explore all valid next configurations in parallel
    # Using ThreadPoolExecutor to handle non-deterministic branching
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map each next configuration to a future task
        futures = [
            executor.submit(simulate_next, automaton, next_st, next_stack, input_string, index + 1)
            for next_st, next_stack in next_configs
        ]

        # As each thread completes, check if any of them found an accepting path
        for future in concurrent.futures.as_completed(futures):
            if future.result() is True:
                # Short-circuit: if one branch succeeds, the entire PDA accepts
                return True

    # If all branches have been explored and none accepted
    return False
