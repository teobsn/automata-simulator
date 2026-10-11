from core import output

def run_simulation(simulate_func, interpret_func, automaton_data, args, **kwargs):
    """
    Generic runner that handles single input string or batch processing from a file.
    """
    if not args.input_list_file:
        # Single input processing
        result = simulate_func(
            automaton_data, args.input_string, **kwargs
        )
        output.write_output(interpret_func(result), args.output_file)
    else:
        # Batch processing from file
        out_f = open(args.output_file, "w") if args.output_file is not None else None
        try:
            with open(args.input_list_file, "r") as in_f:
                for line in in_f:
                    input_str = line.rstrip("\r\n")
                    # We always show input in batch mode
                    result = simulate_func(
                        automaton_data, input_str, show_input=True, **kwargs
                    )
                    rendered = interpret_func(result)
                    if out_f is not None:
                        out_f.write(rendered + "\n")
                    else:
                        print(rendered)
        finally:
            if out_f is not None:
                out_f.close()

