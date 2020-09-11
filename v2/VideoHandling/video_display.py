"""
VideoDisplay: This module shows the captured frames from the ring buffer.

Requirements:
- opencv: pip install opencv-python 
    see - https://www.learnopencv.com/install-opencv-4-on-raspberry-pi/
        - https://medium.com/@aadeshshah/pre-installed-and-pre-configured-raspbian-with-opencv-4-1-0-for-raspberry-pi-3-model-b-b-9c307b9a993a

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY                                                               \n
Version:    (Author) Description:                                   Date:     \n
v0.x.x           see basics (webcam_display) for more informations. 01-09-2020\n
v1.0.0      (AS) First initialize. Added code from webcam_display   01-09-2020\n
                and included buffer.
"""

import platform
if platform.system() == 'Windows':
    from cv2 import cv2
else:
    import cv2
from configuration import * 


class VideoDisplay:
    """ 
    This class shows the captured frames from the ring buffer.
    
    Attributes:
    -----------
    is_running : bool
        while true the process is working
    """
    def __init__(self, buffer_object):
        """ Setup video capture and video writer. 
        """
        self.buffer = buffer_object
 
    

    def display_frames(self):
        self.is_running = True
        while self.is_running:
            frame = self.buffer.get_latest_element()
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.release()

    def release(self):
        """
        Release everything and close open windows.
        """  
        self.is_running = False     
        cv2.destroyAllWindows()



if __name__ == "__main__":
    print("Run data_acquisation.")
