import cv2
from configuration import * 

connection_str = global_camera_connection
use_light = global_use_light

if use_light:
    from LED_control import LEDRing

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(connection_str)

if use_light:
    led = LEDRing()
    led.activate()

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        #frame = cv2.flip(frame,0)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()
if use_light:
    led.deactivate()
    led.release()
