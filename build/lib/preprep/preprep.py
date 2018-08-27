
import os
import pandas as pd
from . import calc_graph
from . import exception

class PrepUnit():
    def __init__(self,name,f,params,cache_dir,cache_format):
        self.op = calc_graph.PrepOp(name,f,params)
        self.dependency = []
        self.compiled_node = None

        if cache_format is not None:
            self.hash_path = os.path.join(cache_dir,name)+".md5"
            cache_path = os.path.join(cache_dir,name)+"."+cache_format
            self.cache_helper = calc_graph.CacheHelper(cache_path,cache_format)
        else:
            self.hash_path = None
            self.cache_helper = None

    def add_dependency(self,prep_unit):
        self.dependency += prep_unit

    def to_node(self):
        if self.compiled_node is None:
            depend_cnode = []
            for du in self.dependency:
                dnode = du.to_node()
                depend_cnode.append(dnode)

            op = self.op
            hash_path = self.hash_path
            cache_helper = self.cache_helper
            cnode = calc_graph.CalcNode(depend_cnode,op,hash_path,cache_helper)
            self.compiled_node = cnode
        return self.compiled_node

class InputUnit():
    def __init__(self,name):
        self.name = name
        self.dependency = []
        self.node = calc_graph.InputNode(self.name)

    def to_node(self):
        return self.node

class Baseprep():
    count_for_name = 0
    def __init__(self,cache_dir,inp_units,top_unit,logger = None):
        self.cache_dir = cache_dir
        self.inp_units = inp_units
        self.top_unit = top_unit
        self.logger = None

    def add(self,f,params = {},name = None, cache_format = "csv"):
        if name is None:
            Baseprep.count_for_name += 1
            name = "unit_{}".format(Baseprep.count_for_name)
        prep_unit = PrepUnit(name,f,params,self.cache_dir,cache_format)
        prep_unit.add_dependency([self.top_unit])

        new_prep = Baseprep(self.cache_dir,self.inp_units,prep_unit)
        return new_prep

    def fit_gene(self,datasets,verbose = 0):
        #walk units and generate calc_graph
        top_node = self.top_unit.to_node()
        cnode_ls,inode_dict = walk_node(top_node)
        if len(cnode_ls) == 0:
            raise exception.OperationError("No operation has registered")
        sorted_nodes = resolve_graph(cnode_ls)
        graph = calc_graph.CalcGraph(inode_dict,sorted_nodes,verbose = verbose)
        return graph.run(datasets,mode = "fit")

    def gene(self,datasets,verbose = 0):
        #walk units and generate calc_graph
        top_node = self.top_unit.to_node()
        cnode_ls,inode_dict = walk_node(top_node)
        if len(cnode_ls) == 0:
            raise exception.OperationError("No operation has registered")
        sorted_nodes = resolve_graph(cnode_ls)
        graph = calc_graph.CalcGraph(inode_dict,sorted_nodes,verbose = verbose)
        return graph.run(datasets,mode = "predict")


class Preprep(Baseprep):
    count_for_input = 0
    def __init__(self,cache_dir,input_name = None, logger = None):

        #if cache_dir doesn't exist, create directory
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

        #if input_name isn't specified, set default value
        if input_name is None:
            Preprep.count_for_input += 1
            input_name = "input_{}".format(Preprep.count_for_input)
            
        inp_unit = InputUnit(input_name)
        super().__init__(cache_dir,[inp_unit],inp_unit, logger = logger)

class Connect(Baseprep):
    count_for_connect = 0
    def __init__(self,f,preps,cache_dir = None, cache_format = None, name = None, param = {}):
        if name is None:
            Connect.count_for_connect += 1
            name = "conncet_{}".format(Connect.count_for_connect)

        if cache_dir is None:
            p = preps[0]
            cache_dir = p.cache_dir
        new_inputs = preps
        prep_unit = PrepUnit(name,f,param,cache_dir,cache_format)
        prep_unit.add_dependency([p.top_unit for p in preps])
        super().__init__(cache_dir,new_inputs,prep_unit)


def walk_node(node):
    cnode_ls = []
    inode_dict = {}
    __walk_node(node,cnode_ls,inode_dict)
    return cnode_ls,inode_dict

def __walk_node(node,cnode_ls,inode_dict):
    if isinstance(node,calc_graph.InputNode):
        inode_dict[node.name] = node
        return
    else:
        for n in node.prev_nodes:
            __walk_node(n,cnode_ls,inode_dict)
        cnode_ls.append(node)

def resolve_graph(nodes):
    resolved = []
    for n in nodes:
        if n not in resolved:
            __resolve_graph(n,resolved)
    return resolved

def __resolve_graph(node,resolved):
    if isinstance(node,calc_graph.InputNode):
        return
    for n in node.prev_nodes:
        if n not in resolved:
            __resolve_graph(n,resolved)
    resolved.append(node)

def check_type(dataset):
    allowed = set([
        pd.DataFrame,
        pd.Series,
        dict,
    ])
    return not type(dataset) in allowed

