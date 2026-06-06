import concurrent.futures
import random

def simulate(grammar, input_string, show_input=False):
    # Initialize simulation results
    results = {}

    # Validate that all input symbols are part of the grammar's terminals
    for symbol in input_string:
        if symbol not in grammar['terminals']:
            raise ValueError(f"Symbol '{symbol}' not in grammar terminals.")

    # Optionally include the input string in the returned results
    if show_input:
        results['input_string'] = input_string

    # Execute the derivation simulation (Recognition mode)
    results['accepted'] = simulate_start(grammar, input_string)

    return results

def generate(grammar, count=1):
    """
    Generates random strings from the grammar by following non-deterministic rules.
    Returns a list of derivations, where each derivation is a list of sentential forms.
    """
    all_derivations = []
    
    for _ in range(count):
        # Start with the start variable
        current_form = [grammar['start_variable']]
        steps = [list(current_form)]
        
        # Safety limit to prevent infinite loops
        max_expansions = 100
        expansions = 0
        
        # While there are still non-terminals to expand
        while any(sym in grammar['variables'] for sym in current_form) and expansions < max_expansions:
            new_form = []
            expanded_in_this_step = False
            
            # Leftmost derivation approach
            for sym in current_form:
                if sym in grammar['variables'] and not expanded_in_this_step:
                    # Non-determinism: randomly choose one of the production rules
                    expansion = random.choice(grammar['rules'][sym])
                    
                    if expansion != ['&']:
                        new_form.extend(expansion)
                    
                    expanded_in_this_step = True
                    expansions += 1
                else:
                    new_form.append(sym)
            
            current_form = new_form
            steps.append(list(current_form))
            
        all_derivations.append(steps)
        
    return all_derivations

def simulate_start(grammar, input_string):
    # Derivation begins with the defined start variable
    initial_derivation = [grammar['start_variable']]

    # Start recursive simulation with zero consecutive expansions
    return simulate_next(grammar, initial_derivation, input_string, 0, 0)

def simulate_next(grammar, derivation, input_string, index, consecutive_expansions):
    """
    Recursive function exploring CFG derivation branches using a parallel approach.
    
    Args:
        derivation: Current sentential form as a list of symbols.
        input_string: The target string to be recognized.
        index: Current offset in the input string.
        consecutive_expansions: Number of non-terminal expansions without consuming a terminal.
    """

    # If the derivation sequence is empty, check if the entire input has been matched
    if not derivation:
        return index == len(input_string)

    # Detect potential infinite loops in unit rules or epsilon cycles.
    # If expansions exceed the number of variables without consumption, a cycle is assumed.
    if consecutive_expansions > len(grammar['variables']):
        return False

    # Optimization: discard branches where fixed terminals already exceed remaining input
    fixed_terminals = sum(1 for s in derivation if s in grammar['terminals'])
    if fixed_terminals > (len(input_string) - index):
        return False

    first = derivation[0]
    rest = derivation[1:]

    # Handle terminal symbols at the front of the derivation
    if first in grammar['terminals']:
        # Match against current input symbol and proceed if successful
        if index < len(input_string) and input_string[index] == first:
            return simulate_next(grammar, rest, input_string, index + 1, 0)
        return False

    # Handle non-terminal variables by exploring all possible rule expansions
    if first in grammar['rules']:
        next_branches = []
        for expansion in grammar['rules'][first]:
            # Handle the empty string symbol (&)
            if expansion == ['&']:
                next_branches.append(rest)
            else:
                # Prepend the expansion to the remaining derivation
                next_branches.append(expansion + rest)

        # Explore all valid derivation branches in parallel using thread-based concurrency
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Expansion counter is incremented as no terminal has been matched yet
            futures = [
                executor.submit(simulate_next, grammar, b, input_string, index, consecutive_expansions + 1)
                for b in next_branches
            ]

            # Short-circuit and return success if any branch finds a valid derivation
            for future in concurrent.futures.as_completed(futures):
                if future.result() is True:
                    return True

    return False
