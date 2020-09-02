"""
This module is the main component of the data acquisition and starts every
needed process. 
"""

import threading, time

from ring_buffer import RingBuffer
from webcam_capture import WebcamCapture
from video_display import VideoDisplay

class DataAcquisation:
    """ 
    This class is the main component of the data acquisition and starts every
    needed process.
    
    Attributes:
    -----------
    
    """
    video_capture_object = None
    video_writer_object = None
    video_display_object = None

    video_capture_thread = None
    video_writer_thread = None
    video_display_thread = None

    def __init__(self):
        """ Setup video capture, video writer and if needed the video display object. 
        """
        ring_buffer = RingBuffer()
        
        self.video_capture_object = WebcamCapture(ring_buffer)
        self.video_capture_thread = threading.Thread(target=self.video_capture_object.capture_frames)
        self.video_capture_thread.start()

        self.video_display_object = VideoDisplay(ring_buffer)
        self.video_display_thread = threading.Thread(target=self.video_display_object.display_frames)
        self.video_display_thread.start()
    
        time.sleep(10)
        self.video_capture_object.release()
        self.video_display_object.release()

if __name__ == "__main__":
    DataAcquisation()