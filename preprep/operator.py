
#wrapper of the Operator, which provides the check of whether on_fit has already called
class Caller():
    def __init__(self,operator):
        self.__on_fit_called = False
        if isinstance(operator,Operator):
            self.operator = operator
        elif callable(operator):
            self.operator = FuncOp(operator)

    def on_fit(self,*args,**kwargs):
        self.__on_fit_called = True
        return self.operator.on_fit(*args,**kwargs)

    def on_pred(self,*args,**kwargs):
        if self.__on_fit_called:
            return self.operator.on_pred(*args,**kwargs)
        else:
            raise Exception("on_fit hasn't called yet")

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



