
def interpret_result(result):
    output = f"[final_state]\n{result['final_state']}\n"
    output += f"\n[accepted]\n{'true' if result['accepted'] else 'false'}\n"
    
    if "steps" in result:
        output += "\n[intermediary_steps]\n"
        output += " ".join(result['steps'])

    return output

def write_output(string, output_file):
    if output_file is None:
        print(string)
    else:
        with open(output_file, 'w') as f:
            f.write(string + '\n')
            