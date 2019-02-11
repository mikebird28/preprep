import unittest
import os
import shutil

from preprep import operator
from preprep.param_holder import Box
#from numpy.testing import assert_array_equal

class TestOperator(unittest.TestCase):

    def test_operator_hashvalue(self):
        test_path = "./test_box"

        if not os.path.exists(test_path):
            os.makedirs(test_path)
        source = None
        for _ in range(100):
            op = operator.Operator()
            op.hello = "OK"
            box = Box("test",test_path)
            caller = operator.Caller(op,box)
            s = caller.get_source()

            if source is None:
                source = s
                continue

            if source != s:
                print("get_source  returns different results")
            source = s
        shutil.rmtree(test_path)


