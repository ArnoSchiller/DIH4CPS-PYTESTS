import os, sys 
import datetime

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs
    
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(current_dir, "..", "models"))
sys.path.append(os.path.join(current_dir, "..", "v2"))

from datasetHandling.dataset_handler import DatasetHandler
from models.trained_model import Model
from v2.mqtt_connection import MQTTConnection


class VideoAnalyser:
    """
    VideoAnalyser: This class uses a model to detect shrimps on frames. For each frame the number of shrimps will be send to the IoT Stack. Also for each process routine there will be a log file group by the recording date of the video files.  

    @authors:   Arno Schiller (AS)
    @email:     schiller@swms.de
    @version:   v0.0.4
    @license:   ...

    VERSION HISTORY
    Version:    (Author) Description:                               Date:
    v0.0.1      (AS) First initialize. Added XML file generator.    19.10.2020\n
    v0.0.2      (AS) Included model prediction results to the       20.10.2020\n
                    log file output.                                          \n
    v0.0.3      (AS) Connected the model results to the IoT Stack.  21.10.2020\n
    v0.0.4      (AS) Included function to save frames if a shrimp   26.10.2020\n
                    was detected.
    """

    models_list = [ "tf_API_data1_v01",
                    "tf_API_data2_v01"]

    date_list = [   "2020-10-07"]

    model_min_score_thresh = 0.6

    with_mqtt = True
    with_visualisation = False
    save_detected_frames = True


    def __init__(self,  model_name):
        """
        If the selected model exists, create an instance of this model. Also create the XML file handler and the dataset handler.
        """

        if not self.models_list.count(model_name) > 0:
            print("choose a valid model or adapt models_list.")
            quit()

        self.model = Model(model_name=model_name, save_detected_frames=self.save_detected_frames, with_visualisation=self.with_visualisation)
        self.model.min_score_thresh = self.model_min_score_thresh

        self.data_handler = DatasetHandler()

    def analyse_videos(self):
        """
        Analyse every video file group by the recording date. For each frame send the results to the IoT Stack and create a log file for every processed day. 
        """
        for date_str in self.date_list:

            self.log_generator = LogGenerator(element_name="video_processing",
                                    with_mqtt=self.with_mqtt,
                                    model_min_score=self.model_min_score_thresh,
                                    model_name=self.model.model_name,
            )
            
            if os.path.exists(os.path.join(os.path.abspath("."), 
                                        "logs_" + self.model.model_name,
                                        "log_" + date_str + ".txt")):
                print("files with this date allready processed")

            video_files = self.data_handler.get_all_video_names(filter_str=date_str)

            for video_name in video_files:
                
                print("\n\nprocessing video {} ...".format(video_name))
                # download video 
                video = video_name + ".avi"
                local_path = os.path.abspath("./"+video)
                self.data_handler.download_video(video, local_path)

                # analyse video
                results = self.model.analyse_video(local_path)
                
                self.add_video_to_xml_tree(video, results)

                # remove video from local storage
                os.remove(local_path)
                print("... done")

            self.write_to_file(self.model.model_name, date_str)


    def add_video_to_xml_tree(self, video_name, results):
        [time_stamps, num_shrimps, boundingBoxes, scores] = results

        self.log_generator.add_video_to_xml_tree(video_name=video_name,
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

        self.log_generator.write_to_file(targetFile=log_output_path)


class LogGenerator:
    """
    LogGenerator: This class creates a log file for every process routine. Also it sends the number of detected shrimps of every frame to the IoT Stack via MQTT.
    
    Make sure it is possible to import the MQTTConnection 

    ToDo:   add/test the read function (txt to XML tree)  

    @authors:   Arno Schiller (AS)
    @email:     schiller@swms.de
    @version:   v0.0.3
    @license:   ...

    VERSION HISTORY
    Version:    (Author) Description:                               Date:
    v0.0.1      (AS) First initialize. Added XML file generator.    19.10.2020\n
    v0.0.2      (AS) Included model prediction results to the       20.10.2020\n
                    log file output.                                          \n
    v0.0.3      (AS) Connected the model results to the IoT Stack.  21.10.2020\n
    """

    user = "damm"
    process_version = "v01"

    def __init__(self,  model_name, 
                        model_min_score=None,
                        process_timestamp=None,
                        with_mqtt=True,
                        file_path="", 
                        element_name="video_process_log"):

        self.model_name = model_name

        if model_min_score is None:
            model_min_score = "N/A"
        self.model_min_score = str(model_min_score)

        if process_timestamp is None:
            process_timestamp = "N/A"
        self.process_timestamp = process_timestamp

        self.with_mqtt = with_mqtt
        if self.with_mqtt:
            self.mqtt_connection = MQTTConnection()

        self.file_path = file_path
        if os.path.exists(self.file_path):
            tree = ElementTree.parse(self.file_path)
            self.xmltree = tree.getroot()
        else:
            self.xmltree = ElementTree.Element(element_name)

            # add timestamp
            used_datetime = datetime.datetime.now()
            ts_str = "{0}-{1:02d}-{2:02d}_{3:02d}-{4:02d}".format(used_datetime.year, 
                                        used_datetime.month,
                                        used_datetime.day,
                                        used_datetime.hour,
                                        used_datetime.minute)
            process_time_stamp_xml = ElementTree.Element("process_time_stamp")
            process_time_stamp_xml.text = ts_str
            self.xmltree.append(process_time_stamp_xml)

            min_score_xml = ElementTree.Element("model_min_score_thresh")
            min_score_xml.text = self.model_min_score
            self.xmltree.append(min_score_xml)


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

            if self.with_mqtt:
                self.send_result_via_mqtt(file_name=video_name, 
                                        frame_timestamp=time_stamps[index], num_shrimps=num_shrimps[index])
    
    def send_result_via_mqtt(self, file_name, frame_timestamp, num_shrimps):
        if self.with_mqtt:
            self.mqtt_connection.sendDetectionMessage(user=self.user,
                    process_version=self.process_version,
                    model_name=self.model_name,
                    score_min_thresh=self.model_min_score,
                    process_timestamp=self.process_timestamp,
                    file_name=file_name,
                    num_shrimps=num_shrimps,
                    frame_timestamp=frame_timestamp)

va = VideoAnalyser("tf_API_data1_v01")
va.analyse_videos()