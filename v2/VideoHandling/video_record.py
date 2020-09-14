"""
VideoRecorder: This module writes the captured frames from the buffer into a 
video file.

Requirements:
- opencv: pip install opencv-python 
    see - https://www.learnopencv.com/install-opencv-4-on-raspberry-pi/
        - https://medium.com/@aadeshshah/pre-installed-and-pre-configured-raspbian-with-opencv-4-1-0-for-raspberry-pi-3-model-b-b-9c307b9a993a

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v1.0.0
@license:   ...

VERSION HISTORY                                                               \n
Version:    (Author) Description:                                   Date:     \n
v0.x.x           see v1 (webcam_recorder) for more informations.    02-09-2020\n
v1.0.0      (AS) First initialize. Added code from webcam_display   02-09-2020\n
                and included buffer.                                          \n
v1.0.1      (AS) Added functionality to record a video with a       11-09-2020\n
                specific length.                                              \n
v1.0.2      (AS) Included direct upload to the recording.           14-09-2020\n
"""

import platform
if platform.system() == 'Windows':
    from cv2 import cv2
else:
    import cv2

import os, sys
import threading, datetime
import numpy as np

from configuration import * 
from mqtt_connection import MQTTConnection
from cloud_connection import CloudConnection


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
    recordsDir_name = global_recordsDir_path
    frames_buffer = None

    def __init__(self, 
                buffer=None, 
                timestamp=None, 
                video_name_addition=None,
                direct_upload=True):
        """  
        Setup internal parameters and the mqtt connection (logging). Also 
        setup the video writer and start a thread writing the given frames to 
        file. 
        """
        if buffer == None:
            return

        self.direct_upload = direct_upload

        self.video_name_addition = video_name_addition

        if timestamp == None:
            self.video_timestamp = datetime.datetime.now()
        else:
            self.video_timestamp = timestamp

        if not buffer == None:
            # self.frames_buffer = np.copy(buffer)
            self.frames_buffer = buffer
            self.video_timestamp = datetime.datetime.now()

        self.mqtt_client = MQTTConnection()

        (self.frame_height, self.frame_width, _) = self.frames_buffer[0].shape
        
        #print("h ", self.frame_height, " w ", self.frame_width)
        parentDir_path = os.path.dirname(os.path.realpath(__file__))
        recordsDir_path = os.path.join(parentDir_path, self.recordsDir_name)
        if not os.path.exists(recordsDir_path):
            os.mkdir(recordsDir_path)

        self.file_name = self.generate_filename(self.video_timestamp)
        self.file_path = os.path.join(recordsDir_path, self.file_name)
    
        self.mqtt_client.sendProcessMessage(self.device_name, 
                self.mqtt_client.status_list["VideoRecorder"]["OpeningWriter"])

        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        self.writer = cv2.VideoWriter(  self.file_path, 
                                        fourcc, 
                                        self.fps, 
                                        (self.frame_width, self.frame_height))

        
        self.mqtt_client.sendProcessMessage(self.device_name, 
                self.mqtt_client.status_list["VideoRecorder"]["OpenedWriter"])
                
        th = threading.Thread(target=self.write_frames_to_file)
        th.start()

    def generate_filename(self, used_datetime=datetime.datetime.now()):
        """
        returns a generic filename depending on the current or given datetime.
        """
        filename = self.device_name
        if not self.video_name_addition == None:
            filename += "_"
            filename += self.video_name_addition
        filename += "_{0}-{1:02d}-{2:02d}_{3:02d}-{4:02d}-{5:02d}.avi".format(used_datetime.year, 
                                        used_datetime.month,
                                        used_datetime.day,
                                        used_datetime.hour,
                                        used_datetime.minute,
                                        used_datetime.second)
        return filename

    def write_frames_to_file(self):
        """
        Writes every frame of the frames_buffer into a video file. 
        """
        self.mqtt_client.sendProcessMessage(self.device_name, 
                self.mqtt_client.status_list["VideoRecorder"]["RecordingFile"], 
                file=self.file_name)
        num_frames = 0
        for frame in self.frames_buffer:
            self.writer.write(frame)
            num_frames += 1
        print("Frames: ", num_frames, " Sekunden: ", num_frames/self.fps)
        self.mqtt_client.sendProcessMessage(self.device_name, 
                self.mqtt_client.status_list["VideoRecorder"]["RecordedFile"], 
                file=self.file_name)
        self.release()

        if self.direct_upload:
            cloud_connection = CloudConnection()
            cloud_connection.uploadFileToCloud(file_name=self.file_name)

    def release(self):
        """
        Release everything and close open windows.
        """  
        self.is_running = False 
        self.writer.release()
        self.mqtt_client.sendProcessMessage(self.device_name, 
                self.mqtt_client.status_list["VideoRecorder"]["ClosedWriter"])


def record_video(ring_buffer, length_seconds=None, length_frames=None):
    """
    Function to record a video with a specific length. 
    """
    if not length_seconds == None:
        length_frames = global_camera_fps * length_seconds

    if length_frames == None and length_frames == None:
        return

    print("Recording video with ", length_frames, " frames")

    counter = 0
    frames_list = []

    video_timestamp = datetime.datetime.now()

    while counter < length_frames:
        frame = ring_buffer.get_next_element()[1]
        frames_list.append(frame)
        counter += 1

    VideoRecorder(buffer=frames_list, timestamp=video_timestamp, video_name_addition="cronjob")

    

if __name__ == "__main__":
    print("Run data_acquisation.")
