import cv2, os

os.system("./init_col_phyCAM_v4l_device.sh")

"""
cap = cv2.VideoCapture('v4l2src device=/dev/video4 !  video/x-bayer,format=grbg,depth=8,width=2592,height=1944 ! bayer2rgbneon ! queue ! kmssink driver-name="imx-drm" force-modesetting=false sync=true', cv2.CAP_V4L2)
"""

cap = cv2.VideoCapture('/dev/video4', cv2.CAP_V4L2)

if cap.isOpened():
    ret, frame = cap.read()

cv2.imwrite("/root/files/test.jpg", frame)
