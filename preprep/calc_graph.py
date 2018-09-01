import io
import os
import hashlib
import dill
import inspect
import xxhash
import numpy as np
import pandas as pd
from pandas.util import hash_pandas_object
from . import exception
from . import save_file
from . import operator

DUMP_CSV = "csv"
DUMP_FEATHER = "feather"
DUMP_PICKLE = "pickle"

MODE_FIT = "fit"
MODE_PRED = "predict"

class PrepOp:
    def __init__(self,name,op,params):
        self.name = name
        #op hash value shuold be calculated becuase there is a possibility that someone may rewrite the source code while running
        
        #self.op_hash = get_sourcecode(op)
        self.op = operator.Caller(op)
        self.op_source = self.op.get_source()
        self.params = params

    def execute(self,dataset,mode):
        if mode == MODE_FIT:
            return self.op.on_fit(*dataset,**self.params)
        elif mode == MODE_PRED:
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

class CalcNode:
    def __init__(self, prev_nodes, op, hash_path, cache_helper):
        self.prev_nodes = prev_nodes
        self.op = op
        self.hash_path = hash_path
        self.cache_helper = cache_helper

        # True is this node has already run
        self.run_state = False
        self.load_from_cache = False

        has_hash_path = hash_path is not None
        has_cache_helper = cache_helper is not None
        if (not has_hash_path) and (not has_cache_helper):
            self.do_cache = False
        elif has_hash_path and has_cache_helper:
            self.do_cache = True
        else:
            raise Exception("")

        self.output_dataset = None
        self.output_hash = None

    def run(self,mode = "fit", verbose = 0):
        #check arguments
        use_hash = True
        if mode == MODE_FIT:
            use_hash = True
        elif mode == MODE_PRED:
            use_hash = False
        else:
            raise ValueError("unknown mode {}".format(mode))

        self.run_state = True
        prev_hash = [n.get_hash() for n in self.prev_nodes]
        op_hash = self.op.get_hash()

        #if hash_path exists ,load hash values
        hash_exists = False
        if self.hash_path is not None:
            hash_exists = True
            hash_exists = check_hash_exists(self.hash_path,self.cache_helper.path)
            saved_out_hash, saved_op_hash, saved_inp_hash = load_hash(self.hash_path)

        # if in prediction mode
        if not use_hash:
            log("[*] running on prediction mode, calculate {}".format(self.op.name),1,verbose)
            df = [n.get_dataset() for n in self.prev_nodes]
            df = self.op.execute(df,mode)
            self.output_dataset = df
            return

        # if cache file avaibale, skip calculate
        elif hash_exists and prev_hash == saved_inp_hash and op_hash == saved_op_hash:
            log("[*] available cache for {} exists, skip calculation".format(self.op.name),1,verbose)
            self.output_hash = saved_out_hash
            self.load_from_cache = True
            return

        # if cache file doesn't avaibale, calculate
        if hash_exists and prev_hash == saved_inp_hash and op_hash != saved_op_hash:
            log("[*] saved cache for {} exists, but op hash value has changed, calculate".format(self.op.name),1,verbose)
        elif hash_exists and prev_hash != saved_inp_hash and op_hash == saved_op_hash:
            log("[*] saved cache for {} exists, but dataset hash value has changed, calculate".format(self.op.name),1,verbose)
        elif hash_exists and prev_hash != saved_inp_hash and op_hash != saved_op_hash:
            log("[*] saved cache for {} exists, but both op and dataset hash value has changed, calculate".format(self.op.name),1,verbose)
        else:
            log("[*] no cache exists for {}, calculate".format(self.op.name),1,verbose)
        df = [n.get_dataset() for n in self.prev_nodes]
        df = self.op.execute(df,mode)
        self.output_dataset = df
        self.output_hash = dataset_hash(df)
        if self.do_cache:
            save_hash(self.hash_path,self.output_hash,op_hash,prev_hash)
            self.cache_helper.save(self.output_dataset)

    def get_hash(self):
        if not self.run_state:
            raise Exception("this node hasn't run yet")
        return self.output_hash

    def get_dataset(self):
        if not self.run_state:
            raise Exception("this node hasn't run yet")
        #if already calculate and have dataset, return it
        if self.output_dataset is not None:
            return self.output_dataset
        #if cache file exists, load from cache file
        elif self.load_from_cache:
            return self.cache_helper.load()
        else:
            raise exception.GraphError("something wrong")

class InputNode:
    def __init__(self,name):
        self.name = name
        self.output_dataset = None
        self.output_hash = None

    def get_hash(self):
        if self.output_hash is None:
            raise Exception("dataset it not registered")
        else:
            return self.output_hash

    def get_dataset(self):
        return self.output_dataset

    def set_dataset(self,dataset):
        self.output_dataset = dataset
        self.output_hash = dataset_hash(dataset)

