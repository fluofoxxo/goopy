import ctypes
from .__govars import *


ptrdiff_t = ctypes.c_int32


class Wrapper:
    def __init__(self, dll):
        self.dll = ctypes.cdll.LoadLibrary(dll)

        self.__funcdefs = {}

    def define(self, funcname, argtypes, restype):
        func = getattr(self.dll, funcname)
        func.argtypes = [a.ctype for a in argtypes]
        func.restype = restype.ctype
        is_void = restype == GoVoid
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
            return result.get_value()  # should be string or bytes
        except AttributeError:  # in case it's probably a ctypes type (for now, just nums)
            return result  # should be a number (TODO: actually, like, safeguard this)

    def __getattr__(self, name):
        if name not in self.__funcdefs:
            raise AttributeError("no method '{}'".format(name))
        return lambda *a: self.__generic_function(self.__funcdefs[name], *a)
