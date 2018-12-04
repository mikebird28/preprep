
import inspect
import dill
import hashlib
from .param_holder import Box
from . import constant


class PrepOp:
    """
    Wrapper of operations

    Attributes:
        name : name of operation
        op   : body of operation
        op_source : source code of op
        params    : arguments for op
    """

    def __init__(self,name,op,params):
        self.name = name
        self.box = Box(name)
        self.op = Caller(op,self.box)
        self.op_source = self.op.get_source()
        self.params = params
        self.is_executed = False

    def execute(self,dataset,mode):
        self.is_executed = True
        if mode == constant.MODE_FIT:
            return self.op.on_fit(*dataset,**self.params)
        elif mode == constant.MODE_PRED:
            return self.op.on_pred(*dataset,**self.params)
        else:
            raise TypeError("unknown mode : {}".format(mode))

    def get_hash(self):
        name_dump = dill.dumps(self.name)
        op_dump = self.op_source
        params_dump = dill.dumps(sorted(self.params.items()))
        total_byte = name_dump + op_dump + params_dump
        hash_value = hashlib.md5(total_byte).hexdigest()
        return hash_value

    def set_box(self,box):
        self.box = box
        self.op.set_box(self.box)


#wrapper of the Operator, which provides the check of whether on_fit has already called
class Caller():
    """
    Wrapper of operatoins
    """
    def __init__(self,operator,box):
        self.__on_fit_called = False
        self.box = box
        if isinstance(operator,Operator):
            self.source = self._get_source_operator(operator)
            self.operator = operator
        elif callable(operator):
            self.source = self._get_source_func(operator)
            self.operator = FuncOp(operator)
        else:
            raise ValueError("you can only use Function or Operator subclass as 'add' arguments")

    def on_fit(self,*args,**kwargs):
        # In training mode, clear all values in the box.
        self.box.clear()
        self.operator._set_box(self.box)
        self.__on_fit_called = True
        return self.operator.on_fit(*args,**kwargs)

    def on_pred(self,*args,**kwargs):
        self.operator._set_box(self.box)
        return self.operator.on_pred(*args,**kwargs)

    def set_box(self,box):
        self.box = box

    def get_box(self):
        return self.operator.box

    def _get_source_func(self,op):
        try:
            lines = inspect.getsource(op).strip().encode()
            return lines
        except:
            print("Warning : cannot access to the source code")

    def _get_source_operator(self,op):
        txt = b""
        methods = inspect.getmembers(op, inspect.ismethod)
        methods = sorted(methods,key = lambda x : x[0])
        for name,value in methods:
            txt += self._get_source_func(value)

        variables = vars(op)
        variables = [(k,v) for k,v in variables.items()]
        variables = sorted(variables, key = lambda x : x[0])
        for name,value in variables:
            txt += name.encode("utf-8")
            txt += dill.dumps(value)
        return txt

    def get_source(self):
        return self.source

#Abstract Class
class Operator(object):

    def _set_box(self,box):
        self.box = box

    def save_value(self,key,value):
        self.box[key] = value

    def get_value(self,key):
        return self.box[key]

    def on_pred(self,*args,**kwargs):
        return

    def on_fit(self,*args,**kwargs):
        return

class FuncOp(Operator):
    def __init__(self,f):
        super().__init__()
        self.f = f

    def on_pred(self,*args,**kwargs):
        return self.f(*args,**kwargs)

    def on_fit(self,*args,**kwargs):
        return self.f(*args,**kwargs)

