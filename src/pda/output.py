def interpret_result(result):
    output = ""
    
    if "input_string" in result:
        output += "[input_string]\n"
        output += f"{result['input_string']}\n\n"

    output += "[accepted]\n"
    output += f"{result['accepted'] is True}\n\n"

    # if "steps" in result:
    #     output += "\n[intermediary_steps]\n"
    #     output += " ".join(result["steps"])
    #     output += "\n\n"

    return output
