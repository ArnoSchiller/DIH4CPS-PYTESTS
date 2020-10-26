import os
import glob
import boto3 

ACCESS_KEY      = "minio"
SECRET_KEY      = "miniostorage"
CLOUD_URL       = "https://minio.dih4cps.swms-cloud.com:9000/"

class DatasetHandler:

    download_dir = os.path.join(os.path.dirname(__file__), "downloads")

    cloud_access_key         = ACCESS_KEY
    cloud_secret_key         = SECRET_KEY
    cloud_url                = CLOUD_URL

    bucket_names = ["dataset-v1-dih4cps", "dataset-v2-dih4cps"]
    video_bucket_name = "test-dih4cps"

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
    
    def define_dataset_version(self, bucket_name, version_id):
        if not self.bucket_names.count(bucket_name) > 0:
            return
        version_file_name = "version_{}.txt".format(version_id)
        bucket = self.s3_resource.Bucket(bucket_name)
        
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count(version_file_name) > 0:
                print("Version ", version_id, " allready exists.")
                return
        
        all_images = self.get_all_image_names(bucket_name)

        with open(version_file_name, "w") as out_file:
            for image_name in all_images:
                out_file.write(image_name + "\n")

        self.s3_client.upload_file(version_file_name, bucket_name, version_file_name)

        os.remove(version_file_name)
    
    def get_complete_dataset_list(self, bucket_name):

        if not self.bucket_names.count(bucket_name) > 0:
            return False

        dataset_files = []
        xml_file_names = []

        bucket = self.s3_resource.Bucket(bucket_name)
        
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count("xml") > 0:
                filepath = object_name.split(".")[0]
                filename = filepath.split("/")[1]
                xml_file_names.append(filename)
                
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count("png") > 0:
                filepath = object_name.split(".")[0]
                filename = filepath.split("/")[1]
                if xml_file_names.count(filename) > 0:
                    dataset_files.append(filename)
        return dataset_files

    def download_video(self, object_name, download_path, bucket_name=None):

        if bucket_name is None:
            bucket_name = self.video_bucket_name

        self.s3_client.download_file(bucket_name, object_name, download_path)

    def download_not_labeled_images(self, bucket_name=None):
        
        if bucket_name is None:
            bucket_name = self.bucket_names[1]    

        if not os.path.exists(self.download_dir):
            os.mkdir(self.download_dir)

        image_files = self.get_all_image_names(bucket_name)
        label_files = self.get_all_label_names(bucket_name)

        for image_name in image_files:
            if label_files.count(image_name):
                continue
            image_file_path = "images/" + image_name + ".png"
            local_file_path = os.path.join(self.download_dir, image_name + ".png")
            self.s3_client.download_file(bucket_name, image_file_path, local_file_path)

    def load_dataset_version(self, bucket_name, version_name=None):
        
        images = []

        if version_name is None:
            version = self.get_latest_dataset_version(bucket_name)
        else:
            version = version_name + ".txt"
        
        self.s3_client.download_file(bucket_name, version, version)

        with open(version, "r") as in_file:
            for image_name in in_file:
                if image_name.count("\n"):
                    image_name = image_name.split("\n")[0]
                images.append(image_name)

        return images 

    def get_latest_dataset_version(self, bucket_name):
        return "version_2020-10-15.txt"

    def get_all_video_names(self, filter_str=""):
        video_file_names = []
        bucket = self.s3_resource.Bucket(self.video_bucket_name)
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count(".avi")>0 and object_name.count(filter_str)>0:
                if object_name.count("/") > 0:
                    object_name = object_name.split("/")[-1]
                filename = object_name.split(".")[0]
                
                video_file_names.append(filename)
        return video_file_names

    def get_all_image_names(self, bucket_name):

        if not self.bucket_names.count(bucket_name) > 0:
            return False

        png_file_names = []

        bucket = self.s3_resource.Bucket(bucket_name)
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count("png") > 0:
                filepath = object_name.split(".")[0]
                filename = filepath.split("/")[1]
                png_file_names.append(filename)
        return png_file_names

    def get_all_label_names(self, bucket_name):

        if not self.bucket_names.count(bucket_name) > 0:
            return False

        xml_file_names = []

        bucket = self.s3_resource.Bucket(bucket_name)
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count("xml") > 0:
                filepath = object_name.split(".")[0]
                filename = filepath.split("/")[1]
                xml_file_names.append(filename)
        return xml_file_names

if __name__ == "__main__":
    dsh = DatasetHandler()

    ## define dataset version, write every used image into txt
    #dsh.define_dataset_version(dsh.bucket_names[1], "2020-10-15")
    
    ## load latest dataset as list 
    #image_list = dsh.load_dataset_version(dsh.bucket_names[1])
    #print(image_list)