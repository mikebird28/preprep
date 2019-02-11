
import unittest
import hashlib
import os
import shutil
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
from numpy.testing import assert_array_equal

from preprep.param_holder import Box
from preprep import calc_graph
from preprep import PrepOp
from preprep import Operator

class TestCalcGraph(unittest.TestCase):

    def test_hash_io(self):
        cache_path = "./test_cache"
        param_path = "./test_params"
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        if not os.path.exists(param_path):
            os.mkdir(param_path)

        path = "./test_cache/hash_io.md5"
        out_hash = hashlib.md5(bytes("a","utf-8")).hexdigest()
        op_hash =  hashlib.md5(bytes("b","utf-8",)).hexdigest()
        inp_hash = [hashlib.md5(bytes(c,"utf-8",)).hexdigest() for c in ["c","d","e"]]
        calc_graph.save_hash(path, out_hash,op_hash,inp_hash)
        out_hash2,op_hash2,inp_hash2 = calc_graph.load_hash(path)
        self.assertEqual(out_hash,out_hash2)
        self.assertEqual(op_hash,op_hash2)
        self.assertEqual(inp_hash,inp_hash2)
        shutil.rmtree(cache_path)
        shutil.rmtree(param_path)

    def test_calc_graph_with_op(self):
        cache_path = "./test_cache"
        param_path = "./test_params"
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        if not os.path.exists(param_path):
            os.mkdir(param_path)

        dataset = create_simple_dataset()
        op = TestOp()
        graph = create_graph_with_op("testop",op,param_path)
        dataset1 = graph.run({"input_1":dataset})
        dataset2 = graph.run(dataset)
        assert_frame_equal(dataset1,dataset2)
        shutil.rmtree(cache_path)
        shutil.rmtree(param_path)

    def test_calc_graph(self):
        cache_path = "./test_cache"
        param_path = "./test_params"
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        if not os.path.exists(param_path):
            os.mkdir(param_path)

        dataset = create_simple_dataset()
        graph = create_simple_graph("test1",param_path)
        dataset1 = graph.run({"input_1":dataset})
        dataset2 = graph.run(dataset)
        assert_frame_equal(dataset1,dataset2)
        shutil.rmtree(cache_path)
        shutil.rmtree(param_path)

    def test_calc_split_graph(self):
        cache_path = "./test_cache"
        param_path = "./test_params"
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        if not os.path.exists(param_path):
            os.mkdir(param_path)

        dataset = create_simple_dataset()
        graph = create_split_graph("test1",param_path)
        dataset1 = graph.run({"input_1":dataset})
        dataset2 = graph.run(dataset)
        assert_frame_equal(dataset1,dataset2)
        shutil.rmtree(cache_path)
        shutil.rmtree(param_path)

    def test_calc_mutlitinput_graph(self):
        cache_path = "./test_cache"
        param_path = "./test_params"
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        if not os.path.exists(param_path):
            os.mkdir(param_path)

        dataset = create_simple_dataset()
        graph = create_mutliinput_graph("test1",param_path)
        dataset1 = graph.run({"input_1":dataset,"input_2":dataset})
        dataset2 = graph.run({"input_1":dataset,"input_2":dataset})
        assert_frame_equal(dataset1,dataset2)
        shutil.rmtree(cache_path)
        shutil.rmtree(param_path)

    def test_calc_graph_with_numpy_dataset(self):
        cache_path = "./test_cache"
        param_path = "./test_params"
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        if not os.path.exists(param_path):
            os.mkdir(param_path)

        dataset = create_numpy_dataset()
        graph = create_simple_graph("test1",param_path,save_format="npy")
        dataset1 = graph.run({"input_1":dataset})
        dataset2 = graph.run(dataset)
        assert_array_equal(dataset1,dataset2)
        shutil.rmtree(cache_path)
        shutil.rmtree(param_path)

    def test_calc_graph_with_different_op(self):
        cache_path = "./test_cache"
        param_path = "./test_params"
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        if not os.path.exists(param_path):
            os.mkdir(param_path)

        dataset = create_simple_dataset()
        graph = create_simple_graph("test1",param_path)
        dataset1 = graph.run(dataset)

        graph = create_simple_graph("test2",param_path)
        dataset2 = graph.run(dataset)
        assert_frame_equal(dataset1,dataset2)
        shutil.rmtree(cache_path)
        shutil.rmtree(param_path)


