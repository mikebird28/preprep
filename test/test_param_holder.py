
import unittest
import dill
import os
import shutil
from preprep import param_holder

class TestParamHolder(unittest.TestCase):

    def test_box(self):
        test_path = "./test_box"
        if not os.path.exists(test_path):
            os.makedirs(test_path)

        box1 = param_holder.Box(name = "test1",paramdir=test_path)
        box1["key1"] = "hello"
        box1["key2"] = 3

        box2 = param_holder.Box(name = "test1",paramdir=test_path)
        self.assertEqual(box1["key1"],box2["key1"])
        self.assertEqual(box1["key2"],box2["key2"])

        # Check size
        self.assertEqual(box1.size,2)
        self.assertEqual(box2.size,2)
        box1.clear()
        self.assertEqual(box1.size,0)
        self.assertEqual(box2.size,0)


    def test_load(self):
        test_path = "./test_box"
        invalid_path = "./invaild_box"

        if not os.path.exists(test_path):
            os.makedirs(test_path)

        #In case no box files in target directory.
        boxes = param_holder.load_boxes(test_path)

        #In case some box files in target directory.
        box1 = param_holder.Box("box1",test_path)
        box1["key1"] = "value1"
        box2 = param_holder.Box("box2",test_path)
        box2["key2"] = "value2"
        boxes = [box1,box2]
        #param_holder.save_boxes(test_path,boxes)

        boxes = param_holder.load_boxes(test_path)
        self.assertEqual(box1["key1"],boxes[box1.name]["key1"])
        self.assertEqual(box2["key2"],boxes[box2.name]["key2"])

        #In case a broken box exiests in the target directory.
        shutil.rmtree(test_path)
        self.assertRaises(FileNotFoundError, lambda : param_holder.load_boxes(test_path))
        self.assertRaises(FileNotFoundError, lambda : param_holder.load_boxes(invalid_path))

