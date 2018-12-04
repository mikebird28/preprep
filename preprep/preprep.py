
import os
import pandas as pd
from . import calc_graph
from . import exception
from . import param_holder
from . import operator

class PrepUnit():
    def __init__(self,name,f,params,cache_dir,params_dir,cache_format):
        self.op = operator.PrepOp(name,f,params)
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
    def __init__(self,cache_dir,param_dir,inp_units,top_unit,logger = None):
        self.cache_dir = cache_dir
        self.param_dir = param_dir
        self.inp_units = inp_units
        self.top_unit = top_unit
        self.logger = None

    def add(self,f,params = {},name = None, cache_format = "csv"):
        """Regiter function to this preprep chain.
        Args:
            f(function) : Operation instace or fuction which apply to datasets.
            name(str) : name of this instance.
            cache_format(str) : "feather", "csv", "pickle", default is "csv".
        Returns:
            return new instance of BasePrep.
        """

        if name is None:
            Baseprep.count_for_name += 1
            name = "unit_{}".format(Baseprep.count_for_name)
        prep_unit = PrepUnit(name,f,params,self.cache_dir,self.param_dir ,cache_format)
        prep_unit.add_dependency([self.top_unit])

        new_prep = Baseprep(self.cache_dir,self.param_dir,self.inp_units,prep_unit)
        return new_prep

    def fit_gene(self, datasets, verbose = 0, do_cache = True):
        """
        Apply operations to datasets. This method will cache results of each basprep outputed.

        Args:
            datasets(pd.DataFrame) : inputs dataset
            verbose(int)  : this mehtods 
            do_cache(bool) : if False, this method will not save cache.

        Returns:
            dataset applied operations.
        """

        #walk units and generate calc_graph
        top_node = self.top_unit.to_node()
        cnode_ls,inode_dict = walk_node(top_node)
        if len(cnode_ls) == 0:
            raise exception.OperationError("No operation has registered")
        sorted_nodes = resolve_graph(cnode_ls)
        graph = calc_graph.CalcGraph(inode_dict,sorted_nodes,verbose = verbose) #Create Graph instance.
        result = graph.run(datasets,mode = "fit")

        # After run, collect boxes and save.
        update_boxes = []
        for node in sorted_nodes:
            # In case node has calculated and have box instance.
            if node.op.is_executed:
                update_boxes.append(node.op.box)
            # In case node hasn't run because cache files exists.
            elif param_holder.is_exists(self.param_dir,node.op.name):
                continue
            else:
                raise RuntimeError("Paramter files for {} doesn't exsits even though available cache exists.".format(node.op.name))
        param_holder.save_boxes(self.param_dir,update_boxes)
        return result

    def gene(self,datasets,verbose = 0):
        """
        apply registered operations to datasets. you can't use this method before fit_gene

        Args:
            datasets : inputs dataset
            verbose  : this mehtods 

        Returns:
            dataset applied registered operations.

        Raises:
        """

        #walk units and generate calc_graph
        top_node = self.top_unit.to_node()
        cnode_ls,inode_dict = walk_node(top_node)
        if len(cnode_ls) == 0:
            raise exception.OperationError("No operation has registered")
        sorted_nodes = resolve_graph(cnode_ls)

        # Before run, load boxes and set to PrepOp instances.
        boxes = param_holder.load_boxes(self.param_dir)
        for n in sorted_nodes:
            if not n.op.name in boxes.keys():
                raise RuntimeError("Paramater file for {} doesn't exist. Run 'fit_gene' befor this functions.".format(n.op.name))
            n.op.set_box(boxes[n.op.name])
        graph = calc_graph.CalcGraph(inode_dict,sorted_nodes,verbose = verbose)
        return graph.run(datasets,mode = "predict")


class Preprep(Baseprep):
    count_for_input = 0
    def __init__(self,cache_dir,param_dir,input_name = None, logger = None):

        #if cache_dir doesn't exist, create directory
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        #if input_name isn't specified, set default value
        if input_name is None:
            Preprep.count_for_input += 1
            input_name = "input_{}".format(Preprep.count_for_input)
            
        inp_unit = InputUnit(input_name)
        super().__init__(cache_dir,param_dir,[inp_unit],inp_unit, logger = logger)

class Connect(Baseprep):
    count_for_connect = 0
    def __init__(self,f,preps,cache_dir = None, param_dir = None, cache_format = None, name = None, param = {}):
        if name is None:
            Connect.count_for_connect += 1
            name = "conncet_{}".format(Connect.count_for_connect)

        if cache_dir is None:
            p = preps[0]
            cache_dir = p.cache_dir
        if param_dir is None:
            p = preps[0]
            param_dir = p.param_dir
        new_inputs = preps
        prep_unit = PrepUnit(name,f,param,cache_dir,param_dir,cache_format)
        prep_unit.add_dependency([p.top_unit for p in preps])
        super().__init__(cache_dir,param_dir,new_inputs,prep_unit)


def walk_node(node):
    """ Walk node and get all conneted nodes.
    Args: 
        node(CalcNode) : Node to walk.
    Retruns:
        cnode_ls : List of CalcNodes in the graph.
        inode_dict : Dictionary of InputNodes in the graph.
    """
    cnode_ls = []
    inode_dict = {}
    __walk_node(node,cnode_ls,inode_dict)
    return cnode_ls,inode_dict

def __walk_node(node,cnode_ls,inode_dict):
    """ Inner function of walk_node
    """
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

