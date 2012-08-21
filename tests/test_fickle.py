import fickle
import unittest

def module_scope_add_10(x):
    return x + 10

class TestFickle(unittest.TestCase):
    def test_module_scope(self):
        f = fickle.loads(fickle.dumps(module_scope_add_10))
        self.assertEqual(f(10), 20)
