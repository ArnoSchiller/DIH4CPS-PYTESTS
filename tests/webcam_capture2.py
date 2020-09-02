import numpy as np
import cv2
import datetime

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('rtsp://192.168.1.64/1')

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
videolength = 10

start = datetime.datetime.now()

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame,0)

        # write the flipped frame
        out.write(frame)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        now = datetime.datetime.now()
        l: datetime.timedelta = now - start
        if l.seconds > videolength:
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()