class CalcGraph:
    def __init__(self,inp_nodes,nodes,verbose = 0):
        self.inp_nodes = inp_nodes
        self.nodes = nodes
        self.verbose = verbose

    def run(self,inp_dataset,mode = "fit"):
        """
        run calc graph

        Arguments:
        inp_datasets : pd.DataFrame, pd.Series, pd.Panel or list of them
        mode : run mode ("fit" or "predict")
        """
        #check input value and set to input_node
        log("[*] start running graph",1,self.verbose)
        if not isinstance(inp_dataset,dict) and len(self.inp_nodes) == 1:
            n = list(self.inp_nodes.values())[0]
            n.set_dataset(inp_dataset)
        elif isinstance(inp_dataset,dict) and len(self.inp_nodes) == len(inp_dataset):
            if sorted(list(inp_dataset.keys())) != sorted(list(self.inp_nodes.keys())):
                raise Exception("Input is something wrong")
            for k,n in self.inp_nodes.items():
                n.set_dataset(inp_dataset[k])
        else:
            raise Exception("Input is something wrong")

        for n in self.nodes:
            n.run(verbose = self.verbose, mode = mode)
        last_node = self.nodes[-1]
        return last_node.get_dataset()

def load_hash(path):
    if not os.path.exists(path):
        return None,None,None

    with open(path,"r") as fp:
        out_hash = fp.readline().strip()
        op_hash = fp.readline().strip()
        inp_hash = []
        for row in fp.readlines():
            inp_hash.append(row.strip())
    return out_hash,op_hash,inp_hash

def save_hash(path,out_hash,op_hash,inp_hash):
    hash_list = [out_hash,op_hash] + inp_hash
    hash_str = "\n".join(hash_list)
    with open(path,"w") as fp:
        fp.write(hash_str)

class CacheHelper():
    def __init__(self,path,typ):
        self.path = path
        self.typ = typ

    def load(self):
        extension = self.path.split(".")[-1]
        if extension != self.typ:
            raise Exception("extension error")
        if extension == "csv":
            return save_file.csv_to_df(self.path)
        elif extension == "feather":
            return save_file.feather_to_df(self.path)
        elif extension == "pickle":
            with open(self.path,"rb") as fp:
                return dill.load(fp)
        else:
            raise Exception("")

    def save(self,dataset):
        if is_pandas_object(dataset) and self.typ == "csv":
            save_file.df_to_csv(dataset,self.path)
        elif is_pandas_object(dataset) and self.typ == "feather":
            save_file.df_to_feather(dataset,self.path)
        else:
            with open(self.path,"wb") as fp:
                dill.dump(dataset,fp)

def is_pandas_object(dataset):
    if isinstance(dataset,pd.DataFrame) or isinstance(dataset,pd.Series) or isinstance(dataset,pd.Panel):
        return True
    return False

def is_numpy_object(dataset):
    if isinstance(dataset,np.ndarray):
        return True
    return False

def dataset_hash(dataset):
    if isinstance(dataset,(tuple,list)):
        hash_list = []
        for d in dataset:
            hv  = int(dataset_hash(d),16)
            hash_list.append(hv)
        hash_value = str(hex(sum(hash_list)))
        return hash_value

    elif isinstance(dataset,(dict)):
        keys = list(dataset.keys())
        values = list(dataset.values())
        hash_value = str(hex(int(dataset_hash(keys),16) + int(dataset_hash(values),16)))
        return hash_value
    elif is_pandas_object(dataset):
        #h = hashlib.md5(dataset.values.tobytes()).hexdigest()
        h = str(hash_pandas_object(dataset).sum())
        #h = xxhash.xxh64(feather_encode(dataset)).hexdigest()
        return h
    elif is_numpy_object(dataset):
        h = xxhash.xxh64(dataset.tobytes()).hexdigest()
        return h
    else:
        h = xxhash.xxh64(dill.dumps(dataset)).hexdigest()
        return h

def check_input(dataset,depth = 0):
    if isinstance(dataset,list) and depth == 0:
        flag = True
        for d in dataset:
            flag = flag and check_input(d,1)
        return flag
    elif isinstance(dataset,list) and depth != 0:
        raise TypeError("Unknown data type")
    elif is_pandas_object(dataset) or is_numpy_object(dataset):
        return True
    else:
        return False

def check_hash_exists(hash_path,data_path):
    hash_ext =  os.path.exists(hash_path)
    data_ext =  os.path.exists(data_path)
    return hash_ext and data_ext

def log(message,level,verbose):
    if verbose >=  level:
        print(message)
