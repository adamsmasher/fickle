import marshal
import types

def dumps(f):
    return marshal.dumps(f.func_code)

def loads(f):
    return types.FunctionType(marshal.loads(f), globals())
