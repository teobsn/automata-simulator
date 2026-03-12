
def interpret_result(result):
    output = f"[final_state]\n"
    output += f"{result['final_state']}\n"
    output += f"\n[accepted]\n"
    output += f"{result['accepted'] is True}\n"
    
    if "steps" in result:
        output += "\n[intermediary_steps]\n"
        output += " ".join(result['steps'])

    return output

def write_output(string, output_file, append=False):
    if output_file is None:
        print(string)
    else:
        mode = 'a' if append else 'w'
        with open(output_file, mode) as f:
            f.write(string + '\n')
            