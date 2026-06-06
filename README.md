# Automaton Emulator

A Python-based emulator for Deterministic Finite Automata (DFA), Non-deterministic Finite Automata (NFA), Pushdown Automata (PDA), and Context-Free Grammars (CFG).

## Features

- **Automata & Grammar Simulation**: Support for DFA, NFA, PDA, and CFG.
- **CFG Generation & Verification**: Generate strings from a grammar or verify if a string belongs to it.
- **Interactive Mode**: Step-by-step simulation for DFA.
- **Batch Processing**: Run multiple input strings against an automaton using a list file.
- **Custom Specification Language**: Easy-to-read format for defining automata and grammars.
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

- `<TYPE>`: `DFA`, `NFA`, `PDA`, or `CFG`.
- `<FILE>`: Path to the definition file.
- `[INPUT_STRING]`: (Optional) The string to test or verify.
- `--interactive`, `-i`: Enable interactive mode (DFA only).
- `--verify`: Verify if `input_string` belongs to the CFG (CFG only).
- `--count <N>`: Number of strings to generate (CFG only, default 1).
- `--input-list-file <PATH>`: Path to a file containing multiple test strings (one per line).
- `--output-file <PATH>`: Path to save results.
- `--write-intermediary`: Write intermediary states to the output (DFA only).

### Example

```bash
./simulator.sh DFA examples/dfa/even_zeros_after_last_one/even_zeros_after_last_one.dfa 10100
./simulator.sh CFG examples/cfg/an_bn/an_bn.cfg --count 3
./simulator.sh CFG examples/cfg/an_bn/an_bn.cfg aabb --verify
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

## Definition Format

Models are defined in text files with specific sections enclosed in brackets.

### Sections

- `[alphabet]`: (DFA/NFA) Space-separated list of symbols.
- `[alphabet_states]`: (PDA) Input symbols.
- `[alphabet_stack]`: (PDA) Stack symbols.
- `[variables]`: (CFG) Non-terminal symbols.
- `[terminals]`: (CFG) Terminal symbols.
- `[start_variable]`: (CFG) The starting variable.
- `[states]`: Space-separated list of states (DFA/NFA/PDA).
- `[initial_state]`: The starting state (DFA/NFA/PDA).
- `[accept_states]`: Space-separated list of accepting states (DFA/NFA/PDA).
- `[transitions]`: Transition rules for automata.
- `[rules]`: Production rules for grammars.

### Syntax

#### DFA
`source_state, symbol -> next_state`

#### NFA
- `source_state, symbol -> next_state1, next_state2`
- `source_state, & -> next_state` (Epsilon transition)

#### PDA
`source_state, input_symbol, stack_pop -> next_state, stack_push`

#### CFG
`Variable -> expansion1 | expansion2`
- Use `&` for epsilon (empty derivation).

### Comments
Use `#` for comments.

## Documentation

Detailed technical specification for the automaton definition language and other project details can be found in `doc/language/specification.tex`.

To regenerate the PDF documentation from the LaTeX source, run:
```bash
./dev/generate_docs.sh
```
