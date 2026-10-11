import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core import parser
from pda import process as pda_process, logic as pda_logic


class TestPDA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "pda"))

    def test_zero_n_one_n(self):
        filepath = os.path.join(self.examples_dir, "zero_n_one_n", "zero_n_one_n.pda")
        automaton = pda_process.process_data(parser.parse(filepath))

        # Balanced 0^n 1^n should accept
        self.assertTrue(pda_logic.simulate(automaton, "")["accepted"])
        self.assertTrue(pda_logic.simulate(automaton, "01")["accepted"])
        self.assertTrue(pda_logic.simulate(automaton, "0011")["accepted"])
        self.assertTrue(pda_logic.simulate(automaton, "000111")["accepted"])

        # Unbalanced should reject
        self.assertFalse(pda_logic.simulate(automaton, "0")["accepted"])
        self.assertFalse(pda_logic.simulate(automaton, "1")["accepted"])
        self.assertFalse(pda_logic.simulate(automaton, "001")["accepted"])
        self.assertFalse(pda_logic.simulate(automaton, "011")["accepted"])
        self.assertFalse(pda_logic.simulate(automaton, "10")["accepted"])

    def test_invalid_symbol(self):
        filepath = os.path.join(self.examples_dir, "zero_n_one_n", "zero_n_one_n.pda")
        automaton = pda_process.process_data(parser.parse(filepath))

        with self.assertRaises(ValueError):
            pda_logic.simulate(automaton, "012")


if __name__ == "__main__":
    unittest.main()
