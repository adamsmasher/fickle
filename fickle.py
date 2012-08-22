import marshal
import pickle
import types

def dumps(f):
    code = marshal.dumps(f.func_code)
    closure = ([cell.cell_contents for cell in f.func_closure]
               if f.func_closure else None)
    return pickle.dumps((code, closure))


def loads(f):
    code, closure = pickle.loads(f)

    code = marshal.loads(code)

    if closure:
        closure = _instantiate_closure(closure)

    return types.FunctionType(code, globals(), closure=closure)


def _instantiate_closure(closure):
    '''Consumes a list of (varname, value) pairs and produces a tuple of cells
       containing the values.'''
    return tuple(_new_cell(value) for value in closure)


def _new_cell(contents):
    def f():
        return contents
    return f.func_closure[0]
