def interpret_result(result):
    """
    Formats the simulation results for display.
    Handles both verification (accepted status) and generation (derivation steps).
    """
    output = ""
    
    # Header for verification mode
    if "input_string" in result:
        output += "[input_string]\n"
        output += f"{result['input_string']}\n\n"

    # Status for verification mode
    if "accepted" in result:
        output += "[accepted]\n"
        output += f"{result['accepted']}\n\n"
        
    # Detail for generation mode
    if "derivations" in result:
        for i, derivation in enumerate(result['derivations']):
            output += f"Derivation {i+1}:\n"
            
            # Format each step of the derivation
            steps = [" ".join(form) for form in derivation]
            output += " -> ".join(steps)
            
            # Extract final string (only terminals)
            final_form = derivation[-1]
            # Filter out non-terminals (if any remained due to safety limit) and epsilon marker
            result_str = "".join([s for s in final_form if s != '&'])
            
            output += f"\nResult: \"{result_str}\"\n\n"

    return output
