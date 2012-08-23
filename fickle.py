import marshal
import pickle
import types

def dumps(f):
    code = marshal.dumps(f.func_code)
    closure = ([cell.cell_contents for cell in f.func_closure]
               if f.func_closure else None)
    globals = f.func_globals
    modules = set(k for k, v in globals.iteritems()
                  if isinstance(v, types.ModuleType) and _safe_to_reload(k))
    globals = dict((k, v) for k, v in globals.iteritems()
                   if not isinstance(v, types.ModuleType))
    return pickle.dumps((code, globals, closure, modules))


def _safe_to_reload(module_name):
    return module_name not in set(['__builtins__'])

def dump(f, f_name):
    with open(f_name, 'w') as fp:
        fp.write(dumps(f))


def loads(f):
    code, globals, closure, modules = pickle.loads(f)

    code = marshal.loads(code)

    if closure:
        closure = _instantiate_closure(closure)

    for module in modules:
        globals[module] = __import__(module)

    return types.FunctionType(code, globals, closure=closure)


def _instantiate_closure(closure):
    '''Consumes a list of (varname, value) pairs and produces a tuple of cells
       containing the values.'''
    return tuple(_new_cell(value) for value in closure)


def _new_cell(contents):
    def f():
        return contents
    return f.func_closure[0]
