"""
MQTTConnection: This class rules the connection to the MQTT broker (iotstack).

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
keepalive : int
    maximum period in seconds allowed between communications with the broker. 
    If no other messages are being exchanged, this controls the rate at which 
    the client will send ping messages to the broker

local_mqtt : bool
    True    - connect to local MQTT
    False   - connect to mqtt_host

info_list : dict
    list of possible informations to send to MQTT server 
    (API for WebcamRecorder and CloudConnection).
warning_list : dict
    list of possible warnings to send to MQTT server 
    (API for WebcamRecorder and CloudConnection).
error_list : dict
    list of possible errors to send to MQTT server 
    (API for WebcamRecorder and CloudConnection).
"""

import paho.mqtt.client as mqtt
import datetime, time
from configuration import *

class MQTTConnection:
    # SSL/TLS1.2 aktivieren. Pub auf den Topic IOT/{irgendwas}
    mqtt_host = global_mqtt_host
    user_name = global_mqtt_user_name
    password = global_mqtt_password

    port = global_mqtt_port
    keepalive = 60

    local_mqtt = global_mqtt_usinglocalhost

    topic = "IOT/test"

    info_list = {
        "WebcamRecorder" : {
            # Open camera
            "ClosedCamera"      : "modul=WebcamRecorder,process=OpenCamera status=0",
            "OpeningCamera"     : "modul=WebcamRecorder,process=OpenCamera status=1",
            "OpenedCamera"      : "modul=WebcamRecorder,process=OpenCamera status=2",
        
            # Open writer
            "ClosedWriter"      : "modul=WebcamRecorder,process=OpenWriter status=0",
            "OpeningWriter"     : "modul=WebcamRecorder,process=OpenWriter status=1",
            "OpenedWriter"      : "modul=WebcamRecorder,process=OpenWriter status=2",

            # Recording file
            "RecordingFile"     : "modul=WebcamRecorder,process=RecordFile status=1",
            "RecordedFile"      : "modul=WebcamRecorder,process=RecordFile status=2"
        },

        "CloudConnection" : {
            # Upload files 
            "UploadingFile" : "modul=CloudConnection,process=UploadFile status=1",
            "UploadedFile"  : "modul=CloudConnection,process=UploadFile status=2",

            # connecting to server
            "DisconnectedServer"    : "modul=CloudConnection,process=ConnectServer status=0",
            "ConnectingToServer"    : "modul=CloudConnection,process=ConnectServer status=1",
            "ConnectedToServer"     : "modul=CloudConnection,process=ConnectServer status=2"
        }
    }
    warning_list = {
        "WebcamRecorder" : {
            # Open camera
            "OpeningCameraFailed"   : "modul=WebcamRecorder,process=OpenCamera status=4",
            # Open writer
            "OpenFileWriterFailed"  : "modul=WebcamRecorder,process=OpenWriter status=4"
        }
    }

    error_list = {
        "WebcamRecorder" : {
            # Open camera
            "OpenCameraError"           : "modul=WebcamRecorder,process=OpenCamera status=10",
            # Open writer
            "OpenWriterError"           : "modul=WebcamRecorder,process=OpenWriter status=10",
            # Record file 
            "RecordLostConnection"      : "modul=WebcamRecorder,process=RecordFile status=9",
            "RecordFileError"           : "modul=WebcamRecorder,process=RecordFile status=10"
        },

        "CloudConnection" : {
            # Upload files 
            "ClientError"   : "modul=CloudConnection,process=UploadFile status=7",
            "FileNotFound"  : "modul=CloudConnection,process=UploadFile status=8",
            "NoCredentials" : "modul=CloudConnection,process=UploadFile status=9",
            "UploadError"   : "modul=CloudConnection,process=UploadFile status=10",

            # connecting to server
            "ConnectServerError" : "modul=CloudConnection,process=ConnectServer status=10"
        }
    }

    def __init__(self):
        """ Setup the MQTT connection. 
        """
        self.client = mqtt.Client()
        self.client._username = self.user_name
        self.client._password = self.password
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.tls_set()
    
        if self.local_mqtt:
            self.client.connect("localhost", 1883, 60)
        else:
            self.client.connect(self.mqtt_host, self.port, self.keepalive)
        self.client.loop_start()
        time.sleep(2)

    def testloop(self):
        while True:
            msg = "test"
            print(msg)
            res = self.sendMessage(msg)
            print(res)
            time.sleep(5)

    def sendProcessMessage(self, user, message, **options):
        msg = "process,user={},".format(user)
        if not options.get("file")  == None:
            msg += "file={},".format(options.get("file")) 
        msg += "{}".format(message)
        print(msg)
        res = self.sendMessage(msg)

    def sendMessage(self, message):
        return self.client.publish("IOT/test", message)

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server.
    see getting started (https://pypi.org/project/paho-mqtt/)
    """
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("IOT/#")

def on_message(client, userdata, msg):
    """ The callback for when a PUBLISH message is received from the server.
    see getting started (https://pypi.org/project/paho-mqtt/)
    """
    print(msg.topic+" "+str(msg.payload))

if __name__ == '__main__':
    conn = MQTTConnection()
    #conn.testloop()
    conn.sendMessage("temperature,location=CPU,modul=SystemMonitoring,user=test1 temperature=20")
