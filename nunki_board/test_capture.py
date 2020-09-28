import cv2, os

os.system("chmod 777 init_col_phyCAM_v4l_device.sh")
os.system("./init_col_phyCAM_v4l_device.sh")

cap = cv2.VideoCapture('/dev/video4', cv2.CAP_V4L2)

while cap.isOpened():
    ret, frame = cap.read()
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# cv2.imwrite("/root/files/test.jpg", frame)
