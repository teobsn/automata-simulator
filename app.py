import sys
from pathlib import Path

import streamlit as st

# Ensure core simulator and tools directories are importable
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from core import parser
import dfa.logic as dfa_logic
import dfa.process as dfa_process
import nfa.logic as nfa_logic
import nfa.process as nfa_process
import pda.logic as pda_logic
import pda.process as pda_process
import cfg.logic as cfg_logic
import cfg.process as cfg_process
from shared.visualization import build_fa_dot, build_pda_dot
import convert_automaton
import minimise_dfa

# Dispatch table mapping automaton type to its validation and normalization function
PROCESSORS = {
    "DFA": dfa_process.process_data,
    "NFA": nfa_process.process_data,
    "PDA": pda_process.process_data,
    "CFG": cfg_process.process_data,
}


def load_preset_examples(model_type: str) -> dict[str, Path]:
    """
    Discover all bundled example files for the specified model type.
    Excludes interactive text-adventure files since they require terminal I/O.
    """
    examples_dir = PROJECT_ROOT / "examples" / model_type.lower()
    if not examples_dir.exists():
        return {}

    files = {}
    for path in sorted(examples_dir.glob(f"**/*.{model_type.lower()}")):
        if path.stem.startswith("adventure_game"):
            continue
        files[path.stem] = path

    return files


def render_sidebar():
    """
    Render configuration controls in the sidebar: model selector, example loader,
    and specification editor. Returns the selected model type and specification text.
    """
    st.sidebar.header("Configuration")
    model_type = st.sidebar.selectbox("Model Type", ["DFA", "NFA", "PDA", "CFG"])

    presets = load_preset_examples(model_type)
    options = list(presets.keys()) + ["Custom Definition"]
    choice = st.sidebar.selectbox("Preset Example", options)

    if choice != "Custom Definition":
        default_spec = presets[choice].read_text(encoding="utf-8")
    else:
        default_spec = ""

    spec_text = st.sidebar.text_area(
        "Specification",
        value=default_spec,
        height=280,
    )

    return model_type, spec_text


def render_dfa_transformations(model_data):
    """
    Render optional state minimization using partition refinement.
    """
    with st.expander("DFA Minimisation"):
        if st.button("Run Minimization"):
            min_dfa, comments = minimise_dfa.minimize(model_data)
            st.success(
                f"Reduced from {len(model_data['states'])} to {len(min_dfa['states'])} states."
            )
            min_dot = build_fa_dot(min_dfa, "dfa")
            st.graphviz_chart(min_dot, use_container_width=True)
            st.caption("\n".join(comments))


def render_nfa_transformations(model_data):
    """
    Render subset construction tool to determinize an NFA into an equivalent DFA.
    """
    with st.expander("Determinization (Subset Construction)"):
        if st.button("Convert to DFA"):
            dfa_result, comments = convert_automaton.determinize(model_data)
            st.success(f"Generated equivalent DFA with {len(dfa_result['states'])} states.")
            dfa_dot = build_fa_dot(dfa_result, "dfa")
            st.graphviz_chart(dfa_dot, use_container_width=True)
            st.caption("\n".join(comments))


def render_simulation_runner(model_type: str, model_data: dict):
    """
    Render automaton metadata and execute string simulation reactively on input change.
    """
    st.subheader("Simulation")

    alphabet_key = "alphabet_states" if model_type == "PDA" else "alphabet"
    alphabet_symbols = ", ".join(f"`{s}`" for s in model_data[alphabet_key])
    accept_states = ", ".join(f"`{s}`" for s in model_data["accept_states"]) or "None"

    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("Initial State", model_data["initial_state"])
        m2.metric("Total States", len(model_data["states"]))
        m3.metric("Accept States", len(model_data["accept_states"]))

        st.caption(f"**Alphabet ({len(model_data[alphabet_key])}):** {alphabet_symbols}")
        st.caption(f"**Accepting States:** {accept_states}")

    input_string = st.text_input("Input String", value="")
    display_input = input_string if input_string else "epsilon (empty string)"

    # Reactively test string without requiring explicit submit button
    try:
        if model_type == "DFA":
            result = dfa_logic.simulate(model_data, input_string, write_intermediary=True)
            final_state = result["final_state"]

            if result["accepted"]:
                st.success(
                    f"String `{display_input}` is accepted into the language (halted in accepting state `{final_state}`)."
                )
            else:
                st.error(
                    f"String `{display_input}` is rejected (halted in non-accepting state `{final_state}`)."
                )

            if "steps" in result:
                st.markdown("**State Trace:**")
                st.code(" -> ".join(result["steps"]))

        elif model_type == "NFA":
            result = nfa_logic.simulate(model_data, input_string)
            if result["branch"]:
                st.success(
                    f"String `{display_input}` is accepted (found a valid computation branch reaching an accept state)."
                )
            else:
                st.error(
                    f"String `{display_input}` is rejected (no nondeterministic computation branch reached an accept state)."
                )

        elif model_type == "PDA":
            result = pda_logic.simulate(model_data, input_string)
            if result["accepted"]:
                st.success(
                    f"String `{display_input}` is accepted (found a valid path consuming the input and ending in an accept state)."
                )
            else:
                st.error(
                    f"String `{display_input}` is rejected (no valid path accepts this input)."
                )

    except ValueError as error:
        st.warning(f"Alphabet mismatch: {error}")


