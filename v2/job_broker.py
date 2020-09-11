"""
VideoProcessor: 

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY                                                                       \n
Version:    (Author) Description:                                           Date:     \n
v1.0.0      (AS) First initialize.                                          09-09-2020\n
v1.0.1      (AS) Tested to use a Queue to exchange internal messages.           10-09-2020\n 
                Maybe use MessageQueue (https://github.com/ingresse/message-queue-python)                    
v1.0.2      (AS) Build job handler using local mqtt.           10-09-2020\n                   
"""

import threading

from global_variables import get_job_queue
from VideoHandling.video_record import VideoRecorder, record_video
import paho.mqtt.client as mqtt # pip install paho-mqtt



class JobBroker:
    """ 
    This class subscibes the job queue and starts jobs. 
    
    Attributes:
    ----------- 
    """
    latest_job = ""

    def __init__(self, ring_buffer):
        """ Setup video capture and video writer. 
        """
        print("JobBroker erstellt")

        self.ring_buffer = ring_buffer

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect("localhost", 1883, 60)

        self.client.loop_forever()

    def process_job(self, message):
        if message == self.latest_job:
            return
        tag_set, field_set = message.split(" ")
        tag_set = tag_set.split(",")
        field_set = field_set.split(",")
        print(tag_set)
        print(field_set)

        if tag_set[0] == "job":
            if tag_set.count("type=record") > 0:
                video_len = 5
                for field in field_set:
                     name, value = field.split("=")
                     if name == "videoLength":
                         video_len = int(value)
                record_video(self.ring_buffer, length_seconds=video_len)
        self.latest_job = message

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("IOT/internal")

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        message =  str(msg.payload)
        message = message[2:len(message)-1]
        self.process_job(message)

if __name__ == "__main__":
    print("Run data_acquisation.")
