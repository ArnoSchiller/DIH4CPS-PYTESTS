"""
VideoRecorder: This module writes the captured frames from the buffer into a video file.

Requirements:
- opencv: pip install opencv-python 
    see - https://www.learnopencv.com/install-opencv-4-on-raspberry-pi/
        - https://medium.com/@aadeshshah/pre-installed-and-pre-configured-raspbian-with-opencv-4-1-0-for-raspberry-pi-3-model-b-b-9c307b9a993a

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY                                                                       \n
Version:    (Author) Description:                                           Date:     \n
v0.x.x           see v1 (webcam_recorder) for more informations.            02-09-2020\n
v1.0.0      (AS) First initialize. Added code from webcam_display and       02-09-2020\n
                included buffer.
"""

import platform
if platform.system() == 'Windows':
    from cv2 import cv2
else:
    import cv2

import os, sys
import threading
import datetime

from configuration import * 
from mqtt_connection import MQTTConnection


class VideoRecorder:
    """ 
    This class writes the captured frames from the buffer into video files.
    
    Attributes:
    -----------
    fps : int
        frames per second. 
    """
    fps = global_camera_fps
    device_name = global_user_name
    recordsDir_name = global_recordsDir_name

    def __init__(self, buffer_dict):
        """ Setup video capture and video writer. 
        """
        self.mqtt_client = MQTTConnection()

        self.frames_buffer = buffer_dict['frames']
        self.video_timestamp = buffer_dict['timestamp']
        if self.video_timestamp == "":
            self.video_timestamp = datetime.datetime.now()
        (self.frame_height, self.frame_width, _) = self.frames_buffer[0][1].shape
        
        #print("h ", self.frame_height, " w ", self.frame_width)
        parentDir_path = os.path.dirname(os.path.realpath(__file__))
        recordsDir_path = os.path.join(parentDir_path, self.recordsDir_name)
        if not os.path.exists(recordsDir_path):
            os.mkdir(recordsDir_path)

        self.filename = self.generate_filename(self.video_timestamp)
        self.file_path = os.path.join(recordsDir_path, self.filename)
    
        self.mqtt_client.sendProcessMessage(self.device_name, 
                                            self.mqtt_client.status_list["VideoRecorder"]["OpeningWriter"])

        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        self.writer = cv2.VideoWriter(self.file_path, fourcc, self.fps, (self.frame_width, self.frame_height))

        
        self.mqtt_client.sendProcessMessage(self.device_name, 
                                            self.mqtt_client.status_list["VideoRecorder"]["OpenedWriter"])
                
        th = threading.Thread(target=self.write_frames_to_file)
        th.start()

    def generate_filename(self, used_datetime=datetime.datetime.now()):
        # generate file name
        filename = "{0}_{1}-{2:02d}-{3:02d}_{4:02d}-{5:02d}-{6:02d}.avi".format(self.device_name, 
                                        used_datetime.year, 
                                        used_datetime.month,
                                        used_datetime.day,
                                        used_datetime.hour,
                                        used_datetime.minute,
                                        used_datetime.second)
        return filename

    def write_frames_to_file(self):
        print("start th")
        self.mqtt_client.sendProcessMessage(self.device_name, 
                                            self.mqtt_client.status_list["VideoRecorder"]["RecordingFile"], 
                                            file=self.filename)
        for index, frame in enumerate(self.frames_buffer):
            self.writer.write(frame[1])
        num_frames = index + 1
        print("Frames: ", num_frames, " Sekunden: ", num_frames/self.fps)
        self.mqtt_client.sendProcessMessage(self.device_name, 
                                            self.mqtt_client.status_list["VideoRecorder"]["RecordedFile"], 
                                            file=self.filename)
        self.release()

    def release(self):
        """
        Release everything and close open windows.
        """  
        self.is_running = False 
        self.writer.release()
        self.mqtt_client.sendProcessMessage(self.device_name, 
                                            self.mqtt_client.status_list["VideoRecorder"]["ClosedWriter"])

def record_video(ring_buffer, length_seconds=None, length_frames=None):
    if length_frames == None and length_seconds == None:
        return

    if not length_seconds == None:
        length_frames = global_camera_fps * length_seconds

    counter = 0
    frames_list = []

    while counter < length_frames:
        frame = ring_buffer.get_next_element()
        frames_list.append(frame)
        counter += 1

    buffer_dict = {}
    buffer_dict['frames'] = frames_list
    buffer_dict['timestamp'] = ""
    vr = VideoRecorder(buffer_dict)

    

if __name__ == "__main__":
    print("Run data_acquisation.")
