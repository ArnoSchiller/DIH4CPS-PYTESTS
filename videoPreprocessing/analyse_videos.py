import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import threading
import os, glob
import cv2
import time

from trained_model import Model

class VideoAnalyser():
    capture = None
    update_needed = False
    border_contourArea = 1500
    count = 0 
    def __init__(self):

        self.shrimp_model = Model()

        cur_dir = os.path.dirname(__file__)
        filter_str = "*.avi"
        filter_path = os.path.join(cur_dir,"video_files", filter_str)
        self.file_paths = glob.glob(filter_path)
        self.video_index = 0
        self.change_capture()

        if self.capture is None: quit()

        while self.capture.isOpened():
            ret, image = self.capture.read()
            if ret:
                num_shrimp, image_pred = self.shrimp_model.predict(image)
                """
                cv2.imshow("predimg", image_pred)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()  
                """
                #print(num_shrimp)
        """
        # create subplot grid
        self.num_cols = 4
        self.num_rows = 1
        self.grid_list = []
        for i in range(self.num_cols * self.num_rows):
            self.grid_list.append(plt.subplot(self.num_rows,self.num_cols,i + 1))
            self.grid_list[i].axis("off")

        #create two image plots
        self.image_list = []
        first_capture, _ = self.convert_frame(first_frame=self.first_frame)
        #self.first_frame = first_capture[0]
        #self.current_frame = self.first_frame  
        self.image_list.append(self.grid_list[0].imshow(first_capture[0]))
        self.image_list.append(self.grid_list[1].imshow(first_capture[1], cmap="gray"))
        self.image_list.append(self.grid_list[2].imshow(first_capture[2], cmap="gray"))
        self.image_list.append(self.grid_list[3].imshow(first_capture[3], cmap="gray"))

        
        #threading.Thread(target=self.read_input).start()

        ani = FuncAnimation(plt.gcf(), self.update, interval=10)
        plt.show()
        """
    
    def change_capture(self):
        print("reset")
        if self.video_index >= len(self.file_paths):
            quit()
        video_path = self.file_paths[self.video_index]
        print(video_path)
        self.capture = cv2.VideoCapture(video_path)
        self.video_index += 1
        self.count = 0
        
    def grab_frame(self):
        if not self.capture.isOpened():
            self.change_capture()
        frame = None
        while frame is None:
            ret,frame = self.capture.read()
            if not ret:
                self.change_capture()
        return frame

    def convert_frame(self, frame=None, first_frame=None):
        detected = False
        while not detected:
            self.count += 1
            frame = self.grab_frame()
            if frame is None:
                continue
            images, contours = self.getIntenseContours(frame, first_frame)
            if len(contours) > 0:
                #print(self.count)
                detected = True
            else: 
                pass
                #cv2.imshow("frame", frame)
                #time.sleep(0.1)
                #cv2.waitKey(1)
        return images, contours
        
        
    def read_input(self):  
        while True:
            if not self.update_needed:
                user_input = input("Press 's' to save frame, 'n' to open next frame or 'q' to quit.")
                print(user_input)
                if user_input == "q":
                    quit() 
                if user_input == "n":
                    self.update_needed = True 
                if user_input == "s":
                    print("saveFrameS")
                    self.update_needed = True 


    def update(self, i):
        self.update_needed = True
        if self.update_needed:
            frame_list, contours = self.convert_frame(first_frame=self.first_frame)

            for i in range(len(frame_list)):
                if i == 0:
                    frame_list[i] = cv2.cvtColor(frame_list[i], cv2.COLOR_RGB2BGR)
                self.image_list[i].set_data(frame_list[i])
                """
                for c in contours:
                    x, y, w, h = cv2.boundingRect(c)
                    # Create a Rectangle patch
                    rect = patches.Rectangle((x,y),w,h,linewidth=1,edgecolor='r',facecolor='none')
                    # Add the patch to the Axes
                    self.grid_list[i].add_patch(rect)
                """
            #print("erkannte Konturen: ", len(contours))
            if len(contours) > 0:
                self.save_image(frame_list[0], self.file_paths[self.video_index], self.count)


            self.current_frame = frame_list[0]
            #self.update_needed = False

    
    def getIntenseContours(self, frame, first_frame=None):
        rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        gray_image = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)

        gray_image_sub = gray_image
        if not first_frame is None: 
        #first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
            cv2.subtract(gray_image_sub, first_frame)
        
        #if not self.first_frame is None:
        #    gray_first = cv2.cvtColor(self.first_frame, cv2.COLOR_RGB2GRAY)
        #    gray_image = gray_image - gray_first
        ret,thresh_image = cv2.threshold(gray_image,130,255,cv2.THRESH_BINARY)

        # find contours and get the external one
        contours, hier = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #image, contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE,
        #                cv2.CHAIN_APPROX_SIMPLE)

        # with each contour, draw boundingRect in green
        # a minAreaRect in red and
        # a minEnclosingCircle in blue
        filtered_contours = []
        for c in contours:
            if cv2.contourArea(c) > self.border_contourArea:
                """
                # get the bounding rect
                x, y, w, h = cv2.boundingRect(c)
                # draw a green rectangle to visualize the bounding rect
                #cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Create a Rectangle patch
                rect = patches.Rectangle((x,y),w,h,linewidth=1,edgecolor='r',facecolor='none')

                # Add the patch to the Axes
                grid_list[3].add_patch(rect)
                """
                filtered_contours.append(c)
        return [frame, gray_image, first_frame, thresh_image], filtered_contours

    def save_image(self, frame, video_file_path, index):
        frame = cv2. cvtColor(frame, cv2.COLOR_RGB2BGR)
        base_path = os.path.dirname(video_file_path)

        video_name_long = os.path.basename(video_file_path)
        video_name = video_name_long.split(".")[0]

        folder_path = os.path.join(base_path, "Images")
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        file_name = video_name + "_" + str(index) + ".png"
        file_path = os.path.join(folder_path, file_name)
        # print(file_path)
        cv2.imwrite(file_path, frame)

if __name__ == '__main__':
    va = VideoAnalyser()
