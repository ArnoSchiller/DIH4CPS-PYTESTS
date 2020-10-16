import os, sys 
    
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, ".."))

from datasetHandling.dataset_handler import DatasetHandler

class VideoAnalyser:

    models_list = [ "tf_API_data1_v01",
                    "tf_API_data2_v01"]

    
    def __init__(self, model_name):

        data_handler = DatasetHandler()
        
        if not self.models_list.count(model_name) > 0:
            print("choose a valid model or adapt models_list.")
            quit()

        log_output_name = "log_" + model_name + ".txt"
        self.log_output_path = os.path.join(self.current_dir, log_output_name)

        test_list = self.read_file_to_list(self.log_output_path)
        test_list.append("next")
        self.write_list_to_file(test_list)

    def write_list_to_file(self, output_list, output_file_path=None):
        if output_file_path is None:
            output_file_path = self.log_output_path
        
        with open(output_file_path, 'w') as out_file:
            for element in output_list:
                out_file.write('%s\n' %element)

    def read_file_to_list(self, input_file_path):
        if not os.path.exists(input_file_path):
            return False
        
        input_list = [] 
        with open(input_file_path, 'r') as in_file:
            for line in in_file:
                element = str(line[:-1])
                input_list.append(element)
        return input_list

data_handler = DatasetHandler()
names = data_handler.get_all_video_names(filter_str="directRecord")
print(len(names))
# va = VideoAnalyser("tf_API_data1_v01")