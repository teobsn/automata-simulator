from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def ensure_input_file(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"File '{path}' does not exist.")
    return path


def ensure_parent_directory(path):
    path = Path(path)
    parent = path.parent
    if parent and not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)
    return path


def unique_preserve_order(items):
    seen = set()
    result = []

    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)

    return result


def format_comment_block(lines):
    if not lines:
        return ""

    return "\n".join(f"# {line}" for line in lines)


def format_section(name, lines):
    output = [f"[{name}]"]
    output.extend(lines)
    return "\n".join(output)


def format_symbol_line(items):
    return " ".join(items)


def format_dfa_transition(source_state, symbol, next_state):
    return f"{source_state}, {symbol} -> {next_state}"


def format_nfa_transition(source_state, symbol, next_states):
    targets = ", ".join(next_states)
    return f"{source_state}, {symbol} -> {targets}"


def render_automaton_file(automaton, *, comments=None, as_nfa=False, transition_order=None):
    comments = comments or []
    transition_order = transition_order or []

    sections = []

    comment_block = format_comment_block(comments)
    if comment_block:
        sections.append(comment_block)

    sections.append(format_section("alphabet", [format_symbol_line(automaton["alphabet"])]))
    sections.append(format_section("states", [format_symbol_line(automaton["states"])]))
    sections.append(format_section("initial_state", [automaton["initial_state"]]))
    sections.append(format_section("accept_states", [format_symbol_line(automaton["accept_states"])]))

    transition_lines = []
    if as_nfa:
        for source_state in transition_order:
            for symbol in automaton["alphabet"]:
                if source_state not in automaton["transitions"]:
                    continue
                if symbol not in automaton["transitions"][source_state]:
                    continue

                next_states = automaton["transitions"][source_state][symbol]
                if isinstance(next_states, str):
                    next_states = [next_states]
                transition_lines.append(
                    format_nfa_transition(source_state, symbol, next_states)
                )
    else:
        for source_state in transition_order:
            for symbol in automaton["alphabet"]:
                if source_state not in automaton["transitions"]:
                    continue
                if symbol not in automaton["transitions"][source_state]:
                    continue

                next_state = automaton["transitions"][source_state][symbol]
                transition_lines.append(
                    format_dfa_transition(source_state, symbol, next_state)
                )

    sections.append(format_section("transitions", transition_lines))

    if automaton.get("settings"):
        sections.append(format_section("settings", automaton["settings"]))

    return "\n\n".join(sections) + "\n"


def write_text(path, content):
    path = ensure_parent_directory(path)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)

