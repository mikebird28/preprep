
import inspect
import dill
#wrapper of the Operator, which provides the check of whether on_fit has already called
class Caller():
    def __init__(self,operator):
        self.__on_fit_called = False
        if isinstance(operator,Operator):
            self.source = self._get_source_operator(operator)
            self.operator = operator
        elif callable(operator):
            self.source = self._get_source_func(operator)
            self.operator = FuncOp(operator)

    def on_fit(self,*args,**kwargs):
        self.__on_fit_called = True
        return self.operator.on_fit(*args,**kwargs)

    def on_pred(self,*args,**kwargs):
        if self.__on_fit_called:
            return self.operator.on_pred(*args,**kwargs)
        else:
            raise Exception("on_fit hasn't called yet")

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
        variables = sorted(variables, key = lambda x : x[0])
        for name,value in methods:
            txt += name.encode("utf-8")
            txt += dill.dumps(value)
        return txt

    def get_source(self):
        return self.source

#Abstract Class
class Operator(object):
    def __init__(self):
        return

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



