import ctypes


ptrdiff_t = ctypes.c_int32


class GoString(ctypes.Structure):
    _fields_ = [('p', ctypes.c_char_p),
                ('n', ptrdiff_t)]

    def __init__(self, p):
        super().__init__()
        self.set_vals(p)

    def set_vals(self, p):
        self.p = ctypes.c_char_p(p.encode())
        self.n = ptrdiff_t(len(p))

    def get_value(self):
        casted = ctypes.cast(self.p, ctypes.c_char_p).value.decode()
        stringform = casted[:self.n]
        return stringform

    def use(self):
        return self


GoString.ctype = GoString  # ctype should be whatever the pyarg should be converted
                           # to, and what it should be in func.argtypes


class GoByteSlice(GoString):  # is almost GoString
    def get_value(self):
        casted = ctypes.cast(self.p, ctypes.c_char_p).value
        bytesform = casted[:self.n]
        return bytesform


class __BaseGoNumber():
    pytype = int  # default
    ctype = ctypes.c_int64

    def __init__(self, i):
        # super().__init__()
        self.set_vals(i)

    def set_vals(self, i):
        self._i = self.pytype(i)  # pytype should either be int or float
        self._i = self.ctype(self._i)
        self._v = self._i.value

    def get_value(self):
        return self._v

    def use(self):
        return self.ctype(self._v)


class __BaseGoInt(__BaseGoNumber):
    pytype = int
    ctype = ctypes.c_int64  # default, doesn't matter


# TODO: create int bounds
class GoInt64(__BaseGoInt):
    ctype = ctypes.c_int64


class GoInt32(__BaseGoInt):
    ctype = ctypes.c_int32


class GoInt16(__BaseGoInt):
    ctype = ctypes.c_int16


class GoInt8(__BaseGoInt):
    ctype = ctypes.c_int8


class GoUint64(__BaseGoInt):
    ctype = ctypes.c_uint64


class GoUint32(__BaseGoInt):
    ctype = ctypes.c_uint32


class GoUint16(__BaseGoInt):
    ctype = ctypes.c_uint16


class GoUint8(__BaseGoInt):
    ctype = ctypes.c_uint8


class __BaseGoFloat(__BaseGoNumber):
    pytype = float
    ctype = ctypes.c_float


class GoFloat64(__BaseGoFloat):
    ctype = ctypes.c_double


class GoFloat32(__BaseGoFloat):
    ctype = ctypes.c_float


class GoVoid(ctypes.Structure):
    ctype = ctypes.c_long

    def use(self):
        return self.ctype(0)


string = GoString
byteslice = GoByteSlice
int64 = GoInt64
int32 = GoInt32
int16 = GoInt16
int8 = GoInt8
uint64 = GoUint64
uint32 = GoUint32
uint16 = GoUint16
uint8 = GoInt8
goint = GoInt64  # really no other thing to name this...
uint = GoUint64
gofloat = GoFloat32
float32 = GoFloat32
float64 = GoFloat64
void = GoVoid
