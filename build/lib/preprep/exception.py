
class OperationError(Exception):
    def __init__(self,message):
        super().__init__(message)

class GraphError(Exception):
    def __init__(self,message):
        super().__init__(message)

class CacheError(Exception):
    def __init__(self,message):
        super().__init__(message)

class InputError(Exception):
    def __init__(self,message):
        super().__init__(message)