def render_automaton_view(model_type: str, model_data: dict):
    """
    Layout for state-machine models: Graphviz state diagram alongside simulation results.
    """
    graph_col, sim_col = st.columns([1.1, 0.9])

    with graph_col:
        st.subheader("Transition Diagram")

        if model_type == "DFA":
            dot_source = build_fa_dot(model_data, "dfa")
        elif model_type == "NFA":
            dot_source = build_fa_dot(model_data, "nfa")
        else:
            dot_source = build_pda_dot(model_data)

        st.graphviz_chart(dot_source, use_container_width=True)

        if model_type == "DFA":
            render_dfa_transformations(model_data)
        elif model_type == "NFA":
            render_nfa_transformations(model_data)

    with sim_col:
        render_simulation_runner(model_type, model_data)


def render_cfg_view(model_data: dict):
    """
    Layout for context-free grammars: display production symbols, interactive string
    derivation verification, and random string generation.
    """
    st.subheader("Context-Free Grammar")

    terminals_symbols = ", ".join(f"`{t}`" for t in model_data["terminals"])
    variables_symbols = ", ".join(f"`{v}`" for v in model_data["variables"])

    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("Start Variable", model_data["start_variable"])
        m2.metric("Variables", len(model_data["variables"]))
        m3.metric("Terminals", len(model_data["terminals"]))

        st.caption(f"**Variables:** {variables_symbols}")
        st.caption(f"**Terminals:** {terminals_symbols}")

    verify_tab, generate_tab = st.tabs(["Verification", "Generation"])

    with verify_tab:
        target_string = st.text_input("Test String", value="aabb")

        try:
            result = cfg_logic.simulate(model_data, target_string)
            display_target = target_string if target_string else "epsilon (empty string)"

            if result["accepted"]:
                st.success(f"String `{display_target}` is in the language (derivable from start variable `{model_data['start_variable']}`).")
            else:
                st.error(f"String `{display_target}` cannot be derived from this grammar.")
        except ValueError as error:
            st.warning(f"Alphabet mismatch: {error}")

    with generate_tab:
        count = st.slider("Derivations", min_value=1, max_value=10, value=3)
        max_exp = st.number_input(
            "Max expansions per derivation (0 to disable)",
            min_value=0,
            max_value=500,
            value=50,
        )

        if st.button("Generate"):
            generation = cfg_logic.generate(model_data, count=count, max_expansions=max_exp)

            for index, steps in enumerate(generation["derivations"], start=1):
                final_string = "".join(steps[-1])
                st.markdown(f"**Derivation {index}:** `\"{final_string}\"`")
                st.code(" -> ".join("".join(step) for step in steps))

            if generation.get("truncated"):
                st.warning("One or more derivations reached the expansion limit.")


def main():
    st.set_page_config(page_title="Automata Simulator", layout="wide")
    st.title("Automata & Formal Languages Simulator")
    st.caption("Interactive simulator for DFA, NFA, PDA, and CFG models.")

    model_type, spec_text = render_sidebar()

    if not spec_text.strip():
        st.info("Select a preset example or enter a specification to begin.")
        return

    # Parse and validate the specification against the grammar for model_type
    try:
        parsed_raw = parser.parse_string(spec_text)
        process_func = PROCESSORS[model_type]
        model_data = process_func(parsed_raw)
    except Exception as error:
        st.error(f"Failed to parse specification: {error}")
        return

    if model_type in ["DFA", "NFA", "PDA"]:
        render_automaton_view(model_type, model_data)
    else:
        render_cfg_view(model_data)


if __name__ == "__main__":
    main()
