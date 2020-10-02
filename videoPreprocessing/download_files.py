import boto3
import os

date_str = "2020-10-01"
download_dir = os.path.join(os.path.abspath("./video_files"), date_str)
if not os.path.exists(download_dir):
    os.mkdir(download_dir)

cloud_access_key         = "minio"
cloud_secret_key         = "miniostorage"
cloud_bucket_name        = "test-dih4cps"
cloud_url                = "https://minio.dih4cps.swms-cloud.com:9000/"
cloud_bucket_name        = "test-dih4cps"

s3_client = boto3.client('s3',
                aws_access_key_id = cloud_access_key,
                aws_secret_access_key = cloud_secret_key,
                endpoint_url=cloud_url, 
                verify=False,
                config=boto3.session.Config(signature_version='s3v4'))
                
s3_resource = boto3.resource('s3',
                aws_access_key_id = cloud_access_key,
                aws_secret_access_key = cloud_secret_key,
                endpoint_url=cloud_url, 
                verify=False,
                config=boto3.session.Config(signature_version='s3v4'))

s3_bucket = s3_resource.Bucket(cloud_bucket_name)

for bucket_object in s3_bucket.objects.all():
    object_name = str(bucket_object.key)
    if object_name.count(date_str) > 0:
        s3_client.download_file(cloud_bucket_name, bucket_object.key, os.path.join(download_dir, bucket_object.key))