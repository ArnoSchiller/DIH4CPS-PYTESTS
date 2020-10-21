import numpy as np
import os
import tensorflow as tf
import cv2

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

file_dir_path = os.path.dirname(__file__)
if not os.path.exists(os.path.join(file_dir_path, "utils")):
    print("could not find utils.")
    quit()
    
from utils import label_map_util
from utils import visualization_utils as vis_util


class Model:
    """
    Model: This class uses pretrained models to detect objects on images.
  
    Make sure u created a folder named as the model version and added every important files: 
        - model graph to a directory called created_model_graph. 
        - label map called object-detection.pbtxt to folder data

    @authors:   Arno Schiller (AS)
    @email:     schiller@swms.de
    @version:   v0.0.1
    @license:   ...

    VERSION HISTORY
    Version:    (Author) Description:                               Date:
    v0.0.1      (AS) First initialize. Added first trained model    14.10.2020\n
                    called tf_API_data2_v1.
    """
    model_label_map_name    = "object-detection.pbtxt"
    model_graph_name        = "created_model_graph"

    num_classes = 12
    
    with_visualisation = True


    def __init__(self, model_name="tf_API_data2_v1"):
        
        model_path = os.path.join(file_dir_path, "pretrained_models", model_name)

        # proof if label map is reachable
        self.model_label_map_path = os.path.join(model_path, "data", self.model_label_map_name)
        if not os.path.exists(self.model_label_map_path):
            print("could not find label map.")
            quit()

        model_graph_path = os.path.join(model_path, self.model_graph_name) 
        if not os.path.exists(model_graph_path):
            print("could not find model graph.")
            quit()
        self.model_ckpt_path = os.path.join(model_graph_path, 'frozen_inference_graph.pb')

        ## load the (frozen) Tensorflow model into memory
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.model_ckpt_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        ## load the label map
        label_map = label_map_util.load_labelmap(self.model_label_map_path)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=self.num_classes, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

    def predict(self, frame):
        num_detected = 0 
        image_np = frame

        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
                # Actual detection.
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                # Visualization of the results of a detection.

                print(classes.shape)
                num_detected = len(boxes)

                if self.with_visualisation:
                    vis_util.visualize_boxes_and_labels_on_image_array(
                        image_np,
                        np.squeeze(boxes),
                        np.squeeze(classes).astype(np.int32),
                        np.squeeze(scores),
                        self.category_index,
                        use_normalized_coordinates=True,
                        line_thickness=8)

                    cv2.imshow('object detection', cv2.resize(image_np, (800, 600)))
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()        
        return  num_detected, image_np

if __name__ == "__main__":
    m = Model()

    img = cv2.imread("./test1_cronjob_2020-10-01_13-59-58_183.png")
    cv2.imshow("Image input", img)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

    res = m.predict(img)
    print(res)
