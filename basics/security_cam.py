"""
SecurityCam: This class is a tester for image processing. With this class the camera should 
                work like a security camera and record a video if a movement is tracked. 

Requirements:

Links:
    - https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                           Date:
v0.0.1      (AS) First initialize. ...                                      11.08.2020\n
    
Attributes:
-----------
recording_name : str
    representative name for clear attribution of the recording
fps : int
    frames per second. 
videolength_s : int
    length of the video to record in seconds. 
videolength_frames : int
    number of frames used to record video with given length.
max_tries : int
    max number of tries to open camera/VideoWriter. 
connection_str : str 
    camera url to connect to like: "rtsp://USERNAME:PASSWORD@IP:PORT"
"""
from cv2 import cv2 
import imutils
import os
import datetime

class SecurityCam:
    recording_name = "SecurityCam"
    fps = 20
    videolength_s = 10
    videolength_frames = fps * videolength_s
    max_tries = 5
    connection_str = "rtsp://admin:admin@192.168.8.22:8554"
    border_notDetected = 10         # frames to record after motion is not detected anymore
    border_resetFirstFrame = 1200   # every minute
    border_contourArea = 500        # minimum area size to recognize motion

    def __init__(self):
        """
        """
        parentDir_path = os.path.dirname(os.path.realpath(__file__))
        recordsDir_name = "Recordings"
        self.recordsDir_path = os.path.join(parentDir_path, recordsDir_name)
        if not os.path.exists(self.recordsDir_path):
            os.mkdir(self.recordsDir_path)
        
        # initialize video capture
        self.capture = cv2.VideoCapture(self.connection_str)
        
        # initialize video writer
        self.frame_width = int(self.capture.get(3))
        self.frame_height = int(self.capture.get(4))

        self.writer = cv2.VideoWriter()
        
    def generateFilePath(self):
        currentDateTime = datetime.datetime.now()
        self.file_name = "{0}_{1}-{2:02d}-{3:02d}_{4:02d}-{5:02d}-{6:02d}.avi".format(self.recording_name, 
                                        currentDateTime.year, 
                                        currentDateTime.month,
                                        currentDateTime.day,
                                        currentDateTime.hour,
                                        currentDateTime.minute,
                                        currentDateTime.second)
        return os.path.join(self.recordsDir_path, self.file_name)
        

    def loop_forever(self):
        firstFrame = None
        notDetectedCounter = self.border_notDetected
        frameCounter = 0 
        motionDetected = False
        
        while True:
            if(self.capture.isOpened()):
                ret, frame = self.capture.read()
                frameCounter += 1
                # text = "Unoccupied"
                if ret == True:
                    
                    # resize the frame, convert it to grayscale, and blur it
                    scaledFrame = imutils.resize(frame, width=500)
                    gray = cv2.cvtColor(scaledFrame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.GaussianBlur(gray, (21, 21), 0)

                    if firstFrame is None:
                        firstFrame = gray
                        continue

                    # compute the absolute difference between the current frame and
                    # first frame
                    frameDelta = cv2.absdiff(firstFrame, gray)
                    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
                    # dilate the thresholded image to fill in holes, then find contours
                    # on thresholded image
                    thresh = cv2.dilate(thresh, None, iterations=2)
                    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
                    cnts = imutils.grab_contours(cnts)
                    motionDetected = False
                    for c in cnts:
                        if cv2.contourArea(c) > self.border_contourArea:
                            motionDetected = True
                            notDetectedCounter = 0
                        

                    if motionDetected or notDetectedCounter < self.border_notDetected:
                        #print("schreibe Datei")
                        # write frame to output file
                        if not self.writer.isOpened():
                            # setup file writer if is not opened
                            file_path = self.generateFilePath()
                            frame_width = int(self.capture.get(3))
                            frame_height = int(self.capture.get(4))
                        
                            fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
                            self.writer = cv2.VideoWriter(file_path, fourcc, self.fps, (frame_width, frame_height))
                        self.writer.write(frame)
                        notDetectedCounter += 1
                    else:
                        if self.writer.isOpened():
                            self.writer.release()
                        
                        if frameCounter >= self.border_resetFirstFrame:
                            firstFrame = gray
                            frameCounter = 0 
                            print("reset")

                    """
                    # loop over the contours
                    for c in cnts:
                        # if the contour is too small, ignore it
                        if cv2.contourArea(c) < 500:#args["min_area"]:
                            continue
                        # compute the bounding box for the contour, draw it on the frame,
                        # and update the text
                        (x, y, w, h) = cv2.boundingRect(c)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        text = "Occupied"

                   # draw the text and timestamp on the frame
                    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
                    # show the frame and record if the user presses a key
                    #"""

                    # Bilder anzeigen
                    
                    cv2.imshow("Security Feed", gray)
                    cv2.imshow("Thresh", thresh)
                    cv2.imshow("Frame Delta", frameDelta)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    #"""
                    # print(counter_frames)
                    # recording completed
                    #if counter_frames >= self.videolength_frames:
                        #logging.info("Recording completed.")
                        #self.mqtt.sendProcessMessage(self.user_name, self.mqtt.info_list[self.module_name]["RecordedFile"],file=self.file_name)
                    #    break

                else:
                    if not self.capture.isOpened():
                        #self.mqtt.sendProcessMessage(self.user_name, self.mqtt.info_list[self.module_name]["RecordLostConnection"],file=self.file_name)
                        #logging.error("Lost connection to camera.")
                        pass
                    #self.mqtt.sendProcessMessage(self.user_name, self.mqtt.info_list[self.module_name]["RecordFileError"],file=self.file_name)
                    #logging.error("Can not read from VideoCapture.")
                    break
        cv2.destroyAllWindows()

if __name__ == '__main__':
    cam = SecurityCam()
    cam.loop_forever()