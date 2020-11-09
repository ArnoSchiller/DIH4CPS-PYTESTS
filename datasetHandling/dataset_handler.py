import os
import sys
import glob
import boto3 

ACCESS_KEY      = "minio"
SECRET_KEY      = "miniostorage"
CLOUD_URL       = "https://minio.dih4cps.swms-cloud.com:9000/"


class DatasetHandler:

    data_transformation_path = os.path.join(os.path.dirname(__file__), "data_transformation")
    sys.path.append(data_transformation_path)

    download_dir = os.path.join(os.path.dirname(__file__), "downloads")

    cloud_access_key         = ACCESS_KEY
    cloud_secret_key         = SECRET_KEY
    cloud_url                = CLOUD_URL

    bucket_names = ["dataset-v1-dih4cps", "dataset-v2-dih4cps"]
    video_bucket_name = "test-dih4cps"

    created_files = ["images.csv", "test.csv", "train.csv",
                     "images.record", "test.record", "train.record"]

    def __init__(self):
        self.s3_client = boto3.client('s3',
                        aws_access_key_id = self.cloud_access_key,
                        aws_secret_access_key = self.cloud_secret_key,
                        endpoint_url=self.cloud_url, 
                        verify=True,
                        config=boto3.session.Config(signature_version='s3v4'))

        self.s3_resource = boto3.resource('s3',
                        aws_access_key_id = self.cloud_access_key,
                        aws_secret_access_key = self.cloud_secret_key,
                        endpoint_url=self.cloud_url, 
                        verify=True,
                        config=boto3.session.Config(signature_version='s3v4'))

    def upload_missing_images(self, bucket_name, image_dir_path):

        png_files = glob.glob(os.path.join(image_dir_path, "*.png"))
        xml_files = glob.glob(os.path.join(self.download_dir, "*.xml"))

        for index, file_path in enumerate(png_files):
            print("File {} of {}.".format(index+1, len(png_files)))
            name = os.path.basename(file_path)
            name = name.split(".")[0]

            #image_path = os.path.join(image_dir_path, name + ".png")
            image_path = file_path

            if os.path.exists(image_path):
                """
                os.system("copy {} {}".format(image_path, os.path.join(self.download_dir, name + ".png")))
                os.remove(file_path)
                """
                self.s3_client.upload_file(image_path, bucket_name, "images/{}.png".format(name))


    def create_dataset_version(self, bucket_name, version_id, full_path=True):

        version_name = "version_{}".format(version_id)
        ## define dataset version, write every used image into txt
        self.define_dataset_version(bucket_name=bucket_name, version_name=version_name)

        ## load latest dataset as list 
        data_list = dsh.load_dataset_version(bucket_name=bucket_name, version_name=version_name)

        ## create download directory
        temp_dir = "TEMP_DOWNLOADS"
        labels_dir = temp_dir
        images_dir = temp_dir

        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

        if full_path:
            """
            for data_path in data_list:
                data_name = data_path.split("/")[-1]
                
                xml_path = data_path + ".xml"
                download_path = os.path.join(labels_dir, "{}.xml".format(data_name))
                self.s3_client.download_file(bucket_name, xml_path, download_path)

                png_path = data_path + ".png"
                download_path = os.path.join(images_dir, "{}.png".format(data_name))
                self.s3_client.download_file(bucket_name, png_path, download_path)
            #"""

        else:
            ## old version not needed anymore
            ## download every xml file and every png file
            for data_name in data_list:
                object_name = "labels/{}.xml".format(data_name)
                download_path = os.path.join(labels_dir, "{}.xml".format(data_name))
                self.s3_client.download_file(bucket_name, object_name, download_path)

                object_name = "images/{}.png".format(data_name)
                download_path = os.path.join(images_dir, "{}.png".format(data_name))
                self.s3_client.download_file(bucket_name, object_name, download_path)
        

        ## convert xml files to csv files
        command = "python xml_to_csv.py"
        args = ""
        args += " --splitted"
        args += " --xml_files_dir {}".format(labels_dir)
        print(command + args)
        os.system(command + args)

        ## convert csv files to tfrecord files  
        for tag in ["images", "test", "train"]:
            if os.path.exists(tag + ".csv"):  
                command = "python generate_tfrecord.py"
                args = ""
                args += " --csv_input={}.csv".format(tag)
                args += " --image_dir={}".format(images_dir)
                args += " --output_path={}.record".format(tag)
                print(command + args)
                os.system(command + args)

        ## upload created files
        for file_name in self.created_files:
            local_path = os.path.join(os.path.dirname(__file__), file_name)
            if os.path.exists(local_path):
                cloud_path = version_name + "/" + file_name
                self.s3_client.upload_file(local_path, bucket_name, cloud_path)

        ## remove created files
        self.created_files.append("images.txt")
        for file_name in self.created_files:
            local_path = os.path.join(os.path.dirname(__file__), file_name)
            if os.path.exists(local_path):
                os.remove(local_path)

        ## remove downloaded files 
        """
        if os.path.exists(temp_dir):
            files = glob.glob(os.path.join(temp_dir, "*"))
            for file_path in files:
                os.remove(file_path)
            os.rmdir(temp_dir)
        #"""


    def define_dataset_version(self, bucket_name, version_name, full_path=True):
        ## define dataset version, write every used image into txt

        if not self.bucket_names.count(bucket_name) > 0:
            return
        images_file_name = "images.txt"
        bucket = self.s3_resource.Bucket(bucket_name)
        
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count(version_name) > 0:
                print("Version ", version_name, " allready exists.")
                return
        
        all_images = self.get_all_image_names(bucket_name, full_path=True)
        print("Selected {} images to define version".format(len(all_images)))

        with open(images_file_name, "w") as out_file:
            for image_name in all_images:
                out_file.write(image_name + "\n")

        object_name = version_name + "/" + images_file_name
        self.s3_client.upload_file(images_file_name, bucket_name, object_name)

        os.remove(images_file_name)
    
    def get_complete_dataset_list(self, bucket_name, full_path=False):

        if not self.bucket_names.count(bucket_name) > 0:
            return False

        dataset_files = []
        xml_file_names = []

        bucket = self.s3_resource.Bucket(bucket_name)
        
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count("xml") > 0:
                filepath = object_name.split(".")[0]
                filename = filepath.split("/")[-1]
                xml_file_names.append(filename)
                
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count("png") > 0:
                filepath = object_name.split(".")[0]
                filename = filepath.split("/")[-1]
                if xml_file_names.count(filename) > 0:
                    if full_path:
                        dataset_files.append(filepath)
                    else:
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

    def download_missing_image_label(self, bucket_name=None):
        
        if bucket_name is None:
            bucket_name = self.bucket_names[1]    

        if not os.path.exists(self.download_dir):
            os.mkdir(self.download_dir)

        image_files = self.get_all_image_names(bucket_name)
        label_files = self.get_all_label_names(bucket_name)

        for label_name in label_files:
            if image_files.count(label_name):
                continue
            label_file_path = "labels/" + label_name + ".xml"
            local_file_path = os.path.join(self.download_dir, label_name + ".xml")
            self.s3_client.download_file(bucket_name, label_file_path, local_file_path)

    def load_dataset_version(self, bucket_name, version_name=None):
        
        images = []
        image_file_name = "images.txt"
        if version_name is None:
            version_name = self.get_latest_dataset_version(bucket_name)

        images_file = version_name + "/" + image_file_name
        self.s3_client.download_file(bucket_name, images_file, image_file_name)

        with open(image_file_name, "r") as in_file:
            for image_name in in_file:
                if image_name.count("\n"):
                    image_name = image_name.split("\n")[0]
                images.append(image_name)

        return images 

    def get_latest_dataset_version(self, bucket_name):
        return "version_2020-10-27"

    def get_all_video_names(self, filter_str="", full_path=False):
        video_file_names = []
        bucket = self.s3_resource.Bucket(self.video_bucket_name)
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count(".avi")>0 and object_name.count(filter_str)>0:
                if object_name.count("/") > 0:
                    object_name = object_name.split("/")[-1]
                filename = object_name.split(".")[0]

                if full_path:
                    video_file_names.append(object_name.split(".")[0])
                else:
                    video_file_names.append(filename)
        return video_file_names

    def get_all_image_names(self, bucket_name, full_path=False):

        if not self.bucket_names.count(bucket_name) > 0:
            return False

        png_file_names = []

        bucket = self.s3_resource.Bucket(bucket_name)
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count("png") > 0:
                filepath = object_name.split(".")[0]
                filename = filepath.split("/")[1]
                
                if full_path:
                    png_file_names.append(object_name.split(".")[0])
                else:
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

    #dsh.download_not_labeled_images()
    #dsh.download_missing_image_label()
    #dsh.upload_missing_images(bucket_name=dsh.bucket_names[0], image_dir_path = dsh.download_dir)# image_dir_path= os.path.abspath("C:/Users/Schiller/Downloads/images_detected"))
    dsh.create_dataset_version(dsh.bucket_names[0], "2020-11-09")
