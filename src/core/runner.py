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
        with open(args.input_list_file, "r") as f:
            input_list = f.read().splitlines()

        # Initialize output file
        if args.output_file is not None:
            output.blank_file(args.output_file)

        for input_str in input_list:
            # We always show input in batch mode
            result = simulate_func(
                automaton_data, input_str, show_input=True, **kwargs
            )
            output.write_output(
                interpret_func(result), args.output_file, append=True
            )
