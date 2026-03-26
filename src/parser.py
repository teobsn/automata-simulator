def parse(input_file):
    # Data dictionary
    data = {}

    # Open file
    f = open(input_file, "r")

    current_section = None

    for line in f:
        line = line.strip()

        # Skip comments
        line = line.split("#")[0].strip()

        # Skip empty lines
        if not line:
            continue

        # Check for section headers
        if line.startswith("[") and line.endswith("]"):
            # Extract section name
            current_section = line[1:-1].strip().lower()

            data[current_section] = []
        else:
            # Check if the data line is within a section
            if not current_section:
                raise ValueError("Parser: Data line found outside of any section.")

            data[current_section].append(line)

    # Close file
    f.close()

    return data


def get_section_from_data(data, section_name):
    if section_name not in data:
        raise ValueError(f"Parser: Section '{section_name}' not found in input file.")
    return data[section_name]


def get_section_list(data):
    return list(data.keys())
