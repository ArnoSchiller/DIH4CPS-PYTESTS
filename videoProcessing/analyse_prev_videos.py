import os, sys 

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs
    
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(current_dir, "..", "models"))

from datasetHandling.dataset_handler import DatasetHandler


class VideoAnalyser:

    models_list = [ "tf_API_data1_v01",
                    "tf_API_data2_v01"]

    
    def __init__(self, model_name):

        data_handler = DatasetHandler()

        file_handler = XMLFileConverter("") 
        
        if not self.models_list.count(model_name) > 0:
            print("choose a valid model or adapt models_list.")
            quit()

        log_output_name = "log_" + model_name + ".txt"
        self.log_output_path = os.path.join(current_dir, log_output_name)

        test_list = self.read_file_to_list(self.log_output_path)
        test_list.append("next")
        self.write_list_to_file(test_list)




class XMLFileConverter:

    def __init__(self, file_path):
        
        self.file_path = file_path
        if os.path.exists(self.file_path):
            tree = ElementTree.parse(self.file_path)
            self.xmltree = tree.getroot()
        else:
            self.xmltree = ElementTree.Element("video_process_log")
        

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

#data_handler = DatasetHandler()
#names = data_handler.get_all_video_names(filter_str="directRecord")
#print(len(names))

# va = VideoAnalyser("tf_API_data1_v01")

fc = XMLFileConverter("log_test.txt")
fc.add_video_to_xml_tree(video_name="a",
                            time_stamps=["LOOOOL", "2019"],
                            num_shrimps=[1, 2],
                            boundingBoxes=[[1,2], [3,4]],
                            scores=[0.9, 0.4])
fc.write_to_file()