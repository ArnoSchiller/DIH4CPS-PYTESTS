import os, sys 
import datetime

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs
    
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(current_dir, "..", "models"))

from datasetHandling.dataset_handler import DatasetHandler
from models.trained_model import Model


class VideoAnalyser:

    models_list = [ "tf_API_data1_v01",
                    "tf_API_data2_v01"]

    date_list = [   "2020-10-06",
                    "2020-10-07"]
    
    def __init__(self, model_name):

        if not self.models_list.count(model_name) > 0:
            print("choose a valid model or adapt models_list.")
            quit()

        self.model = Model(model_name=model_name)

        self.data_handler = DatasetHandler()

        self.file_handler = XMLFileConverter(element_name="video_processing")

    def analyse_videos(self):
        for date_str in self.date_list:
            video_files = self.data_handler.get_all_video_names(filter_str=date_str)
            video_files = [video_files[0]]

            for video_name in video_files:

                # download video 
                video = video_name + ".avi"
                local_path = os.path.abspath("./"+video)
                print(video)
                self.data_handler.download_video(video, local_path)

                # analyse video
                results = self.model.analyse_video(local_path)
                
                self.add_video_to_xml_tree(video, results)

                # remove video from local storage
                os.remove(local_path)

            self.write_to_file(self.model.model_name, date_str)
            self.file_handler = XMLFileConverter(element_name="video_processing")


    def add_video_to_xml_tree(self, video_name, results):
        [time_stamps, num_shrimps, boundingBoxes, scores] = results

        self.file_handler.add_video_to_xml_tree(video_name=video_name,
                                                time_stamps=time_stamps,
                                                num_shrimps=num_shrimps,
                                                boundingBoxes=boundingBoxes,
                                                scores=scores)


    def write_to_file(self, model_name, date_str):

        log_output_dir = os.path.join(current_dir, "logs_" + model_name)
        if not os.path.exists(log_output_dir):
            os.mkdir(log_output_dir)

        log_output_name = "log_" + date_str + ".txt"
        log_output_path = os.path.join(log_output_dir, log_output_name)

        self.file_handler.write_to_file(targetFile=log_output_path)



class XMLFileConverter:

    def __init__(self, file_path="", element_name="video_process_log"):
        
        self.file_path = file_path
        if os.path.exists(self.file_path):
            tree = ElementTree.parse(self.file_path)
            self.xmltree = tree.getroot()
        else:
            self.xmltree = ElementTree.Element(element_name)

            # add timestamp
            used_datetime = datetime.datetime.now()
            ts_str = "_{0}-{1:02d}-{2:02d}_{3:02d}-{4:02d}".format(used_datetime.year, 
                                        used_datetime.month,
                                        used_datetime.day,
                                        used_datetime.hour,
                                        used_datetime.minute)
            process_time_stamp = ElementTree.Element("process_time_stamp")
            process_time_stamp.text = ts_str
            self.xmltree.append(process_time_stamp)

        

    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        return etree.tostring(root, pretty_print=True).replace("  ".encode(), "\t".encode())

    def write_to_file(self, root=None, targetFile=None):

        if root is None:
            root = self.xmltree
        if targetFile is None:
            if self.file_path == "":
                print("Add a path to write a file.")
                return False
            targetFile = self.file_path
        if os.path.exists(targetFile):
            os.remove(targetFile)

        out_file = None
        out_file = codecs.open(targetFile, 'w')

        prettifyResult = self.prettify(root)
        out_file.write(prettifyResult.decode('utf8'))
        out_file.close()
    
    def add_video_to_xml_tree(self, 
                        video_name=None,
                        time_stamps=[],
                        num_shrimps=[],
                        boundingBoxes=[],
                        scores=[]):

        if video_name is None:
            return False

        if num_shrimps == []:
            for boxes in boundingBoxes:
                num_shrimps.append(len(boxes))
        
        # checking dimensions
        if (len(time_stamps) != len(num_shrimps)) or (len(num_shrimps) != len(boundingBoxes)) or (len(boundingBoxes) != len(scores)):
            print("List dimensions must agree.")
            return False

        video_file_xml = ElementTree.Element("video_file")
        self.xmltree.append(video_file_xml)
        # video file name 
        video_name_xml = ElementTree.Element("video_name")
        video_name_xml.text = video_name
        video_file_xml.append(video_name_xml)
        # timestamp of processing the image
        video_ts_xml = ElementTree.Element("process_time_stamp")
        video_ts_xml.text = "20201019"
        video_file_xml.append(video_ts_xml)

        for index in range(len(time_stamps)):
            frame_xml = ElementTree.SubElement(video_file_xml, "frame")

            ts = ElementTree.SubElement(frame_xml, "time_stamp")
            ts.text = time_stamps[index]
            
            ns = ElementTree.SubElement(frame_xml, "num_shrimps")
            ns.text = str(num_shrimps[index])
            
            bb = ElementTree.SubElement(frame_xml, "bounding_boxes")
            bb.text = str(boundingBoxes[index])
            
            sc = ElementTree.SubElement(frame_xml, "scores")
            sc.text = str(scores[index])

va = VideoAnalyser("tf_API_data1_v01")
va.analyse_videos()
