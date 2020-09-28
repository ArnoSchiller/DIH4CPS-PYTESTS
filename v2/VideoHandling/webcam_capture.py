"""
WebcamCapture: This module captures the frame from the video stream of the IP 
    camera and saves them into the ring buffer.

Requirements:
- opencv: pip install opencv-python 
    see - https://www.learnopencv.com/install-opencv-4-on-raspberry-pi/
        - https://medium.com/@aadeshshah/pre-installed-and-pre-configured-raspbian-with-opencv-4-1-0-for-raspberry-pi-3-model-b-b-9c307b9a993a

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v1.0.0
@license:   ...

VERSION HISTORY                                                               \n
Version:    (Author) Description:                                   Date:     \n
v0.x.x           see v1 (webcam_recorder) for more informations.    01-09-2020\n
v1.0.0      (AS) First initialize. Added code from WebcamRecorder.  01-09-2020\n
                This version does only saves video frames to ring             \n
                buffer.                                                       \n
v1.0.1      (AS) Adapted code to phyBoard Nunki. Testing process.   28-09-2020\n
"""
import platform
if platform.system() == 'Windows':
    from cv2 import cv2
else:
    import cv2
import threading
from configuration import * 
from mqtt_connection import MQTTConnection


class WebcamCapture:
    """ 
    This class captures the frame from the video stream of the IP camera and
    saves them into the ring buffer.
    
    Attributes:
    -----------
    fps : int
        frames per second of the used camera
    connection_str : str 
        camera url to connect to like: "rtsp://USERNAME:PASSWORD@IP:PORT"
    frame_width : int
        witdth of the captured frame in pixels
    frame_height : int
        height of the captured frame in pixels

    """
    fps = 20
    connection_str = global_camera_connection
    frame_width = 0 
    frame_height = 0 
    device_name = global_user_name

    def __init__(self, buffer_object):
        """ Setup video capture and video writer. 
        """
        self.mqtt_client = MQTTConnection()
        self.buffer = buffer_object
        # initialize video capture
        self.reconnect()

    def init_videoCapture(self):
        if platform.node() == 'phyboard-nunki-imx6-1':
            os.system("chmod 777 init_col_phyCAM_v4l_device.sh")
            os.system("./init_col_phyCAM_v4l_device.sh")
            self.capture = cv2.VideoCapture("/dev/video4", cv2.CAP_V4L2)    
            return
        self.capture = cv2.VideoCapture(self.connection_str)

    def reconnect(self):
        """
        Connect to ip camera. 
        """
        self.mqtt_client.sendProcessMessage(self.device_name, 
                self.mqtt_client.status_list["WebcamCapture"]["OpeningCamera"])
        self.init_videoCapture()

        # try to connect to camera
        while not self.capture.isOpened():
            self.mqtt_client.sendProcessMessage(self.device_name, 
                self.mqtt_client.status_list["WebcamCapture"]["OpeningCameraFailed"])
            self.init_videoCapture()

        self.mqtt_client.sendProcessMessage(self.device_name, 
                self.mqtt_client.status_list["WebcamCapture"]["OpenedCamera"])

        # update frame size
        self.frame_width = int(self.capture.get(3))
        self.frame_height = int(self.capture.get(4))


    def capture_frames(self):
        self.is_running = True
        while self.is_running:
            if self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret == True:
                    self.add_frame_to_buffer(frame)
            else:
                self.reconnect()
        self.release()

    def add_frame_to_buffer(self, frame):
        self.buffer.append_element(frame)

    def release(self):
        """
        Release everything and close open windows.
        """    
        self.is_running = False   
        self.capture.release()
        self.mqtt_client.sendProcessMessage(self.device_name, 
                self.mqtt_client.status_list["WebcamCapture"]["ClosedCamera"])
        cv2.destroyAllWindows()



if __name__ == "__main__":
    print("Run data_acquisation.")
