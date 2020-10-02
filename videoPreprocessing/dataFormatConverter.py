"""
FormatConverter: 

Requirements:
    - cv2 (openCV)

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                           Date:
v0.0.1      (AS) First initialize. Added method to convert avi files to     31.08.2020\n
                    png.
    
Attributes:
-----------
possible_input_formats : list
    list of strings that are possible as input formats
possible_output_formats : list
    list of strings that are possible as output formats
input_format : str
    file format of given file
output_format : str
    file format to convert to
videolength_frames : int
    number of frames used to record video with given length.
max_tries : int
    max number of tries to open camera/VideoWriter. 
connection_str : str 
    camera url to connect to like: "rtsp://USERNAME:PASSWORD@IP:PORT"
"""
from cv2 import cv2 
import os, glob

class FormatConverter:
    possible_input_video_formats = ["avi", "mp4"]
    possible_input_image_formats = ["png"]
    possible_input_formats = possible_input_video_formats + possible_input_image_formats

    possible_output_video_formats = ["avi", "mp4"]
    possible_output_image_formats = ["png"]
    possible_output_formats = possible_output_video_formats + possible_output_image_formats

    fps = 20

    def __init__(self, input_format = "avi", output_format = "png", dirPath = None, filePath = ""):
        """
        """
        if self.possible_input_formats.count(input_format) > 0:
            self.input_format = input_format
        else:
            print("input format not supported")
        if self.possible_output_formats.count(output_format) > 0:
            self.output_format = output_format
        else:
            print("output format not supported")
            quit()
        self.dirPath = dirPath
        self.filePath = filePath

    def convertFiles(self):
        if self.dirPath == None:
            self.convertSingleFile(self.filePath)
        else:
            if os.path.exists(self.dirPath):
                filter_str = "*." + self.input_format
                filter_path = os.path.join(self.dirPath, filter_str)
                file_paths = glob.glob(filter_path)

                for path in file_paths:
                    self.convertSingleFile(path)
                return len(file_paths)

            else:
                print("Directory does not exists.")
                return -1

    def convertSingleFile(self, filePath):
        if (self.possible_input_video_formats.count(self.input_format) > 0 and 
                self.possible_output_image_formats.count(self.output_format) > 0):
            self.convert_video_to_images(filePath)
        if (self.possible_input_video_formats.count(self.input_format) > 0 and 
                self.possible_output_video_formats.count(self.output_format) > 0):
            self.convert_video_to_video(filePath)

    def convert_video_to_images(self, filePath):
        capture = cv2.VideoCapture(filePath)

        basePath = os.path.dirname(filePath)
        imageDirPath = os.path.join(basePath, "Images")
        if not os.path.exists(imageDirPath):
            os.mkdir(imageDirPath)
        os.chdir(imageDirPath) 

        videoNameLong = os.path.basename(filePath)
        videoName = videoNameLong.split(".")[0]
        
        print("Converting file", videoNameLong, "to", self.output_format, "images")

        counter = 0
        while capture.isOpened:
            ret, frame = capture.read()
            if ret == False: break
            filename = "{}_{}.{}".format(videoName, counter,self.output_format)
            counter += 1
            cv2.imwrite(filename, frame) 
            
            """
            cv2.imshow(videoName, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            #"""
        print("converted ", counter, " frames to images")
        cv2.destroyAllWindows()
        capture.release()

    def convert_video_to_video(self, filePath):
        capture = cv2.VideoCapture(filePath)
        
        frame_width  = int(capture.get(3))  # float
        frame_height = int(capture.get(4))  # float

        basePath = os.path.dirname(filePath)
        videoDirPath = os.path.join(basePath, self.output_format)
        if not os.path.exists(videoDirPath):
            os.mkdir(videoDirPath)
        os.chdir(videoDirPath) 

        videoNameLong = os.path.basename(filePath)
        videoName = videoNameLong.split(".")[0]
        
        file_path = os.path.join(videoDirPath, videoName)+"."+self.output_format
        print(file_path)
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        writer = cv2.VideoWriter(file_path, 
                                        fourcc, 
                                        self.fps, 
                                        (frame_width, frame_height))
        
        print("Converting file", videoNameLong, "to", self.output_format, "video")

        while capture.isOpened:
            ret, frame = capture.read()
            if ret == False: break
                
            writer.write(frame)

        cv2.destroyAllWindows()
        capture.release()
        writer.release()
        

if __name__ == '__main__':
    #formater = FormatConverter(input_format="mp4",output_format="png", dirPath="C:/Users/swms-hit/Schiller/DIH4CPS-PYTESTS/Testlauf_24-08-2020/Shrimp_detect_short")
    #formater = FormatConverter(input_format="avi",output_format="png", filePath="C:/Users/swms-hit/Schiller/DIH4CPS-PYTESTS/Testlauf_24-08-2020/Shrimp_detect/test1_2020-08-24_00-02-02.avi")
    formater = FormatConverter(input_format="avi",output_format="png", dirPath=os.path.abspath("C:/Users/swms-hit/Schiller/DIH4CPS-PYTESTS/videoPreprocessing/video_files/2020-09-30"))
    formater.convertFiles()