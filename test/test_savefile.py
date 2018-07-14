
import os
import shutil
import unittest
import pandas as pd
from pandas.util.testing import assert_frame_equal
from preprep import preprep
from preprep import save_file


class TestSavefile(unittest.TestCase):

    def test_csv(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        path = "./test_cache/test_df.feather"
        df_bef = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"])
        save_file.df_to_csv(df_bef,path)
        df_aft = save_file.csv_to_df(path)
        assert_frame_equal(df_bef,df_aft)
        shutil.rmtree("./test_cache")

    def test_feather1(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        path = "./test_cache/test_df.feather"
        df_bef = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"])
        save_file.df_to_feather(df_bef,path)
        df_aft = save_file.feather_to_df(path)
        assert_frame_equal(df_bef,df_aft)
        shutil.rmtree("./test_cache")

    def test_feather2(self):
        if not os.path.exists("./test_cache"):
            os.mkdir("./test_cache")
        path = "./test_cache/test_df.feather"
        df_bef = pd.DataFrame([[1,2,3],[4,5,6]],columns = ["a","b","c"])
        df_bef.index = ["row1","row2"]
        save_file.df_to_feather(df_bef,path)
        df_aft = save_file.feather_to_df(path)
        assert_frame_equal(df_bef,df_aft)
        shutil.rmtree("./test_cache")


if __name__ == "__main__":
    unittest.main()
