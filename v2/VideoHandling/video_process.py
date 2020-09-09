"""
VideoProcessor: 

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY                                                                       \n
Version:    (Author) Description:                                           Date:     \n
v1.0.0      (AS) First initialize.                                          02-09-2020\n
"""

import threading
from VideoHandling.video_record import VideoRecorder

class VideoProcessor:
    """ 
    This class writes the captured frames from the buffer into video files.
    
    Attributes:
    ----------- 
    """

    def __init__(self, ring_buffer):
        """ Setup video capture and video writer. 
        """
        self.ring_buffer = ring_buffer
        print("erstellt")

    def process_video_data(self):
        self.isRunning = True
        counter = 0
        frames_list = []
        while self.isRunning:
            counter += 1
            frame = self.ring_buffer.get_next_element()
            """
            if counter >= 40 and counter < 80:
                frames_list.append(frame)
            print(counter)
            if counter == 80:
                buffer_dict = {}
                buffer_dict['frames'] = frames_list
                buffer_dict['timestamp'] = ""
                vr = VideoRecorder(buffer_dict)
            """

    def release(self):
        self.isRunning = False


if __name__ == "__main__":
    print("Run data_acquisation.")
