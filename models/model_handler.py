import os
import glob
import boto3 

ACCESS_KEY      = "minio"
SECRET_KEY      = "miniostorage"
CLOUD_URL       = "https://minio.dih4cps.swms-cloud.com:9000/"

class ModelHandler:

    download_dir = os.path.join(os.path.dirname(__file__), "downloads")

    cloud_access_key        = ACCESS_KEY
    cloud_secret_key        = SECRET_KEY
    cloud_url               = CLOUD_URL

    trained_model_bucket    = str("trained-models-dih4cps")
    created_model_bucket    = "created-models-dih4cps"
    model_names             = ["tf_API_data1_v01", "tf_API_data2_v01"]

    def __init__(self):
        self.s3_client = boto3.client('s3',
                        aws_access_key_id = self.cloud_access_key,
                        aws_secret_access_key = self.cloud_secret_key,
                        endpoint_url=self.cloud_url, 
                        verify=False,
                        config=boto3.session.Config(signature_version='s3v4'))

        self.s3_resource = boto3.resource('s3',
                        aws_access_key_id = self.cloud_access_key,
                        aws_secret_access_key = self.cloud_secret_key,
                        endpoint_url=self.cloud_url, 
                        verify=False,
                        config=boto3.session.Config(signature_version='s3v4'))

    def download_trained_model(self, model_name, base_path):

        if not self.model_names.count(model_name) > 0:
            print("model name is not available.")
            return
        
        if not os.path.exists(base_path):
            print("base path is not available.")
            return
        
        self.download_utils(base_path)

        model_path = os.path.join(base_path, model_name)
        if os.path.exists(model_path):
            print("model is allready downloaded.")
            return
        os.mkdir(model_path)
        
        lm_res = self.download_label_map(model_name, model_path)
        mg_res = self.download_model_graph(model_name, model_path)


    
    def download_utils(self, base_path):

        utils_path = os.path.join(base_path, "utils")

        if os.path.exists(utils_path):
            print("utils allready downloaded.")
            return True
        
        os.mkdir(utils_path)
        download_files = []

        bucket = self.s3_resource.Bucket(self.trained_model_bucket)        
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            # download utils files
            if object_name.count("utils") > 0:
                
                file_name = object_name.split("/")[-1]
                file_path = os.path.join(utils_path, file_name)
                download_files.append(file_path)
                
                self.s3_client.download_file(self.trained_model_bucket, object_name, file_path)
        
        download_complete = self.verify_download(download_files)
        
        if not download_complete:
            for downloaded_file in glob.glob(os.path.join(utils_path,"*")):
                os.remove(downloaded_file)
            os.rmdir(utils_path)
            return False
        return True

    def download_label_map(self, model_name, base_path):

        label_map_path = os.path.join(base_path, "data")
        
        if not os.path.exists(label_map_path):
            os.mkdir(label_map_path)

        label_map_name = "object-detection.pbtxt"
        file_path = os.path.join(label_map_path,label_map_name)

        download_files = []
        bucket = self.s3_resource.Bucket(self.trained_model_bucket) 
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            # download utils files
            if object_name.count(model_name) > 0 and object_name.count(label_map_name) > 0:
                
                download_files.append(file_path)
                        
                self.s3_client.download_file(self.trained_model_bucket, object_name, file_path)

        download_complete = self.verify_download(download_files)
        
        if not download_complete:
            for downloaded_file in glob.glob(os.path.join(label_map_path,"*")):
                os.remove(downloaded_file)
            os.rmdir(label_map_path)
            return False
        return True
         
    def download_model_graph(self, model_name, base_path, model_graph_name=None):
        
        possible_graphs = self.get_model_graph_names(model_name)

        if model_graph_name is None:
            model_graph_name = self.get_latest_graph(model_name)

        if not possible_graphs.count(model_graph_name) > 0:
            print("Graph is not available")
            return False

        model_graph_path = os.path.join(base_path, "created_model_graph")
        if not os.path.exists(model_graph_path):
            os.mkdir(model_graph_path)

        saved_model_path = os.path.join(model_graph_path, "saved_model")
        if not os.path.exists(saved_model_path):
            os.mkdir(saved_model_path)

        download_files = []
        bucket = self.s3_resource.Bucket(self.trained_model_bucket) 
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            # download utils files
            if object_name.count(model_graph_name) > 0:
                file_name = object_name.split("/")[-1]
                if object_name.count("saved_model") > 0:
                    file_path = os.path.join(saved_model_path, file_name)
                else:
                    file_path = os.path.join(model_graph_path, file_name)
                download_files.append(file_path)
                        
                self.s3_client.download_file(self.trained_model_bucket, object_name, file_path)

        # verify download
        download_complete = self.verify_download(download_files)
        
        if not download_complete:
            for downloaded_file in glob.glob(os.path.join(saved_model_path,"*")):
                os.remove(downloaded_file)
            os.rmdir(saved_model_path)
            for downloaded_file in glob.glob(os.path.join(model_graph_path,"*")):
                os.remove(downloaded_file)
            os.rmdir(model_graph_path)
            return False
        return True

    def get_latest_graph(self, model_name):
        graphs = self.get_model_graph_names(model_name)

        latest_version = 0
        latest_graph_name = ""

        for graph in graphs:
            version = int(graph.split("_")[-1])
            if version > latest_version:
                latest_version = version
                latest_graph_name = graph
        
        return latest_graph_name

    def get_model_graph_names(self, model_name):

        graphs = []
        graph_prefix = model_name + "_graph_"
        bucket = self.s3_resource.Bucket(self.trained_model_bucket) 

        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            # download utils files
            if object_name.count(graph_prefix) > 0:
                graph_name = object_name.split("/")[0]
                if not graphs.count(graph_name) > 0:
                    graphs.append(graph_name)
        return graphs

    def verify_download(self, download_paths):
        for path in download_paths:
            if not os.path.exists(path):
                print("Downloading file {} failed. Restore download.".format(path))
                return False
        return True


mh = ModelHandler()
#mh.get_latest_graph("tf_API_data1_v01")
# mh.get_model_graph_names("tf_API_data1_v01")
mh.download_trained_model(mh.model_names[1], os.path.dirname(__file__))