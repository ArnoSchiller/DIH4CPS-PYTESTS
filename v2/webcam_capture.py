"""
WebcamCapture: This module captures the frame from the video stream of the IP camera and
        saves them into the ring buffer.

Requirements:
- opencv: pip install opencv-python 
    see - https://www.learnopencv.com/install-opencv-4-on-raspberry-pi/
        - https://medium.com/@aadeshshah/pre-installed-and-pre-configured-raspbian-with-opencv-4-1-0-for-raspberry-pi-3-model-b-b-9c307b9a993a

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.8
@license:   ...

VERSION HISTORY                                                                       \n
Version:    (Author) Description:                                           Date:     \n
v0.x.x           see v1 (webcam_recorder) for more informations.            01-09-2020\n
v1.0.0      (AS) First initialize. Added code from WebcamRecorder. This     01-09-2020\n
                version does only saves video frames to ring buffer.                  \n
"""
import platform
if platform.system() == 'Windows':
    from cv2 import cv2
else:
    import cv2
import threading
from configuration import * 


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

    def __init__(self, buffer_object):
        """ Setup video capture and video writer. 
        """
        self.buffer = buffer_object
        # initialize video capture
        self.reconnect()
 
    

    def reconnect(self):
        self.capture = cv2.VideoCapture(self.connection_str)

        # try to connect to camera
        while not self.capture.isOpened():
            self.capture = cv2.VideoCapture(self.connection_str)

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
        cv2.destroyAllWindows()



if __name__ == "__main__":
    print("Run data_acquisation.")
