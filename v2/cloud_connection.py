"""
CloudConnection: This class rules the cloud connection (S3 architecture) using 
    boto3.

Requirements:                    
pip install boto3, see https://pypi.org/project/boto3/ for more informations.
also see https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html.

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v1.0.0
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                   Date:
v0.0.*           Version 1. See v1 (cloud_connection).              05.08.2020\n
v1.0.0      (AS) First initialize of v2. Included code from v1.     07.09.2020\n
"""
import boto3
from botocore.exceptions import *
import os, glob
import datetime, time
from datetime import timedelta
import logging
import argparse 
from mqtt_connection import MQTTConnection
from configuration import * 

class CloudConnection:
    """ 
    This class rules the connection to the storage cloud so it is possible
    to uploade files to cloud. 
    
    Attributes:
    -----------
    access_key : str
        access key (username) of the cloud
    secret_key : str
        secret key (password) of the cloud
    bucket_name : str
        used bucket to save the data to
    cloud_url : str
        url to cloud server
    recordsDir_name : str
        directory the video data is placed in
    max_tries : int
        max number of tries to connect to cloud. 
    """
    access_key = global_cloud_access_key
    secret_key = global_cloud_secret_key
    bucket_name = global_cloud_bucket_name
    cloud_url = global_cloud_url

    recordsDir_name = global_recordsDir_name
    max_tries = 10

    
    module_name = "CloudConnection"
    user_name = global_user_name

    def __init__(self):
        """
        Setup the S3 connection and the used bucket. Also define the recordings directory.
        """

        # logging via MQTT
        self.mqtt = MQTTConnection()

        #logging via output / file
        logging.basicConfig(level=logging.INFO)
        logging.info("Initialize CloudConnection.")

        # setup the S3 client
        counter_tries = 0
        self.s3_client = None
        while self.s3_client == None:
            if counter_tries == 0:
                # logging.info("Connecting to S3 server...")
                self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["ConnectingToServer"])
            if counter_tries > self.max_tries:
                # logging.error("Can not connect to S3 server ({0} tries). Quitting...".format(counter_tries))
                self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["ConnectServerError"])
                exit()
            self.s3_client = boto3.client('s3', 
                aws_access_key_id = self.access_key,
                aws_secret_access_key = self.secret_key,
                endpoint_url=self.cloud_url, 
                config=boto3.session.Config(signature_version='s3v4'))
            counter_tries += 1
            time.sleep(5)
        self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["ConnectedToServer"])
        # logging.info("Connected to S3 server.")

        # get directory 
        parentDir_path = os.path.dirname(os.path.realpath(__file__))
        self.recordsDir_path = os.path.join(parentDir_path, self.recordsDir_name)

    def setBucketName(self, bucket_name):
        """
        Set new bucket name if bucket exists.
        """ 
        # Retrieve the list of existing buckets
        response = self.s3_client.list_buckets()

        for bucket in response['Buckets']:
            if bucket['Name'] == bucket_name:
                self.bucket_name = bucket_name

    def uploadFileToCloud(self, file_name, object_name=None):
        """Upload a file to an S3 bucket

        Parameters
        ----------
        file_name : str 
            file to upload
        object_name : str 
            S3 object name, if not specified then file_name is used

        Returns
        ----------
        true    if upload was successfull
        false   otherwise
        """
        if object_name == None:
            object_name = file_name
        self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["UploadingFile"], file=object_name)
        # logging.info("Uploading file {0} ...".format(object_name))
        file_path = os.path.join(self.recordsDir_path, file_name)
        try:
            self.s3_client.upload_file(file_path, self.bucket_name,object_name, Callback=ProgressPercentage(file_path))

            # Prove if the upload was successfully
            content = self.s3_client.head_object(Bucket=self.bucket_name,Key=object_name)
            if content.get('ResponseMetadata',None) is not None:
                logging.info("File exists - s3://%s/%s " %(self.bucket_name,object_name))
                self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["UploadedFile"], file=object_name)
                time.sleep(1)
                self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["UploadReady"], file=object_name)
                # if upload was successful, delete the file 
                if os.path.exists(file_path):
                    os.remove(file_path)

            else:
                logging.info("File does not exist - s3://%s/%s " %(self.bucket_name,object_name))
                self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["UploadError"], file=object_name)

            return True
        except FileNotFoundError:
            self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["FileNotFound"], file=object_name)
            #logging.error("The file to upload was not found.")
            return False
        except NoCredentialsError:
            self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["NoCredentials"], file=object_name)
            #logging.error("Credentials are not available.")
            return False
        except ClientError:
            self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["ClientError"], file=object_name)
            #logging.error("Client Error")
            return False
        except Exception:
            self.mqtt.sendProcessMessage(self.user_name, self.mqtt.status_list[self.module_name]["UploadError"], file=object_name)
            #logging.error("Client Error")
            return False


    def uploadFilesFromDay(self, recording_name, day_datetime):
        """ Upload every avi file that was created on that day.

        Parameters
        ----------
        day_datetime : datetime 
            day as datetime object to save the files from
        recording_name : str
            representative name for clear attribution of the recording (see WebcamRecorder)
        """
        logging.info("Upload files from {0} ...".format(day_datetime))
        # create the filter string
        filter_str = "{0}_{1}-{2:02d}-{3:02d}_*-*-*.avi".format(recording_name, 
                                    day_datetime.year,
                                    day_datetime.month,
                                    day_datetime.day)
        filter_path = os.path.join(self.recordsDir_path, filter_str)
        file_paths = glob.glob(filter_path)

        for path in file_paths:
            file_name = os.path.basename(path)
            self.uploadFileToCloud(file_name)

        self.mqtt.sendProcessMessage(self.user_name, self.mqtt.info_list[self.module_name]["DisconnectedServer"])
        logging.info("Upload files from {0} done.".format(day_datetime))

    def uploadEveryAviFile(self, recording_name):
        """ Upload every avi file in the Recordings directory.

        Parameters
        ----------
        recording_name : str
            representative name for clear attribution of the recording (see WebcamRecorder)
        """
        logging.info("Upload every avi file ...")
        # create the filter string
        filter_str = "*.avi"
        filter_path = os.path.join(self.recordsDir_path, filter_str)
        file_paths = glob.glob(filter_path)

        for path in file_paths:
            file_name = os.path.basename(path)
            self.uploadFileToCloud(file_name)

        self.mqtt.sendProcessMessage(self.user_name, self.mqtt.info_list[self.module_name]["DisconnectedServer"])
        logging.info("Upload avi files done.")

import sys
import threading
class ProgressPercentage(object):
    """ This class is used to show the progress percentage while uploading files.
    Source: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()
        print("\n")

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    os.path.basename(self._filename), self._seen_so_far, 
                    self._size, percentage))
            sys.stdout.flush()
    
         
def uploadFilesFromToday():
    s3Con = CloudConnection()
    today = datetime.datetime.now() 
    s3Con.uploadFilesFromDay("test1", today)

def uploadFilesFromYesterday():
    s3Con = CloudConnection()
    yesterday = datetime.datetime.now() - timedelta(days = 1)
    s3Con.uploadFilesFromDay("test1", yesterday)

if __name__ == "__main__":

    # setup argument parser 
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--today", help="upload files recorded today, default is yesterday.",
			action="store_true")
    args = parser.parse_args()
    if args.today:
        uploadFilesFromToday()
    else:
        uploadFilesFromYesterday()

