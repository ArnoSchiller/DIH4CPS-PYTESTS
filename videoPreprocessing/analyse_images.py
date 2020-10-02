import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os, glob
import cv2

class ImageAnalyser:
    border_contourArea = 200

    def __init__(self):
        #cur_dir = os.path.abspath("C:/Users/swms-hit/Schiller/DIH4CPS-PYTESTS/videoPreprocessing/video_files")
        #image_path = os.path.join(cur_dir, os.path.abspath("2020-09-30/Images/test1_cronjob_2020-09-30_14-33-43_169.png"))
        image_path = os.path.abspath("C:/Users/swms-hit/Schiller/DIH4CPS-PYTESTS/videoPreprocessing/video_files/2020-09-30/Images/test1_cronjob_2020-09-30_14-33-43_170.png")
        
        self.image = cv2.imread(image_path)
        print(self.image.shape)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

        self.num_cols = 2
        self.num_rows = 2

        grid_list = []
        for i in range(self.num_cols * self.num_rows):
            grid_list.append(plt.subplot(self.num_rows,self.num_cols,i + 1))
            grid_list[i].axis("off")

        #create image plots
        self.image_list = []
        self.image_list.append(grid_list[0].imshow(self.image))
        hsv_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
        self.image_list.append(grid_list[1].imshow(hsv_image))
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        self.image_list.append(grid_list[2].imshow(gray_image, cmap='gray'))
        ret,thresh_image = cv2.threshold(gray_image,127,255,cv2.THRESH_BINARY)
        self.image_list.append(grid_list[3].imshow(thresh_image, cmap='gray'))



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
                # get the bounding rect
                x, y, w, h = cv2.boundingRect(c)
                # draw a green rectangle to visualize the bounding rect
                #cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Create a Rectangle patch
                rect = patches.Rectangle((x,y),w,h,linewidth=1,edgecolor='r',facecolor='none')

                # Add the patch to the Axes
                grid_list[3].add_patch(rect)

                filtered_contours.append(c)

        if len(filtered_contours) > 0:
            print("Bild ist interessant")
        plt.show()

if __name__ == '__main__':
    va = ImageAnalyser()
