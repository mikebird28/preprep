
import unittest
import dill
import os
import shutil
from preprep import param_holder

class TestParamHolder(unittest.TestCase):

    def test_box(self):
        box = param_holder.Box(name = "test1")
        box["key1"] = "hello"
        box["key2"] = 3

        serialize = box.serialize()
        deserialize = dill.loads(serialize)
        self.assertEqual(box,deserialize)

        bef_id = id(box)
        box.clear()
        aft_id = id(box)
        self.assertEqual(len(box),0)
        self.assertEqual(bef_id,aft_id)

    def test_save(self):
        test_path = "./test_box"
        invalid_path = "./invaild_box"

        if not os.path.exists(test_path):
            os.makedirs(test_path)

        box1 = param_holder.Box("box1")
        box2 = param_holder.Box("box2")
        boxes = [box1,box2]
        param_holder.save_boxes(test_path,boxes)

        box_filenames = ["box1.box","box2.box"]
        files_in_dir = os.listdir(test_path)
        for f in box_filenames:
            self.assertIn(f,files_in_dir)

        self.assertRaises(FileNotFoundError, lambda : param_holder.save_boxes(invalid_path,boxes))
        shutil.rmtree(test_path)

    def test_load(self):
        test_path = "./test_box"
        invalid_path = "./invaild_box"

        if not os.path.exists(test_path):
            os.makedirs(test_path)

        #In case no box files in target directory.
        boxes = param_holder.load_boxes(test_path)
        self.assertEquals(len(boxes), 0)

        #In case some box files in target directory.
        box1 = param_holder.Box("box1")
        box2 = param_holder.Box("box2")
        boxes = [box1,box2]
        param_holder.save_boxes(test_path,boxes)
        boxes = param_holder.load_boxes(test_path)
        self.assertEqual(len(boxes),2)
        self.assertEqual(box1,boxes[box1.name])
        self.assertEqual(box2,boxes[box2.name])

        #In case a broken box exiests in the target directory.
        bef = os.path.join(test_path,"box1.box")
        aft = os.path.join(test_path,"box3.box")
        os.rename(bef,aft)
        self.assertRaises(ValueError, lambda : param_holder.load_boxes(test_path))

        #In case directory doesn't exist.
        self.assertRaises(FileNotFoundError, lambda : param_holder.load_boxes(invalid_path))
        shutil.rmtree(test_path)

