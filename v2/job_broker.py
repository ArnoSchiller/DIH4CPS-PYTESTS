"""
job_broker: This module is used to handle internal message exchange. 

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY                                                     \n
Version:    (Author) Description:                                   Date:     \n
v1.0.0      (AS) First initialize.                                  09-09-2020\n
v1.0.1      (AS) Tested to use a Queue to exchange internal         10-09-2020\n 
                messages. Maybe use MessageQueue                              \n
                (https://github.com/ingresse/message-queue-python)            \n      
v1.0.2      (AS) Build job handler using local mqtt.                11-09-2020\n                   
"""

import threading

from VideoHandling.video_record import VideoRecorder, record_video
import paho.mqtt.client as mqtt # pip install paho-mqtt

def do_nothing():
    pass

class JobBroker:
    """ 
    This class subscibes the local mqtt and starts the  
    
    Attributes:
    ----------- 
    client : Client (paho.mqtt.cleint)
        client for mqtt connection
    ring_buffer : RingBuffer
        used RingBuffer including captured video frames
    latest_job : str
        latest started job so one job will not start multiple times
    """
    latest_job = "" 

    def __init__(self, ring_buffer, release_function = do_nothing):
        """ Setup buffer and mqtt client.  
        """
        print("JobBroker erstellt")
        
        self.release_fn = release_function

        self.ring_buffer = ring_buffer

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect("localhost", 1883, 60)

        self.client.loop_start()

    def process_job(self, message):
        """
        Called when a message recieved. Will start the task if the message 
        follows a specific construction.  
        """
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
                
            if tag_set.count("type=general") > 0:
                for field in field_set:
                    name, value = field.split("=")
                    if name == "process" and value == "stop":
                        self.release_fn()

        self.latest_job = message

    def release(self):
        self.client.loop_stop()
        print("stop")

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
