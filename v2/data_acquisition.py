"""
This module is the main component of the data acquisition and starts every
needed process as a thread. 
"""
import os, sys
import datetime, time
import threading 

currentdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,currentdir) 

from VideoHandling.ring_buffer import RingBuffer
from VideoHandling.webcam_capture import WebcamCapture
from VideoHandling.video_display import VideoDisplay
from VideoHandling.video_process import VideoProcessor
from VideoHandling.video_record import direct_record_video

from job_timer import JobTimer

from configuration import *

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

    with_display    = global_with_video_display
    with_process    = global_with_video_process
    with_direct_rec = global_with_direct_rec
    with_job_timer  = global_with_job_timer

    video_capture_object = None
    video_capture_thread = None

    video_display_object = None
    video_display_thread = None

    video_process_object = None
    video_process_thread = None

    job_broker_object = None

    def __init__(self):
        """ Setup video capture, video writer and if needed the video display 
        object. Also setup the job broker to rule the internal communication for job exchange.
        """
        self.ring_buffer = RingBuffer()
        
        self.video_capture_object = WebcamCapture(self.ring_buffer)
        self.video_capture_thread = threading.Thread(target=
                            self.video_capture_object.capture_frames)
        self.video_capture_thread.start()
        
        if self.with_process:
            self.video_process_object = VideoProcessor(self.ring_buffer)
            self.video_processor_thread = threading.Thread(target=
                            self.video_process_object.process_video_data)
            self.video_processor_thread.start()
        
        if self.with_display:
            self.video_display_object = VideoDisplay(self.ring_buffer)
            self.video_display_thread = threading.Thread(target=
                                self.video_display_object.display_frames)
            self.video_display_thread.start()

        if self.with_job_timer:    
            self.job_timer_object = JobTimer(ring_buffer=self.ring_buffer,
                                    video_length=global_record_video_length_s,
                                    duration=global_record_frequency_s)
        
        if self.with_direct_rec:
            direct_record_video(self.ring_buffer, length_seconds=60*60)
    
    def check_process_status(self):
        if not self.video_capture_thread.is_alive():
            self.video_capture_object.is_running = True
            self.video_capture_thread = threading.Thread(target=
                            self.video_capture_object.capture_frames)
            self.video_capture_thread.start()

        if not self.video_process_thread.is_alive():
            self.video_process_object.isRunning = True
            self.video_processor_thread = threading.Thread(target=
                            self.video_process_object.process_video_data)
            self.video_processor_thread.start()

        if not self.job_timer_object.isRunning:
            self.job_timer_object = JobTimer(ring_buffer=self.ring_buffer,
                                    video_length=global_record_video_length_s,
                                    duration=global_record_frequency_s)

        if self.with_display:
            if not self.video_display_thread.is_alive():
                self.video_display_object.is_running = True
                self.video_display_thread = threading.Thread(target=
                                self.video_display_object.display_frames)
                self.video_display_thread.start()

    def release(self):
        self.video_capture_object.release()
        self.video_display_object.release()
        self.video_process_object.release()
        self.job_broker_object.release()


if __name__ == "__main__":
    da = DataAcquisition()
    #da.check_process_status()
