import os
import sys
import unittest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, os.path.join(project_root, "tools"))

from core import parser
from dfa import process as dfa_process, logic as dfa_logic
from nfa import process as nfa_process
import convert_automaton
import minimise_dfa
from shared import visualization


class TestTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples_dir = os.path.join(project_root, "examples")

    def test_convert_nfa_to_dfa(self):
        nfa_path = os.path.join(self.examples_dir, "nfa", "ends_with_aa_or_bb", "ends_with_aa_or_bb.nfa")
        parsed_nfa = nfa_process.process_data(parser.parse(nfa_path))
        dfa_result, comments = convert_automaton.determinize(parsed_nfa)

        self.assertIn("alphabet", dfa_result)

        self.assertIn("states", dfa_result)
        self.assertIn("transitions", dfa_result)
        # Test the determinized DFA on sample inputs
        self.assertTrue(dfa_logic.simulate(dfa_result, "aa")["accepted"])
        self.assertTrue(dfa_logic.simulate(dfa_result, "bb")["accepted"])
        self.assertTrue(dfa_logic.simulate(dfa_result, "aabb")["accepted"])
        self.assertFalse(dfa_logic.simulate(dfa_result, "aba")["accepted"])

    def test_minimise_dfa(self):
        dfa_path = os.path.join(self.examples_dir, "dfa", "contains_11", "contains_11.dfa")
        parsed_dfa = dfa_process.process_data(parser.parse(dfa_path))
        minimized, comments = minimise_dfa.minimize(parsed_dfa)

        self.assertIn("states", minimized)
        self.assertTrue(dfa_logic.simulate(minimized, "11")["accepted"])
        self.assertTrue(dfa_logic.simulate(minimized, "0110")["accepted"])
        self.assertFalse(dfa_logic.simulate(minimized, "01")["accepted"])

    def test_visualize_dot_generation(self):
        dfa_path = os.path.join(self.examples_dir, "dfa", "contains_11", "contains_11.dfa")
        parsed_dfa = dfa_process.process_data(parser.parse(dfa_path))
        dot = visualization.build_fa_dot(parsed_dfa, "dfa")

        self.assertIn("digraph G", dot)
        self.assertIn("q0", dot)


if __name__ == "__main__":
    unittest.main()
