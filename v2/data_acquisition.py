"""
This module is the main component of the data acquisition and starts every
needed process as a thread. 
"""
import os, sys
import threading, time

currentdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,currentdir) 

from job_broker import JobBroker
from VideoHandling.ring_buffer import RingBuffer
from VideoHandling.webcam_capture import WebcamCapture
from VideoHandling.video_display import VideoDisplay
from VideoHandling.video_process import VideoProcessor

class DataAcquisition:
    """ 
    This class is the main component of the data acquisition and starts every
    needed process as a thread.
    
    Attributes:
    -----------
    video_capture_object : WebcamCapture
        object to capture frames from video stream and save frames to buffer
    video_capture_thread : Thread
        thread to run the capture process

    video_display_object : VideoDisplay
        object to grab the last taken frame and display it on screen
    video_display_thread : Thread
        thread to run the display process

    video_process_object = VideoProcessor
        object takes frame from buffer and uses computer vision to detect 
        interesting frames
    video_process_thread = Thread
        thread to run the video processor process
        
    job_broker_object = JobBroker 
        object to reciev and handle internal messages (job exchange)
    """
    video_capture_object = None
    video_capture_thread = None

    video_display_object = None
    video_display_thread = None

    video_process_object = None
    video_process_thread = None

    job_broker_object = None
    job_broker_thread = None

    def __init__(self):
        """ Setup video capture, video writer and if needed the video display 
        object. Also setup the job broker tu rule the internal communication for job exchange.
        """
        self.ring_buffer = RingBuffer()
        
        self.video_capture_object = WebcamCapture(self.ring_buffer)
        self.video_capture_thread = threading.Thread(target=
                            self.video_capture_object.capture_frames)
        self.video_capture_thread.start()

        self.video_display_object = VideoDisplay(self.ring_buffer)
        self.video_display_thread = threading.Thread(target=
                            self.video_display_object.display_frames)
        self.video_display_thread.start()
        
        self.video_process_object = VideoProcessor(self.ring_buffer)
        self.video_processor_thread = threading.Thread(target=
                            self.video_process_object.process_video_data)
        self.video_processor_thread.start()

        self.job_broker_object = JobBroker(self.ring_buffer,
                        release_function=self.release)
        

    def release(self):
        """
        self.job_broker_thread = threading.Thread(target=   
                            self.job_broker_object.process_jobs)
        self.job_broker_thread.start()
        """
        print("new")
        self.video_capture_object.release()
        self.video_display_object.release()
        self.video_process_object.release()
        self.job_broker_object.release()

if __name__ == "__main__":
    DataAcquisition()
