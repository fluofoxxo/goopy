from .__govars import *
import copy
import ctypes


ITERABLES = list, tuple
__doc__ = """Known issues:
  - Putting goopy.string or goopy.byteslice inside a tuple is not possible, and it is thus not possible for Go functions to return tuples containing strings."""

ptrdiff_t = ctypes.c_int32


class Wrapper:
    def __init__(self, dll):
        self.dll = ctypes.cdll.LoadLibrary(dll)

        self.__funcdefs = {}

    def define(self, funcname, argtypes, restype):
        func = getattr(self.dll, funcname)
        func.argtypes = [a.ctype for a in argtypes]
        if type(restype) not in ITERABLES:
            func.restype = restype.ctype
        else:
            fields = []
            for i, res in enumerate(restype):
                fields.append(("r{}".format(i), res.ctype))

            class _NewTuple_(ctypes.Structure):
                _fields_ = fields

                def get_value(self):
                    end = []
                    for f, v in self._fields_:
                        attr = getattr(self, f)
                        try:
                            end.append(attr.value)
                        except AttributeError:  # probably .value, but debug
                            end.append(attr)
                    return end

            new_tuple = _NewTuple_
            restype = new_tuple
            func.restype = restype

        is_void = (restype is GoVoid)
        self.__funcdefs[funcname] = [argtypes, restype, func, is_void]

    def __generic_function(self, funcdefs, *a):
        need = len(funcdefs[0])
        have = len(a)
        if need < have:
            raise ValueError("too many arguments")
        elif have > need:
            raise ValueError("too few arguments")

        args = [funcdefs[0][i](x) for i, x in enumerate(a)]
        fixed_args = [arg.use() for arg in args]

        result = funcdefs[2](*fixed_args)
        try:
            if funcdefs[3]:  # if is_void (GoVoid)
                return None
            return result.get_value()  # should be string or bytes or tuple
        except AttributeError:  # in case it's probably a ctypes type (for now, just nums)
            try:  # try to see if it's a ctype
                return result.value
            except AttributeError:  # probably not a ctype
                return result  # use for debugging

    def __getattr__(self, name):
        if hasattr(self.dll, name) and name not in self.__funcdefs:
            raise ValueError("method '{}' exists, but is not defined".format(name))
        if name not in self.__funcdefs:
            raise AttributeError("no method '{}'".format(name))
        return lambda *a: self.__generic_function(self.__funcdefs[name], *a)
