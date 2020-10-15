import boto3 
from tabulate import tabulate       # pip install tabulate
import pandas as pd                 # pip install pandas


class DatasetStatistics:
    cloud_access_key         = "minio"
    cloud_secret_key         = "miniostorage"
    cloud_url                = "https://minio.dih4cps.swms-cloud.com:9000/"
    
    bucket_names = ["dataset-v1-dih4cps", "dataset-v2-dih4cps"]

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

    def summery(self):

        matrix = []
        for bucket_name in self.bucket_names:
            bucket = self.s3_resource.Bucket(bucket_name)
            num_complete = len(self.get_complete_dataset_list(bucket))
            num_labels = len(self.get_all_label_names(bucket))
            num_images = len(self.get_all_image_names(bucket))
            matrix.append((bucket_name, num_complete, num_labels, num_images))
        df = pd.DataFrame(matrix, columns=["Name", "gelabelte Bilder", "Anzahl Label", "Anzahl Bilder"])
        
        return tabulate(df, headers='keys', tablefmt='psql')

    def get_all_image_names(self, bucket):
        png_file_names = []
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count("png") > 0:
                filepath = object_name.split(".")[0]
                filename = filepath.split("/")[1]
                png_file_names.append(filename)
        return png_file_names

    def get_all_label_names(self, bucket):
        xml_file_names = []
        for bucket_object in bucket.objects.all():
            object_name = str(bucket_object.key)
            if object_name.count("xml") > 0:
                filepath = object_name.split(".")[0]
                filename = filepath.split("/")[1]
                xml_file_names.append(filename)
        return xml_file_names

    def get_complete_dataset_list(self, bucket):
        dataset_files = []
        xml_file_names = []
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


if __name__ == "__main__":
    stats = DatasetStatistics()
    print(stats.summery())