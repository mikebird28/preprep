import dill
import os
import shutil

def load_boxes(path):
    """ Load saved box files and return dictionary of boxes.
    Args:
        path(str) : Path of directory which contains saved box files.
    Returns:
        boxes : Dictionary of boxes. key : name of box, values : box instance.
    """

    if not os.path.exists(path):
        raise FileNotFoundError("{} is not exists.".format(path))
    boxes = {}
    files = os.listdir(path)
    for f in files:
        try:
            f = remove_box_suffix(f)
            boxes[f] = Box(f,path)
        except ValueError:
            # If file name doesn't contains box suffix, skip.
            pass
    return boxes

def is_exists(path,name):
    filename = get_box_name(name)
    path = os.path.join(path,filename)
    return os.path.exists(path)

def get_box_name(name):
    return "{}_box".format(name)

def remove_box_suffix(name):
    suffix = "_box"
    if not name.endswith(suffix):
        raise ValueError("Text {} does not contains {}.".format(name,suffix))
    else:
        return name[:len(name)-len(suffix)]

class Box():
    """ 
    Holder to store common values.
    """

    def __init__(self,name,paramdir):
        self.name = name
        self.cache = {}
        self.paramdir = paramdir

        # Check paramdir exists.
        if not os.path.exists(self.paramdir):
            raise FileNotFoundError("{} is not exists.".format(self.paramdir))

        boxpath = os.path.join(self.paramdir,get_box_name(self.name))
        if not os.path.exists(boxpath):
            os.mkdir(boxpath)

    def __getitem__(self,key):
        filepath = os.path.join(self.paramdir,get_box_name(self.name),key)
        if key in self.cache:
            return self.cache[key]
        elif os.path.exists(filepath):
            with open(filepath,"rb") as fp:
                obj = dill.loads(fp.read())
                self.cache[key] = obj
            return obj
        else:
            raise KeyError("the key {} is not in {}".format(key,self.name))

    def __setitem__(self,key,value):
        self.cache[key] = value
        filepath = os.path.join(self.paramdir,get_box_name(self.name),key)
        with open(filepath,"wb") as fp:
            serialized = dill.dumps(value)
            fp.write(serialized)

    def clear(self):
        self.cache.clear()
        boxpath = os.path.join(self.paramdir,get_box_name(self.name))
        if not os.path.exists(boxpath):
            raise FileNotFoundError("{} doesn't exists.")

        if not os.path.isdir(boxpath):
            raise IOError("{} is not directory.")

        for f in os.listdir(boxpath):
            file_path = os.path.join(boxpath,f)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    #os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)
    @property
    def size(self):
        boxpath = os.path.join(self.paramdir,get_box_name(self.name))
        if not os.path.exists(boxpath):
            raise FileNotFoundError("{} doesn't exists.")

        if not os.path.isdir(boxpath):
            raise IOError("{} is not directory.")

        return len(os.listdir(boxpath))