def create_graph_with_op(op_name,op,param_path,save_format = "csv"):
    box = Box(op_name,param_path)
    op = PrepOp(op_name,op,{},box)
    inp_node = calc_graph.InputNode("inp1")
    inp_nodes = {"input_1":inp_node}
    calc_node_1 = calc_graph.CalcNode([inp_node],op,"./test_cache/hash1.md5",calc_graph.CacheHelper("./test_cache/cache1."+save_format,save_format))
    calc_node_2 = calc_graph.CalcNode([calc_node_1],op,"./test_cache/hash2.md5",calc_graph.CacheHelper("./test_cache/cache2."+save_format,save_format))
    calc_node_3 = calc_graph.CalcNode([calc_node_2],op,"./test_cache/hash3.md5",calc_graph.CacheHelper("./test_cache/cache3."+save_format,save_format))
    calc_node_4 = calc_graph.CalcNode([calc_node_3],op,"./test_cache/hash4.md5",calc_graph.CacheHelper("./test_cache/cache4."+save_format,save_format))
    nodes = [calc_node_1,calc_node_2,calc_node_3,calc_node_4]
    return calc_graph.CalcGraph(inp_nodes,nodes)


def create_simple_graph(op_name,param_path,save_format = "csv"):
    box = Box(op_name,param_path)
    op = PrepOp(op_name,lambda x : x*2, {},box)
    inp_node = calc_graph.InputNode("inp1")
    inp_nodes = {"input_1":inp_node}
    calc_node_1 = calc_graph.CalcNode([inp_node],op,"./test_cache/hash1.md5",calc_graph.CacheHelper("./test_cache/cache1."+save_format,save_format))
    calc_node_2 = calc_graph.CalcNode([calc_node_1],op,"./test_cache/hash2.md5",calc_graph.CacheHelper("./test_cache/cache2."+save_format,save_format))
    calc_node_3 = calc_graph.CalcNode([calc_node_2],op,"./test_cache/hash3.md5",calc_graph.CacheHelper("./test_cache/cache3."+save_format,save_format))
    calc_node_4 = calc_graph.CalcNode([calc_node_3],op,"./test_cache/hash4.md5",calc_graph.CacheHelper("./test_cache/cache4."+save_format,save_format))
    nodes = [calc_node_1,calc_node_2,calc_node_3,calc_node_4]
    return calc_graph.CalcGraph(inp_nodes,nodes)

def create_split_graph(op_name,param_path,save_format = "csv"):
    box = Box(op_name,param_path)
    op = PrepOp(op_name,lambda x : x*2, {},box)
    op_s = PrepOp(op_name,lambda x,y : x+y, {},box)
    inp_node = calc_graph.InputNode("inp1")
    inp_nodes = {"input_1":inp_node}
    calc_node_1 = calc_graph.CalcNode([inp_node],op,"./test_cache/hash1.md5",calc_graph.CacheHelper("./test_cache/cache1."+save_format,save_format))
    calc_node_2 = calc_graph.CalcNode([calc_node_1],op,"./test_cache/hash2.md5",calc_graph.CacheHelper("./test_cache/cache2."+save_format,save_format))
    calc_node_3 = calc_graph.CalcNode([calc_node_1],op,"./test_cache/hash3.md5",calc_graph.CacheHelper("./test_cache/cache3."+save_format,save_format))
    calc_node_4 = calc_graph.CalcNode([calc_node_2,calc_node_3],op_s,"./test_cache/hash4.md5",calc_graph.CacheHelper("./test_cache/cache4."+save_format,save_format))
    nodes = [calc_node_1,calc_node_2,calc_node_3,calc_node_4]
    return calc_graph.CalcGraph(inp_nodes,nodes)

def create_mutliinput_graph(op_name,param_path,save_format = "csv"):
    box = Box(op_name,param_path)
    op = PrepOp(op_name,lambda x : x*2, {},box)
    op_s = PrepOp(op_name,lambda x,y : 3*(x+y), {}, box)
    inp_node1 = calc_graph.InputNode("inp1")
    inp_node2 = calc_graph.InputNode("inp2")
    inp_nodes = {"input_1":inp_node1,"input_2":inp_node2}
    calc_node_1 = calc_graph.CalcNode([inp_node1],op,"./test_cache/hash1.md5",calc_graph.CacheHelper("./test_cache/cache1."+save_format,save_format))
    calc_node_2 = calc_graph.CalcNode([inp_node2],op,"./test_cache/hash2.md5",calc_graph.CacheHelper("./test_cache/cache2."+save_format,save_format))
    calc_node_3 = calc_graph.CalcNode([calc_node_1,calc_node_2],op_s,"./test_cache/hash3.md5",calc_graph.CacheHelper("./test_cache/cache3."+save_format,save_format))
    nodes = [calc_node_1,calc_node_2,calc_node_3]
    return calc_graph.CalcGraph(inp_nodes,nodes)


def create_simple_dataset():
    ls = [[1,2,3],[4,5,6]]
    return pd.DataFrame(ls,columns = ["a","b","c"])

def create_numpy_dataset():
    return np.array([[1,2,3],[4,5,6]])

class TestOp(Operator):
    def on_fit(self,df):
        return df * 2

    def on_pred(self,df):
        return df * 3

if __name__ == "__main__":
    unittest.main()
