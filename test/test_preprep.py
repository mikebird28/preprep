
import os
import sys
import shutil
import unittest
import pandas as pd
from pandas.util.testing import assert_frame_equal
from preprep import preprep
from preprep import Operator
from io import StringIO

class TestPreprep(unittest.TestCase):

    def test_func(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        df = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"])
        prep = preprep.Preprep("./test_cache")
        prep = prep.add(lambda x:x * 4)
        prep = prep.add(lambda x:x * 2)
        prep = prep.add(lambda x:x * 3)
        ret1 = prep.fit_gene(df)
        ret2 = prep.fit_gene(df)
        df_true = pd.DataFrame([[24,48,72],[96,120,144]],columns = ["a","b","c"])

        assert_frame_equal(ret1,ret2)
        assert_frame_equal(ret1,df_true)

        prep = preprep.Preprep("./test_cache")
        prep = prep.add(f1,name = "unit_1")
        prep = prep.add(f1)
        prep = prep.add(f1)
        prep.fit_gene(df)
        shutil.rmtree("./test_cache")

    def test_op(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        df = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"])
        op = TestOp1()
        io = StringIO()
        sys.stdout = io
        prep = preprep.Preprep("./test_cache")
        prep = prep.add(op,name = "1")
        prep = prep.add(op,name = "2")
        prep = prep.add(op,name = "3")

        io = StringIO()
        sys.stdout = io
        ret1 = prep.fit_gene(df,verbose = True)
        sys.stdout = sys.__stdout__
        stdout_log1 = io.getvalue()

        io = StringIO()
        sys.stdout = io
        ret2 = prep.fit_gene(df,verbose = True)
        sys.stdout = sys.__stdout__
        stdout_log2 = io.getvalue()

        ret3 = prep.gene(df)

        assert_frame_equal(ret1,ret2)
        assert_frame_not_equal(ret1,ret3)
        self.assertNotEqual(stdout_log1,stdout_log2)

        op2 = TestOp2()
        io = StringIO()
        sys.stdout = io
        prep = preprep.Preprep("./test_cache")
        prep = prep.add(op2,name = "1")
        prep = prep.add(op2,name = "2")
        prep = prep.add(op2,name = "3")
        prep.fit_gene(df,verbose = True)
        sys.stdout = sys.__stdout__
        stdout_log3 = io.getvalue()
        self.assertNotEqual(stdout_log1,stdout_log3)

        op2 = TestOp2()
        op2.a = 100
        io = StringIO()
        sys.stdout = io
        prep = preprep.Preprep("./test_cache")
        prep = prep.add(op2,name = "1")
        prep = prep.add(op2,name = "2")
        prep = prep.add(op2,name = "3")
        prep.fit_gene(df,verbose = True)
        sys.stdout = sys.__stdout__
        stdout_log4 = io.getvalue()
        self.assertNotEqual(stdout_log3,stdout_log4)

        shutil.rmtree("./test_cache")

    def test_multiinput(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        df1 = pd.DataFrame([[2,2,3],[4,5,5]])
        df2 = pd.DataFrame([[1,2,3],[4,5,5]])
        prep1 = preprep.Preprep("./test_cache","input_1")
        prep1 = prep1.add(lambda x:x * 4)

        prep2 = preprep.Preprep("./test_cache","input_2")
        prep2 = prep2.add(lambda x:x * 4)
        prep = preprep.Connect(lambda x,y : x+y,[prep1,prep2],cache_format = "csv")
        prep.fit_gene({"input_1":df1,"input_2":df2})
        #prep.fit_gene({"input_1":df1,"input_2":df2})
        shutil.rmtree("./test_cache")

    def test_connect(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        df = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"])

        prep = preprep.Preprep("./test_cache")
        prep1 = prep.add(lambda x:x * 4)
        prep2 = prep.add(lambda x:x * 4)
        prep = preprep.Connect(lambda x,y : x+y,[prep2,prep1],cache_format = "csv")
        ret = prep.fit_gene(df)
        df_true = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"]) * 8
        assert_frame_equal(ret,df_true)

        prep = preprep.Preprep("./test_cache")
        prep1 = prep.add(lambda x:x * 4)
        prep = preprep.Connect(lambda x,y : x+y,[prep,prep1],cache_format = "csv")
        ret = prep.fit_gene(df)
        df_true = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"]) * 5
        assert_frame_equal(ret,df_true)
        shutil.rmtree("./test_cache")

    def test_feather_support(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        df = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"])

        prep = preprep.Preprep("./test_cache")
        prep = prep.add(lambda x:x * 4, name = "feather_test", cache_format = "feather")
        ret1 = prep.fit_gene(df)
        ret2 = prep.fit_gene(df)
        df_true = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"]) * 4
        assert_frame_equal(ret1,ret2)
        assert_frame_equal(ret1,df_true)

        shutil.rmtree("./test_cache")

    def test_pred_mode(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        df = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"])
        prep = preprep.Preprep("./test_cache")
        prep = prep.add(lambda x:x * 4)
        prep = prep.add(lambda x:x * 2)
        prep = prep.add(lambda x:x * 3)
        ret1 = prep.fit_gene(df,verbose = False)
        ret2 = prep.gene(df,verbose = False)
        df_true = pd.DataFrame([[24,48,72],[96,120,144]],columns = ["a","b","c"])

        assert_frame_equal(ret1,ret2)
        assert_frame_equal(ret1,df_true)
        shutil.rmtree("./test_cache")

    def test_multivalue_output(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        df = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"])
        prep = preprep.Preprep("./test_cache")
        prep = prep.add(f2)
        ret11,ret12 = prep.fit_gene(df)
        ret21,ret22 = prep.fit_gene(df)

        assert_frame_equal(ret11,ret12)
        assert_frame_equal(ret11,ret21)

        prep = preprep.Preprep("./test_cache")
        prep = prep.add(lambda df: "b")
        prep.fit_gene("a")
        shutil.rmtree("./test_cache")

class TestOp1(Operator):
    def on_fit(self,df):
        return df * 2

    def on_pred(self,df):
        return df * 3

class TestOp2(Operator):
    def on_fit(self,df):
        return df * 3

    def on_pred(self,df):
        return df * 4


def f1(df1,add_value = 3):
    return df1 + add_value

def f2(df1,add_value = 3):
    return (df1,df1)

def assert_frame_not_equal(*args, **kwargs):
    try:
        assert_frame_equal(*args, **kwargs)
    except AssertionError:
        pass
    else:
        raise AssertionError

if __name__ == "__main__":
    unittest.main()
