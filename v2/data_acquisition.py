"""
This module is the main component of the data acquisition and starts every
needed process. 
"""

import threading, time

from ring_buffer import RingBuffer
from webcam_capture import WebcamCapture
from video_display import VideoDisplay
from video_process import VideoProcessor

class DataAcquisition:
    """ 
    This class is the main component of the data acquisition and starts every
    needed process.
    
    Attributes:
    -----------
    
    """
    video_capture_object = None
    video_display_object = None
    video_process_object = None

    video_capture_thread = None
    video_display_thread = None
    video_process_thread = None

    def __init__(self):
        """ Setup video capture, video writer and if needed the video display object. 
        """
        self.ring_buffer = RingBuffer()
        
        self.video_capture_object = WebcamCapture(self.ring_buffer)
        self.video_capture_thread = threading.Thread(target=self.video_capture_object.capture_frames)
        self.video_capture_thread.start()

        self.video_display_object = VideoDisplay(self.ring_buffer)
        self.video_display_thread = threading.Thread(target=self.video_display_object.display_frames)
        self.video_display_thread.start()

        self.video_process_object = VideoProcessor(self.ring_buffer)
        self.video_processor_thread = threading.Thread(target=self.video_process_object.process_video_data)
        self.video_processor_thread.start()

        time.sleep(10)
        self.video_capture_object.release()
        self.video_display_object.release()

if __name__ == "__main__":
    DataAcquisition()