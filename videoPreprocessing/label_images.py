from matplotlib.pyplot import plot as plt
import os, glob
import cv2

filter_str = "*.avi"
filter_path = os.path.join(os.path.abspath("./"), filter_str)
print(filter_path)
file_paths = glob.glob(filter_path)
print(file_paths)

for path in file_paths:
    file_name = os.path.basename(path)
    self.uploadFileToCloud(file_name)