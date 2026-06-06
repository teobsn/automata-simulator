from pathlib import Path
import platform
import subprocess
import tempfile
import webbrowser


def dot_quote(value):
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def dot_escape_label(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def dot_quote_label(value):
    return '"' + dot_escape_label(value) + '"'


def format_dot_node(node_id, **attrs):
    parts = [dot_quote(node_id)]
    if attrs:
        attr_text = ", ".join(
            f"{key}={dot_quote_label(value) if key == 'label' else dot_quote(value)}"
            for key, value in attrs.items()
        )
        parts.append(f"[{attr_text}]")
    return " ".join(parts) + ";"


def format_dot_edge(source, target, **attrs):
    parts = [f"{dot_quote(source)} -> {dot_quote(target)}"]
    if attrs:
        attr_text = ", ".join(
            f"{key}={dot_quote_label(value) if key == 'label' else dot_quote(value)}"
            for key, value in attrs.items()
        )
        parts.append(f"[{attr_text}]")
    return " ".join(parts) + ";"


def build_header(graph_type="digraph"):
    return [
        f"{graph_type} G {{",
        '    graph [rankdir=LR, bgcolor="white", pad="0.35", nodesep="0.55", ranksep="0.9", splines=true];',
        '    node [shape=circle, style="filled", fillcolor="white", color="#1f3b73", fontname="Times", fontsize="12", penwidth="1.4"];',
        '    edge [color="#000000", fontname="Times", fontsize="11", arrowsize="0.8"];',
    ]


def finalize_dot(lines):
    return "\n".join(lines + ["}"]) + "\n"


def build_fa_dot(automaton, automaton_type):
    lines = build_header()

    lines.append('    "__start__" [shape=point, label="", style="filled", fillcolor="#1f3b73", width="0.15"];')

    for state in automaton["states"]:
        attrs = {}
        if state == automaton["initial_state"]:
            attrs["penwidth"] = "2.2"
            attrs["color"] = "#0f172a"
            attrs["fillcolor"] = "#f8fafc"
        if state in automaton["accept_states"]:
            attrs["peripheries"] = "2"
            attrs["fillcolor"] = "#e8f4ff"
        lines.append(format_dot_node(state, **attrs))

    lines.append(format_dot_edge("__start__", automaton["initial_state"], color="#0f172a", penwidth="1.2"))

    edge_labels = {}

    if automaton_type == "dfa":
        for source_state, transitions in automaton["transitions"].items():
            for symbol, target_state in transitions.items():
                edge_labels.setdefault((source_state, target_state), []).append(symbol)
    else:
        for source_state, transitions in automaton["transitions"].items():
            for symbol, target_states in transitions.items():
                label = "ε" if symbol == "&" else symbol
                for target_state in target_states:
                    edge_labels.setdefault((source_state, target_state), []).append(label)

    for (source_state, target_state), labels in sorted(edge_labels.items()):
        label = ", ".join(sorted(set(labels)))
        lines.append(
                format_dot_edge(
                    source_state,
                    target_state,
                    label=label,
                    fontcolor="#000000",
                )
            )

    return finalize_dot(lines)


def build_pda_dot(automaton):
    lines = build_header()
    lines.append('    "__start__" [shape=point, label="", style="filled", fillcolor="#1f3b73", width="0.15"];')

    for state in automaton["states"]:
        attrs = {}
        if state == automaton["initial_state"]:
            attrs["penwidth"] = "2.2"
            attrs["color"] = "#0f172a"
            attrs["fillcolor"] = "#f8fafc"
        if state in automaton["accept_states"]:
            attrs["peripheries"] = "2"
            attrs["fillcolor"] = "#f1f5f9"
        lines.append(format_dot_node(state, **attrs))

    lines.append(format_dot_edge("__start__", automaton["initial_state"], color="#0f172a", penwidth="1.2"))

    for source_state, by_symbol in sorted(automaton["transitions"].items()):
        for input_symbol, by_stack in sorted(by_symbol.items()):
            for stack_pop, transitions in sorted(by_stack.items()):
                for next_state, stack_push in transitions:
                    input_label = "ε" if input_symbol == "&" else input_symbol
                    pop_label = "ε" if stack_pop == "&" else stack_pop
                    push_label = "ε" if stack_push == "&" else stack_push
                    label = f"{input_label}, {pop_label} → {push_label}"
                    lines.append(
                        format_dot_edge(
                            source_state,
                            next_state,
                            label=label,
                            fontcolor="#000000",
                        )
                    )

    return finalize_dot(lines)
def render_svg(dot_source):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as svg_file:
        svg_path = Path(svg_file.name)

    with open(svg_path, "wb") as handle:
        subprocess.run(
            ["dot", "-Tsvg"],
            input=dot_source.encode("utf-8"),
            stdout=handle,
            check=True,
        )
    return svg_path


def open_preview(svg_path):
    uri = svg_path.as_uri()

    if webbrowser.open(uri):
        return True

    system = platform.system().lower()
    fallback_commands = []

    if system == "darwin":
        fallback_commands.append(["open", str(svg_path)])
    elif system == "windows":
        fallback_commands.append(["cmd", "/c", "start", "", str(svg_path)])
    else:
        fallback_commands.extend(
            [
                ["xdg-open", str(svg_path)],
                ["gio", "open", str(svg_path)],
            ]
        )

    for command in fallback_commands:
        try:
            subprocess.Popen(command)
            return True
        except FileNotFoundError:
            continue
        except Exception:
            continue

    print(f"Preview generated at: {svg_path}")
    return False
