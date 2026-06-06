# Automaton Emulator

A Python-based emulator for Deterministic Finite Automata (DFA), Non-deterministic Finite Automata (NFA), and Pushdown Automata (PDA).

## Features

- **DFA, NFA, and PDA Simulation**: Support for three types of automata.
- **Interactive Mode**: Step-by-step simulation for DFA.
- **Batch Processing**: Run multiple input strings against an automaton using a list file.
- **Custom Specification Language**: Easy-to-read format for defining automata.
- **Flexible Output**: Results can be printed to the console or saved to a file.

## Installation

Ensure you have Python 3 installed. Clone the repository and use the provided shell script or run `src/main.py` directly.

```bash
chmod +x simulator.sh
```

## Usage

### Command Line Arguments

```bash
./simulator.sh <TYPE> <FILE> [INPUT_STRING] [OPTIONS]
```

- `<TYPE>`: `DFA`, `NFA`, or `PDA`.
- `<FILE>`: Path to the automaton definition file.
- `[INPUT_STRING]`: (Optional) The string to test.
- `--interactive`, `-i`: Enable interactive mode (DFA only).
- `--input-list-file <PATH>`: Path to a file containing multiple test strings (one per line).
- `--output-file <PATH>`: Path to save results.
- `--write-intermediary`: Write intermediary steps to the output (DFA only).

### Example

```bash
./simulator.sh DFA examples/dfa/even_zeros_after_last_one/even_zeros_after_last_one.dfa 10100
./simulator.sh PDA examples/pda/zero_n_one_n/zero_n_one_n.pda 0011
```

## Transformation Tools

The repository also includes file-to-file helpers under `tools/` that use the same ASL format as the simulator.

### DFA / NFA Conversion

```bash
python3 tools/convert_automaton.py --to dfa input.nfa output.dfa
python3 tools/convert_automaton.py --to nfa input.dfa output.nfa
```

- `--to dfa` applies NFA determinization using subset construction.
- `--to nfa` rewrites a DFA as an equivalent NFA-compatible ASL file.

### DFA Minimisation

```bash
python3 tools/minimise_dfa.py input.dfa output.min.dfa
```

- The output is a minimized DFA written back to the same project format.

## Automaton Definition Format

Automata are defined in text files with specific sections enclosed in brackets.

### Sections

- `[alphabet]`: (DFA/NFA) Space-separated list of symbols.
- `[alphabet_states]`: (PDA) Input symbols.
- `[alphabet_stack]`: (PDA) Stack symbols.
- `[states]`: Space-separated list of states.
- `[initial_state]`: The starting state.
- `[accept_states]`: Space-separated list of accepting (final) states.
- `[transitions]`: Transition rules (see below).

### Transition Syntax

#### DFA
`source_state, symbol -> next_state`

#### NFA
- `source_state, symbol -> next_state1, next_state2`
- `source_state, & -> next_state` (Epsilon transition)
- `source_state, (symbol1, symbol2) -> next_state` (Multiple symbols)

#### PDA
`source_state, input_symbol, stack_pop -> next_state, stack_push`
- Use `&` for epsilon (no input consumed, or no push/pop).

### Comments
Use `#` for comments.

## Documentation

Detailed technical specification for the automaton definition language can be found in `doc/language/specification.tex`.

To regenerate the PDF documentation from the LaTeX source, run:
```bash
./generate_docs.sh
```
