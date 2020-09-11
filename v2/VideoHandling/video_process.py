"""
VideoProcessor: 

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY                                                               \n
Version:    (Author) Description:                                   Date:     \n
v1.0.0      (AS) First initialize.                                  02-09-2020\n
v1.0.1      (AS) Included parts of the security camera to test the  10-09-2020\n
                programm workflow.                                            \n
v1.0.2      (AS) Tested the security camera. Works fine.            10-09-2020\n
                programm workflow.                                            \n

"""

import threading
import cv2,imutils
from VideoHandling.video_record import VideoRecorder

class VideoProcessor:
    """ 
    This class writes the captured frames from the buffer into video files.
    
    Attributes:
    ----------- 
    """
    border_notDetected = 20         # frames to record after motion is not detected anymore
    border_resetFirstFrame = 1200   # every minute
    border_contourArea = 500        # minimum area size to recognize motion

    def __init__(self, ring_buffer):
        """ Setup video capture and video writer. 
        """
        self.ring_buffer = ring_buffer
        print("Prozessor erstellt")

    def process_video_data(self):
        print("Start")
        self.security_cam()
        """
        self.isRunning = True
        counter = 0
        frames_list = []
        while self.isRunning:
            counter += 1
            frame = self.ring_buffer.get_next_element()
            """"""
            if counter >= 40 and counter < 80:
                frames_list.append(frame)
            print(counter)
            if counter == 80:
                buffer_dict = {}
                buffer_dict['frames'] = frames_list
                buffer_dict['timestamp'] = ""
                vr = VideoRecorder(buffer_dict)
            """

    
    def security_cam(self):
        print("Start")
        firstFrame = None
        notDetectedCounter = self.border_notDetected
        frameCounter = 0 
        motionDetected = False
        frames_list = []
        
        while True:
            
            frame = self.ring_buffer.get_next_element()[1]
                
            frameCounter += 1
                    
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
                print("Bewegung erkannt")
                # write frame to output file
                frames_list.append(frame)
                notDetectedCounter += 1
            else:
                if not frames_list == []:
                    vr = VideoRecorder(buffer=frames_list)
                    frames_list.clear()
                        
            if frameCounter >= self.border_resetFirstFrame:
                firstFrame = gray
                frameCounter = 0 
                print("reset")

            # Bilder anzeigen
            """
            cv2.imshow("Security Feed", gray)
            cv2.imshow("Thresh", thresh)
            cv2.imshow("Frame Delta", frameDelta)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            #"""
               
        cv2.destroyAllWindows()

    def release(self):
        self.isRunning = False


if __name__ == "__main__":
    print("Run data_acquisation.")
