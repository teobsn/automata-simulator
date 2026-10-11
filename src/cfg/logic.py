import random

def simulate(grammar, input_string, show_input=False):
    # Initialize simulation results
    results = {}

    # Validate that all input symbols are part of the grammar's terminals
    terminals_set = set(grammar['terminals'])
    for symbol in input_string:
        if symbol not in terminals_set:
            raise ValueError(f"Symbol '{symbol}' not in grammar terminals.")

    # Optionally include the input string in the returned results
    if show_input:
        results['input_string'] = input_string

    # Execute the derivation simulation (Recognition mode)
    results['accepted'] = simulate_start(grammar, input_string)

    return results

def generate(grammar, count=1, max_expansions=100):
    """
    Generates random strings from the grammar by following non-deterministic rules.
    Returns a list of derivations, where each derivation is a list of sentential forms.
    """
    all_derivations = []
    truncated = False
    
    if max_expansions is not None and max_expansions <= 0:
        max_expansions = None

    variables_set = set(grammar['variables'])

    for _ in range(count):
        # Start with the start variable
        current_form = [grammar['start_variable']]
        steps = [list(current_form)]
        
        expansions = 0
        
        # While there are still non-terminals to expand
        while (max_expansions is None or expansions < max_expansions):
            # Leftmost derivation: find the first non-terminal
            var_idx = next((i for i, sym in enumerate(current_form) if sym in variables_set), None)
            if var_idx is None:
                break

            sym = current_form[var_idx]
            expansion = random.choice(grammar['rules'][sym])
            if expansion == ['&']:
                current_form = current_form[:var_idx] + current_form[var_idx + 1:]
            else:
                current_form = current_form[:var_idx] + expansion + current_form[var_idx + 1:]

            expansions += 1
            steps.append(list(current_form))

        if max_expansions is not None and any(sym in variables_set for sym in current_form):
            truncated = True
            
        all_derivations.append(steps)
        
    return {
        "derivations": all_derivations,
        "truncated": truncated,
    }

def simulate_start(grammar, input_string):
    # Derivation begins with the defined start variable
    initial_derivation = [grammar['start_variable']]

    # Start recursive simulation with memoization to avoid recomputing the same
    # sentential forms and to handle left-recursive grammars safely.
    return simulate_next(grammar, tuple(initial_derivation), input_string, 0, {}, set())

def simulate_next(grammar, derivation, input_string, index, memo, active):
    """
    Recursive function exploring CFG derivation branches using a parallel approach.
    
    Args:
        derivation: Current sentential form as a tuple of symbols.
        input_string: The target string to be recognized.
        index: Current offset in the input string.
        memo: Cache for already solved (derivation, index) subproblems.
        active: Set of states currently being explored on the recursion stack.
    """

    state = (derivation, index)

    if state in memo:
        return memo[state]

    # If the derivation sequence is empty, check if the entire input has been matched
    if not derivation:
        result = index == len(input_string)
        memo[state] = result
        return result

    # Break cycles caused by left recursion or epsilon loops.
    if state in active:
        return False

    active.add(state)

    # Optimization: discard branches where fixed terminals already exceed remaining input
    fixed_terminals = sum(1 for s in derivation if s in grammar['terminals'])
    if fixed_terminals > (len(input_string) - index):
        active.remove(state)
        memo[state] = False
        return False

    first = derivation[0]
    rest = derivation[1:]

    # Handle terminal symbols at the front of the derivation
    if first in grammar['terminals']:
        # Match against current input symbol and proceed if successful
        if index < len(input_string) and input_string[index] == first:
            result = simulate_next(grammar, rest, input_string, index + 1, memo, active)
        else:
            result = False

        active.remove(state)
        memo[state] = result
        return result

    # Handle non-terminal variables by exploring all possible rule expansions
    if first in grammar['rules']:
        result = False
        for expansion in grammar['rules'][first]:
            # Handle the empty string symbol (&)
            if expansion == ['&']:
                next_derivation = tuple(rest)
            else:
                # Prepend the expansion to the remaining derivation
                next_derivation = tuple(expansion + list(rest))

            if simulate_next(grammar, next_derivation, input_string, index, memo, active):
                result = True
                break

        active.remove(state)
        memo[state] = result
        return result

    active.remove(state)
    memo[state] = False
    return False
