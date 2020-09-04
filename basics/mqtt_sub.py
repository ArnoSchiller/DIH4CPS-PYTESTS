#!/usr/bin/env python

# run C:\Program Files\mosquitto\mosquitto.exe first
# download: https://mosquitto.org/download/
#
# into terminal:    cd C:\Program Files\mosquitto
#                   mosquitto_sub -t IOT/test1 
# (https://www.youtube.com/watch?v=wKgXQwY7oCU)

import paho.mqtt.client as mqtt # pip install paho-mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe("#")

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.8.131", 1883, 60)

client.loop_forever()