import unittest
from bal_runtime import Interpreter, parse, BALRuntimeError

class TestBALLanguage(unittest.TestCase):
    def run_bal(self,source):
        output=[]; Interpreter(output=output.append).run(source); return output
    def test_variables_arithmetic_and_print(self):
        self.assertEqual(self.run_bal("let x = 2 + 3 * 4\nprint x"),["14"])
    def test_functions_lists_and_while(self):
        source="""\nfn square(x) { return x * x }\nlet values = [1, 2, 3]\nlet i = 0\nlet total = 0\nwhile i < values.length {\n total = total + square(values[i])\n i = i + 1\n}\nprint total\n"""
        self.assertEqual(self.run_bal(source),["14"])
    def test_if_else(self):
        self.assertEqual(self.run_bal('if 3 > 2 { print "yes" } else { print "no" }'),["yes"])
    def test_dictionary_and_index(self):
        self.assertEqual(self.run_bal('let x = {a: 9}\nprint x["a"]'),["9"])
    def test_bioavailability_builtin(self):
        value=self.run_bal("print availability(0.5, 0.2, 0.4, 2.0, 1.5)")
        self.assertEqual(len(value),1); self.assertGreater(float(value[0]),0)
    def test_undefined_variable_errors(self):
        with self.assertRaises(BALRuntimeError): Interpreter(output=lambda _:None).run("print missing")
    def test_parser_rejects_invalid_syntax(self):
        with self.assertRaises(Exception): parse("let = 3")

if __name__=="__main__": unittest.main()
