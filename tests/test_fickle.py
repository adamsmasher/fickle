#!/usr/bin/env python
import fickle
import unittest

def module_scope_add_10(x):
    return x + 10

g = 10
def module_scope_add_global(x):
    return x + g

import math
def module_scope_use_imported(x):
    return math.ceil(x) + 10

class TestFickle(unittest.TestCase):
    def test_module_scope(self):
        f = fickle.dumps(module_scope_add_10)
        del globals()['module_scope_add_10']
        f = fickle.loads(f)
        self.assertEqual(f(10), 20)
        globals()['module_scope_add_10'] = f

    def test_closed_functions(self):
        def f():
            return 5
        def g():
            return f()
        gstr = fickle.dumps(g)
        f = None
        g = fickle.loads(gstr)
        self.assertEqual(g(), 5)

    def test_shared_state(self):
        x = []
        def f():
            x.append(1)
        def g():
            x.append(2)
            f()
            return x
        gstr = fickle.dumps(g)
        f = None
        g = fickle.loads(gstr)
        self.assertEqual(g(), [2, 1])

    def test_mutual(self):
        def f(x):
            if x <= 0:
                return True
            else:
                return g(x-1)
        def g(x):
            if x <= 0:
                return False
            else:
                return f(x-1)
        fstr = fickle.dumps(f)
        g = None
        f = fickle.loads(fstr)
        self.assertEqual(f(5), False)

    def test_module_scope_read_global(self):
        '''What should we do when we reference a global? It's something we
           closed over, so let's try to keep the value.'''
        s = fickle.dumps(module_scope_add_global)
        # remove g from the global dictionary to simulate loading in a different
        # time and place
        del globals()['g']
        f = fickle.loads(s)
        self.assertEqual(f(10), 20)
        # restore global
        globals()['g'] = 10

    def test_module_scope_import(self):
        f = fickle.loads(fickle.dumps(module_scope_use_imported))
        del globals()['math']
        self.assertEqual(f(9.7), 20)
        import math

    def test_lambda(self):
        f = fickle.loads(fickle.dumps(lambda x: x + 10))
        self.assertEqual(f(10), 20)

    def test_closure(self):
        x = 5
        def f(y):
            return x + y
        f = fickle.loads(fickle.dumps(f))
        self.assertEqual(f(10), 15)

if __name__ == '__main__':
    unittest.main()
