"""
job_broker: This module is used to handle internal message exchange. 

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY                                                     \n
Version:    (Author) Description:                                   Date:     \n
v1.0.0      (AS) First initialize. Using Timer class to replace     14-09-2020\n  
                the usage of crontab.                                         \n
"""

import threading, datetime

from VideoHandling.video_record import record_video


class JobTimer:
    """ 
    This class subscibes the local mqtt and starts the  
    
    Attributes:
    ----------- 
    ring_buffer : RingBuffer
        used RingBuffer including captured video frames
    video_length_s : int
        length of the video to record
    duration_s : int
        duration time in seconds the recording task should be called 
    """

    def __init__(self, ring_buffer, video_length=10, duration=60*30):
        """ Setup buffer and internal parameters. 
        
        Parameters:
        ----------- 
        ring_buffer : RingBuffer
            used RingBuffer including captured video frames
        video_length : int
            length of the video to record in seconds, default = 10 seconds
        duration : int
            duration time in seconds the recording task should be called,
            default = every 30 minutes 
        """
        self.ring_buffer = ring_buffer
        self.video_length_s = video_length
        self.duration_s = duration

        self.isRunning = True
        
        self.process_job()

    def process_job(self):
        """
        Will start the task to record a video with a specific length.  
        """
        if self.isRunning:
            threading.Timer(self.duration_s, self.process_job).start()
            print("Job: ", datetime.datetime.now())
            record_video(self.ring_buffer, length_seconds=self.video_length_s)

    def release(self):
        self.isRunning = False

    def on_connect(self, client, userdata, flags, rc):
        """ Called when the client connected. 
        """
        print("Connected with result code " + str(rc))
        client.subscribe("IOT/internal")

    def on_message(self, client, userdata, msg):
        """ Called when the client recieves a message from the broker. 
        """
        print(msg.topic + " " + str(msg.payload))
        message =  str(msg.payload)
        message = message[2:len(message)-1]
        self.process_job(message)

if __name__ == "__main__":
    print("Run data_acquisation.")
