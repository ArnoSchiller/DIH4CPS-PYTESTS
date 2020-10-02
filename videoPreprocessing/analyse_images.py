import matplotlib.pyplot as plt
import os, glob
import cv2

class ImageAnalyser:
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

        plt.show()

if __name__ == '__main__':
    va = ImageAnalyser()
