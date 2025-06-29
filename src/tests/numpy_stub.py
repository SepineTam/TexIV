import math
class ndarray:
    def __init__(self, data):
        if isinstance(data, ndarray):
            data = data.data
        if data and isinstance(data[0], (list, tuple)):
            self.data=[list(map(float,row)) for row in data]
            self.ndim=2
            self.shape=(len(self.data), len(self.data[0]))
        else:
            self.data=list(map(float,data))
            self.ndim=1
            self.shape=(len(self.data),)
    def __iter__(self):
        return iter(self.data)
    def __len__(self):
        return len(self.data)
    def __getitem__(self, idx):
        return self.data[idx]
    def _binary(self, other, op):
        if isinstance(other, ndarray):
            if self.ndim==2:
                other_rows = other.data
                if other.ndim==2 and other.shape[1]==1 and self.shape[1] != 1:
                    other_rows = [[row[0]] * self.shape[1] for row in other.data]
                return ndarray([[op(a,b) for a,b in zip(ar, br)] for ar, br in zip(self.data, other_rows)])
            else:
                other_vals = other.data
                if other.ndim==1 and len(other_vals)==1 and len(self.data)!=1:
                    other_vals = other_vals * len(self.data)
                return ndarray([op(a,b) for a,b in zip(self.data, other_vals)])
        else:
            if self.ndim==2:
                return ndarray([[op(a,other) for a in ar] for ar in self.data])
            else:
                return ndarray([op(a,other) for a in self.data])
    def __ge__(self, other):
        return self._binary(other, lambda a,b: a>=b)
    def __add__(self, other):
        return self._binary(other, lambda a,b: a+b)
    def __sub__(self, other):
        return self._binary(other, lambda a,b: a-b)
    def __rsub__(self, other):
        return self._binary(other, lambda a,b: b-a)
    def __truediv__(self, other):
        return self._binary(other, lambda a,b: a/b)
    def __mul__(self, other):
        return self._binary(other, lambda a,b: a*b)
    @property
    def T(self):
        if self.ndim==2:
            return ndarray([list(col) for col in zip(*self.data)])
        else:
            return self

float64=float

def array(data, dtype=float):
    return ndarray(data)

def dot(a,b):
    import builtins
    a=a.data if isinstance(a, ndarray) else a
    b=b.data if isinstance(b, ndarray) else b
    result=[]
    for row in a:
        row_res=[]
        for col in zip(*b):
            row_res.append(builtins.sum(x*y for x,y in zip(row,col)))
        result.append(row_res)
    return ndarray(result)

def _axis_reduce(arr, axis, func):
    if axis==1:
        return ndarray([func(row) for row in arr.data])
    elif axis==0:
        return ndarray([func(col) for col in zip(*arr.data)])
    else:
        if arr.ndim == 1:
            return func(arr.data)
        return func([func(row) for row in arr.data])

def any(arr, axis=None):
    import builtins
    return _axis_reduce(arr, axis, builtins.any)

def all(arr, axis=None):
    import builtins
    return _axis_reduce(arr, axis, builtins.all)

def sum(arr, axis=None):
    import builtins
    return _axis_reduce(arr, axis, builtins.sum)

class linalg:
    @staticmethod
    def norm(arr, axis=None, keepdims=False):
        import math, builtins
        if axis==1:
            res=[math.sqrt(builtins.sum(x*x for x in row)) for row in arr.data]
            if keepdims:
                res=[[v] for v in res]
            return ndarray(res)
        else:
            raise NotImplementedError
