import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core import parser
from nfa import process as nfa_process, logic as nfa_logic


class TestNFA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "nfa"))

    def test_ends_with_aa_or_bb(self):
        filepath = os.path.join(self.examples_dir, "ends_with_aa_or_bb", "ends_with_aa_or_bb.nfa")
        automaton = nfa_process.process_data(parser.parse(filepath))

        self.assertTrue(nfa_logic.simulate(automaton, "aa")["branch"])
        self.assertTrue(nfa_logic.simulate(automaton, "bb")["branch"])
        self.assertTrue(nfa_logic.simulate(automaton, "aaa")["branch"])
        self.assertTrue(nfa_logic.simulate(automaton, "aabb")["branch"])
        self.assertFalse(nfa_logic.simulate(automaton, "aba")["branch"])
        self.assertFalse(nfa_logic.simulate(automaton, "abba")["branch"])
        self.assertFalse(nfa_logic.simulate(automaton, "a")["branch"])
        self.assertFalse(nfa_logic.simulate(automaton, "b")["branch"])

    def test_third_from_end_is_one(self):
        filepath = os.path.join(self.examples_dir, "third_from_end_is_one", "third_from_end_is_one.nfa")
        automaton = nfa_process.process_data(parser.parse(filepath))

        self.assertTrue(nfa_logic.simulate(automaton, "100")["branch"])
        self.assertTrue(nfa_logic.simulate(automaton, "0100")["branch"])
        self.assertTrue(nfa_logic.simulate(automaton, "11100")["branch"])
        self.assertFalse(nfa_logic.simulate(automaton, "001")["branch"])
        self.assertFalse(nfa_logic.simulate(automaton, "010")["branch"])
        self.assertFalse(nfa_logic.simulate(automaton, "10")["branch"])

    def test_epsilon_transitions(self):
        filepath = os.path.join(self.examples_dir, "epsilon_transition_test", "epsilon_transition_test.nfa")
        automaton = nfa_process.process_data(parser.parse(filepath))

        self.assertTrue(nfa_logic.simulate(automaton, "a")["branch"])
        self.assertFalse(nfa_logic.simulate(automaton, "")["branch"])

    def test_state_range(self):
        filepath = os.path.join(self.examples_dir, "state_range_test", "state_range_test.nfa")
        automaton = nfa_process.process_data(parser.parse(filepath))

        self.assertTrue(nfa_logic.simulate(automaton, "0011")["branch"])
        self.assertFalse(nfa_logic.simulate(automaton, "001")["branch"])


if __name__ == "__main__":
    unittest.main()
