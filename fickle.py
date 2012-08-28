import marshal
import pickle
import types

def dumps(f):
    '''Given a function f, returns a string containing a serialized version of
       f.'''
    global_scopes = {}
    def _dumps(f):
        code = marshal.dumps(f.func_code)

        closure = _get_closure(f)

        globals, global_modules, global_functions = _get_global_data(f)

        return pickle.dumps((
            code, globals, closure, global_modules, global_functions))

    def _get_closure(f):
        '''Returns a list consisting of the closed over values of f, in order, or
           None if f does not have a closure.'''
        return ([cell.cell_contents for cell in f.func_closure]
                if f.func_closure else None)

    def _get_global_data(f):
        '''Returns a (globals, global_modules, global_functions) tuple.'''
        global_id = id(f.func_globals)
        if global_id not in global_scopes:
            # set it initially so recursion halts
            global_scopes[global_id] = ({}, set(), set())
            
            globals, global_modules, global_functions = (
                _get_globals(f),
                _get_global_modules(f),
                _get_global_functions(f))
    
            # inject results into vars that everyone refs
            global_scopes[global_id][0].update(globals)
            global_scopes[global_id][1].update(global_modules)
            global_scopes[global_id][2].update(global_functions)
        return global_scopes[global_id]

    def _get_global_functions(f):
        return set((k, _dumps(v)) for k, v in f.func_globals.iteritems()
                   if isinstance(v, types.FunctionType) and f != v)
    
    return _dumps(f)

def _get_globals(f):
    '''Return a dictionary containing the globals the function expects - 
       without modules or functions referenced (because these need to be
       pickled/unpickled specially).'''
    return dict((k, v) for k, v in f.func_globals.iteritems()
                if not isinstance(v, types.ModuleType) and
                   not isinstance(v, types.FunctionType))


def _get_global_modules(f):
    return set(k for k, v in f.func_globals.iteritems()
               if isinstance(v, types.ModuleType) and _safe_to_reload(k))




def _safe_to_reload(module_name):
    return module_name not in set(['__builtins__'])

def dump(f, f_name):
    with open(f_name, 'w') as fp:
        fp.write(dumps(f))


def loads(f):
    code, globals, closure, global_modules, global_functions = pickle.loads(f)

    code = marshal.loads(code)

    if closure:
        closure = _instantiate_closure(closure)

    for module in global_modules:
        globals[module] = __import__(module)

    for (function_name, function) in global_functions:
        globals[function_name] = loads(function)

    return types.FunctionType(code, globals, closure=closure)


def load(f_name):
    with open(f_name) as f:
        return loads(f.read())


def _instantiate_closure(closure):
    '''Consumes a list of (varname, value) pairs and produces a tuple of cells
       containing the values.'''
    return tuple(_new_cell(value) for value in closure)


def _new_cell(contents):
    def f():
        return contents
    return f.func_closure[0]
