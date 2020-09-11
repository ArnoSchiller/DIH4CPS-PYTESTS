"""
WebcamRecorder: This file includes every configuration with global usage. 

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                   Date:
v0.0.1      (AS) First initialize. Added important configurations.  10.08.2020\n
"""

global_user_name = "test1"

# Recorder 
global_recordsDir_name      = "../Recordings"
#global_camera_connection    = "rtsp://192.168.3.70:8554"
#global_camera_connection    = "rtsp://admin:admin@192.168.3.70:8554"
#global_camera_connection    = "rtsp://admin:admin@192.168.8.22:8554"
#global_camera_connection    = "http://root:root@192.168.8.134/mjpg/1/video.mjpg"
global_camera_connection    = "http://root:root@192.168.178.78/mjpg/1/video.mjpg"
global_camera_fps           = 20
global_use_light            = False

# Cloud 
global_cloud_access_key     = "minio"
global_cloud_secret_key     = "miniostorage"
global_cloud_bucket_name    = "test-dih4cps"
global_cloud_url            = "https://minio.dih4cps.swms-cloud.com:9000/"

# MQTT
global_mqtt_usinglocalhost = False

global_mqtt_host        = "demo2.iotstack.co"
global_mqtt_user_name   = "pubclient"
global_mqtt_password    = "tiguitto"
global_mqtt_port        = 8883
