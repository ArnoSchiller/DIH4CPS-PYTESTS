"""
This module is used to send local MQTT messages to the used MQTT API (iotstack).

Requirements:
- paho (mqtt api): pip install paho-mqtt (see https://pypi.org/project/paho-mqtt/)

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                           Date:
v0.0.1      (AS) First initialize. ...                                      07.08.2020\n
    
Attributes:
-----------
mqtt_host : str
    the hostname or IP address of the remote broker
user_name : str
    username of the MQTT client
password : str
    password of the MQTT client
port : int
    the network port of the server host to connect to. Defaults to 1883. 
    Note that the default port for MQTT over SSL/TLS is 8883 so if you are 
    using tls_set() or tls_set_context(), the port may need providing manually

"""
import paho.mqtt.client as mqtt # pip install paho-mqtt
import queue

msg_queue = queue.Queue()


class MQTTTransfer:
    mqtt_host        = "demo2.iotstack.co"
    mqtt_user_name   = "pubclient"
    mqtt_password    = "tiguitto"
    mqtt_port        = 8883 

    def __init__(self):
        self.iotstack_client = mqtt.Client()
        self.iotstack_client._username = self.mqtt_user_name
        self.iotstack_client._password = self.mqtt_password
        self.iotstack_client.tls_set()
        self.iotstack_client.connect(self.mqtt_host, self.mqtt_port, 60)
        self.iotstack_client.loop_start()

        self.iotstack_client.publish("IOT/test2", "test")

        self.local_client = mqtt.Client()
        self.local_client.on_connect = on_connect
        self.local_client.on_message = on_message
        self.local_client.connect("localhost", 1883, 60)
        self.local_client.loop_start()

    def runLoop(self):
        while True:
            msg = msg_queue.get()
            print(msg)
            self.iotstack_client.publish("IOT/test2", msg)
        
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe("#")

def on_message(client, userdata, msg):

    print(msg.topic + " " + msg.payload.decode('ascii'))
    msg_queue.put(msg.payload.decode('ascii'))

if __name__ == '__main__':
    conn = MQTTTransfer()
    conn.runLoop()