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

from global_variables import get_job_queue
from VideoHandling.video_record import VideoRecorder


class JobBroker:
    """ 
    This class subscibes the job queue and starts jobs. 
    
    Attributes:
    ----------- 
    """

    def __init__(self, ring_buffer):
        """ Setup video capture and video writer. 
        """
        self.ring_buffer = ring_buffer
        print("erstellt")

    def process_jobs(self):
        self.isRunning = True
        print("Start job manage")
        while self.isRunning:
            job = get_job_queue().get()
            job_obtions = job.split(",")
            print(job_obtions)
            

    def release(self):
        self.isRunning = False


if __name__ == "__main__":
    print("Run data_acquisation.")
