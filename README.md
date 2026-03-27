# Automaton Emulator

A Python-based emulator for Deterministic Finite Automata (DFA) and Non-deterministic Finite Automata (NFA).

## Features

- **DFA and NFA Simulation**: Support for both types of finite automata.
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

- `<TYPE>`: `DFA` or `NFA`.
- `<FILE>`: Path to the automaton definition file.
- `[INPUT_STRING]`: (Optional) The string to test.
- `--input-list-file <PATH>`: Path to a file containing multiple test strings (one per line).
- `--output-file <PATH>`: Path to save results.
- `--write-intermediary`: Write intermediary steps to the output (currently implemented for DFA).

### Example

```bash
./simulator.sh DFA examples/dfa/c2/1/1.dfa 10101
```

## Automaton Definition Format

Automata are defined in text files with specific sections enclosed in brackets.

### Sections

- `[alphabet]`: Space-separated list of symbols.
- `[states]`: Space-separated list of states.
- `[initial_state]`: The starting state.
- `[accept_states]`: Space-separated list of accepting (final) states.
- `[transitions]`: Transition rules (see below).

### Transition Syntax

#### DFA
Each transition must be on its own line:
`source_state, symbol -> next_state`

#### NFA
NFAs support more flexible transition syntax:
- `source_state, symbol -> next_state`
- `source_state, (symbol1, symbol2) -> next_state` (Multiple symbols)
- `source_state, symbol -> next_state1, next_state2` (Non-determinism)

### Comments
Use `#` for comments.

```ini
[alphabet]
0 1

[states]
q0 q1

[initial_state]
q0

[accept_states]
q1

[transitions]
q0, 1 -> q1 # Transition to q1 on input 1
q1, 0 -> q1
```

## Documentation

Detailed technical specification for the automaton definition language can be found in `doc/language/specification.tex`.
