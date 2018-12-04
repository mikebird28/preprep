import dill
import os

def load_boxes(path):
    """ Load saved box files and return dictionary of boxes.
    Args:
        path(str) : Path of directory which contains saved box files.
    Returns:
        boxes : Dictionary of boxes. key : name of box, values : box instance.
    """

    # Check if the path exists.
    if not os.path.exists(path):
        raise FileNotFoundError("{} is not exists.".format(path))
    files = os.listdir(path)

    # Load all box files from path.
    boxes = {} 
    for f in files:
        if not f.endswith(".box"):
            continue
        filepath = os.path.join(path,f)
        with open(filepath,"rb") as fp:
            name = f.replace(".box","")
            box = dill.loads(fp.read())
            boxes[name] = box
    
    # Check equallity of keys and box.name.
    for name,box in boxes.items():
        if name != box.name:
            raise ValueError("Box file {}.box is broken.".format(name+".box"))
    return boxes


def save_boxes(path,boxes):
    """ Save all box files.
    Args:
        boxes : list of boxes.
    """

    # Check if the path exists.
    if not os.path.exists(path):
        raise FileNotFoundError("{} is not exists.".format(path))

    # Svae all box instances.
    for box in boxes:
        filename = box.name + ".box"
        filepath = os.path.join(path,filename)
        with open(filepath,"wb") as fp:
            fp.write(box.serialize())

def is_exists(path,name):
    filename = name+".box"
    path = os.path.join(path,filename)
    return os.path.exists(path)

class Box(dict):
    """ 
    Holder to store common values
    """

    def __init__(self,name):
        self.name = name

    def serialize(self):
        """ Serialize itself and return
        Args:
            None
        Returns:
            Serialized object
        """
        return dill.dumps(self)
