import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core import parser
from dfa import process as dfa_process, logic as dfa_logic


class TestDFA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "dfa"))

    def test_contains_11(self):
        filepath = os.path.join(self.examples_dir, "contains_11", "contains_11.dfa")
        automaton = dfa_process.process_data(parser.parse(filepath))

        self.assertTrue(dfa_logic.simulate(automaton, "11")["accepted"])
        self.assertTrue(dfa_logic.simulate(automaton, "0110")["accepted"])
        self.assertTrue(dfa_logic.simulate(automaton, "1011")["accepted"])
        self.assertFalse(dfa_logic.simulate(automaton, "101")["accepted"])
        self.assertFalse(dfa_logic.simulate(automaton, "000")["accepted"])
        self.assertFalse(dfa_logic.simulate(automaton, "")["accepted"])

    def test_even_zeros_after_last_one(self):
        filepath = os.path.join(self.examples_dir, "even_zeros_after_last_one", "even_zeros_after_last_one.dfa")
        automaton = dfa_process.process_data(parser.parse(filepath))

        self.assertTrue(dfa_logic.simulate(automaton, "1")["accepted"])
        self.assertTrue(dfa_logic.simulate(automaton, "100")["accepted"])
        self.assertTrue(dfa_logic.simulate(automaton, "10100")["accepted"])
        self.assertFalse(dfa_logic.simulate(automaton, "10")["accepted"])
        self.assertFalse(dfa_logic.simulate(automaton, "101000")["accepted"])

    def test_wildcard_transitions(self):
        filepath = os.path.join(self.examples_dir, "wildcard_test", "wildcard_test.dfa")
        automaton = dfa_process.process_data(parser.parse(filepath))

        self.assertTrue(dfa_logic.simulate(automaton, "a")["accepted"])
        self.assertTrue(dfa_logic.simulate(automaton, "c")["accepted"])
        self.assertTrue(dfa_logic.simulate(automaton, "ba")["accepted"])
        self.assertFalse(dfa_logic.simulate(automaton, "b")["accepted"])

    def test_write_intermediary(self):
        filepath = os.path.join(self.examples_dir, "contains_11", "contains_11.dfa")
        automaton = dfa_process.process_data(parser.parse(filepath))

        res = dfa_logic.simulate(automaton, "011", write_intermediary=True)
        self.assertIn("steps", res)
        self.assertEqual(res["steps"], ["q0", "q0", "q1", "q2"])

    def test_invalid_symbol(self):
        filepath = os.path.join(self.examples_dir, "contains_11", "contains_11.dfa")
        automaton = dfa_process.process_data(parser.parse(filepath))

        with self.assertRaises(ValueError):
            dfa_logic.simulate(automaton, "102")

    def test_parse_string(self):
        raw_spec = """
        [alphabet]
        0 1
        [states]
        s0 s1
        [initial_state]
        s0
        [accept_states]
        s1
        [transitions]
        s0, 1 -> s1
        """
        parsed = parser.parse_string(raw_spec)
        automaton = dfa_process.process_data(parsed)
        self.assertIs(dfa_logic.simulate(automaton, "1")["accepted"], True)
        self.assertIsNot(dfa_logic.simulate(automaton, "0")["accepted"], True)




if __name__ == "__main__":
    unittest.main()
