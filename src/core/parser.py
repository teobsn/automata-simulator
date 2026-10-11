import re


def parse_lines(lines):
    data = {}
    current_section = None

    for line in lines:
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

    return data


def parse_string(text):
    return parse_lines(text.splitlines())


def parse(input_file):
    with open(input_file, "r") as f:
        return parse_lines(f)



def expand_range(token):
    # Example: q[0-15] -> q0, q1, ..., q15
    match = re.match(r"(.*)\[(\d+)-(\d+)\]", token)
    if match:
        prefix = match.group(1)
        start = int(match.group(2))
        end = int(match.group(3))
        return [f"{prefix}{i}" for i in range(start, end + 1)]
    return [token]


def get_section_from_data(data, section_name):
    if section_name not in data:
        raise ValueError(f"Parser: Section '{section_name}' not found in input file.")
    return data[section_name]


def get_section_list(data):
    return list(data.keys())

