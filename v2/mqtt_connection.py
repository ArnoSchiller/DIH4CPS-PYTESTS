"""
MQTTConnection: This class rules the connection to the MQTT broker (iotstack).

Requirements:
- paho (mqtt api): pip install paho-mqtt (see https://pypi.org/project/paho-mqtt/)

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v1.0.0
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                   Date:
v0.0.1           See v1 (mqtt_connection) for more.    	            07.08.2020\n
v1.0.0      (AS) Updated to version 2.                              07.09.2020\n
v1.0.1      (AS) Updated code in case there is no internet          07.09.2020\n
                connction by using try and except.                            \n

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

status_list : dict
    list of possible informations, warnings and errors to send to MQTT server 
    (API for WebcamCapture and CloudConnection).
"""

import paho.mqtt.client as mqtt
import datetime, time
from configuration import *

class MQTTConnection:
    """
    This class rules the connection to the MQTT broker (iotstack).
    """
    # SSL/TLS1.2 aktivieren. Pub auf den Topic IOT/{irgendwas}
    
    mqtt_host = global_mqtt_host
    user_name = global_mqtt_user_name
    password = global_mqtt_password

    port = global_mqtt_port
    keepalive = 60

    local_mqtt = global_mqtt_usinglocalhost

    topic = "IOT/test"

    status_list = {
        "WebcamCapture" : {
            # Open camera
            "ClosedCamera"          : "modul=WebcamCapture,process=OpenCamera status=0",
            "OpeningCamera"         : "modul=WebcamCapture,process=OpenCamera status=1",
            "OpenedCamera"          : "modul=WebcamCapture,process=OpenCamera status=2",

            "OpeningCameraFailed"   : "modul=WebcamCapture,process=OpenCamera status=4",

            "OpenCameraError"       : "modul=WebcamCapture,process=OpenCamera status=10",
        },

        "VideoRecorder" : {
            # Open writer
            "ClosedWriter"          : "modul=VideoRecorder,process=OpenWriter status=0",
            "OpeningWriter"         : "modul=VideoRecorder,process=OpenWriter status=1",
            "OpenedWriter"          : "modul=VideoRecorder,process=OpenWriter status=2",

            "OpenFileWriterFailed"  : "modul=VideoRecorder,process=OpenWriter status=4",

            "OpenWriterError"       : "modul=VideoRecorder,process=OpenWriter status=10",

            # Recording file
            "RecordingFile"         : "modul=VideoRecorder,process=RecordFile status=1",
            "RecordedFile"          : "modul=VideoRecorder,process=RecordFile status=2",

            "RecordLostConnection"  : "modul=VideoRecorder,process=RecordFile status=9",
            "RecordFileError"       : "modul=VideoRecorder,process=RecordFile status=10",
        },

        "CloudConnection" : {
            # Upload files 
            "UploadReady"       	: "modul=CloudConnection,process=UploadFile status=0",
            "UploadingFile"         : "modul=CloudConnection,process=UploadFile status=1",
            "UploadedFile"          : "modul=CloudConnection,process=UploadFile status=2",

            "ClientError"           : "modul=CloudConnection,process=UploadFile status=7",
            "FileNotFound"          : "modul=CloudConnection,process=UploadFile status=8",
            "NoCredentials"         : "modul=CloudConnection,process=UploadFile status=9",
            "UploadError"           : "modul=CloudConnection,process=UploadFile status=10",

            # connecting to server
            "DisconnectedServer"    : "modul=CloudConnection,process=ConnectServer status=0",
            "ConnectingToServer"    : "modul=CloudConnection,process=ConnectServer status=1",
            "ConnectedToServer"     : "modul=CloudConnection,process=ConnectServer status=2",

            "ConnectServerError"    : "modul=CloudConnection,process=ConnectServer status=10"
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

        self.reconnect()
    

    def reconnect(self):
        if self.local_mqtt:
            self.client.connect("localhost", 1883, 60)
        else: 
            try:
                self.client.connect(self.mqtt_host, self.port, self.keepalive)
            except Exception:
                pass
        self.client.loop_start()

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
        """
        if self.client.is_connected():
            try:
                return self.client.publish("IOT/test", message)
            except Exception:
                return False
        else: 
            self.reconnect()
            return self.client.publish("IOT/test", message)
        """

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
