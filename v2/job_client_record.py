"""
This module is used to send a recording job to the running video handling 
process via local mqtt.
"""

import paho.mqtt.client as mqtt # pip install paho-mqtt
import time, datetime

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

video_len = 2
job_type = "record"

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect

    client.connect("localhost", 1883, 60)

    client.loop_start()
    used_datetime=datetime.datetime.now()
        # generate file name
    timestamp = "{0}-{1:02d}-{2:02d}_{3:02d}-{4:02d}-{5:02d}".format(
                                        used_datetime.year, 
                                        used_datetime.month,
                                        used_datetime.day,
                                        used_datetime.hour,
                                        used_datetime.minute,
                                        used_datetime.second) 

    job = "job,type={0},timestamp={1} videoLength={2}".format(job_type, 
                                                        timestamp, video_len)

    job = "job,type=general process=stop"
    counter = 0
    for i in range(5):
        time.sleep(1)
        client.publish("IOT/internal", job)
        