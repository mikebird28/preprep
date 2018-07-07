
import os
import shutil
import unittest
import pandas as pd
from pandas.util.testing import assert_frame_equal
from preprep import preprep

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
        ret = prep.fit_gene(df)
        answer = df * 24
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
        ret = prep.fit_gene({"input_1":df1,"input_2":df2})
        ret = prep.fit_gene({"input_1":df1,"input_2":df2})
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


def f1(df1,add_value = 3):
    return df1 + add_value

if __name__ == "__main__":
    unittest.main()
