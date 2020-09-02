#!/usr/bin/env python

# run C:\Program Files\mosquitto\mosquitto.exe first
# download: https://mosquitto.org/download/
#
# into terminal:    cd C:\Program Files\mosquitto
#                   mosquitto_pub -t IOT/test1 -m "MESSAGE" 
# (https://www.youtube.com/watch?v=wKgXQwY7oCU)
import time

import paho.mqtt.client as mqtt # pip install paho-mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect

#client.connect("192.168.8.121", 1883, 60)
client.connect("localhost", 1883, 60)

client.loop_start()

while True:
    time.sleep(2)
    client.publish("test/one", "test")