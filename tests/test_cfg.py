import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core import parser
from cfg import process as cfg_process, logic as cfg_logic


class TestCFG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "cfg"))

    def test_an_bn_verify(self):
        filepath = os.path.join(self.examples_dir, "an_bn", "an_bn.cfg")
        grammar = cfg_process.process_data(parser.parse(filepath))

        self.assertTrue(cfg_logic.simulate(grammar, "ab")["accepted"])
        self.assertTrue(cfg_logic.simulate(grammar, "aabb")["accepted"])
        self.assertTrue(cfg_logic.simulate(grammar, "aaabbb")["accepted"])
        self.assertFalse(cfg_logic.simulate(grammar, "a")["accepted"])
        self.assertFalse(cfg_logic.simulate(grammar, "b")["accepted"])
        self.assertFalse(cfg_logic.simulate(grammar, "aab")["accepted"])
        self.assertFalse(cfg_logic.simulate(grammar, "abb")["accepted"])

    def test_an_bn_generate(self):
        filepath = os.path.join(self.examples_dir, "an_bn", "an_bn.cfg")
        grammar = cfg_process.process_data(parser.parse(filepath))

        result = cfg_logic.generate(grammar, count=5, max_expansions=10)
        self.assertEqual(len(result["derivations"]), 5)
        for steps in result["derivations"]:
            final_form = steps[-1]
            # Must consist entirely of terminals
            self.assertTrue(all(sym in grammar["terminals"] for sym in final_form))
            # Language is a^n b^n (number of a's must equal number of b's)
            self.assertEqual(final_form.count("a"), final_form.count("b"))

    def test_invalid_symbol(self):
        filepath = os.path.join(self.examples_dir, "an_bn", "an_bn.cfg")
        grammar = cfg_process.process_data(parser.parse(filepath))

        with self.assertRaises(ValueError):
            cfg_logic.simulate(grammar, "abc")


if __name__ == "__main__":
    unittest.main()
