import unittest
from preprep import operator
from preprep.param_holder import Box
#from numpy.testing import assert_array_equal

class TestOperator(unittest.TestCase):

    def test_operator_hashvalue(self):
        source = None
        for _ in range(100):
            op = operator.Operator()
            op.hello = "OK"
            box = Box("test")
            caller = operator.Caller(op,box)
            s = caller.get_source()

            if source is None:
                source = s
                continue

            if source != s:
                print("get_source  returns different results")
            source = s


