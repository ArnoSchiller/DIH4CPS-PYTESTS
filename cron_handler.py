"""
CronHandler: This class creates crontab files and the crontabs can be added ti linux system. 

Requirements:
- os, sys (allready installed)

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.2
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                           Date:
v0.0.1      (AS) First initialize. Added functions to add and update        06.08.2020\n
                crontabs. It saves crontabs to a txt file and this crontab            \n
                file will be added to the sytem.                                      \n
v0.0.2      (AS) Updated CronHandler and tested on Linux. Works fine.       07.08.2020\n
    
Attributes:
-----------
cronList : list
    list of crontab strings to write to file. crontabs can be added and updated.
outputFile_name : str
    file name of the file the crontabs will be written to.
cron_choices : dict
    differnt choices for times the crontabs will be executed. 
"""

import os, sys

class CronHandler:

    cronList = []
    outputFile_name = "crontabs.txt"

    cron_choices = {
        "every_min"       : "* * * * *",
        "every_2min"      : "*/2 * * * *",
        "every_5min"      : "*/5 * * * *",
        "every_10min"     : "*/10 * * * *",
        "every_30min"     : "*/30 * * * *",
        "every_hour_00"   : "0 * * * *",
        "every_2hour_00"  : "0 */2 * * *",
        "every_6hour_00"  : "0 */6 * * *",
        "every_12hour_00" : "0 */12 * * *",
        "every_day_00_05" : "5 0 * * *"
    }

    def __init__(self):
        """ Set used paths, commands and output file paths.
        """

        self.parentDir_path = os.path.dirname(os.path.realpath(__file__))
        self.outputFile_path = os.path.join(self.parentDir_path, self.outputFile_name)
        
        self.python_path = sys.executable                                                 # find from system
        # self.python_path = os.path.join(self.parentDir_path, ".venv/Scripts/python.exe")  # for windows venv
        # self.python_path = os.path.join(self.parentDir_path, ".linux_venv/bin/python3")     # for linux venv

        self.webcamRecorder_path = os.path.join(self.parentDir_path, "webcam_recorder.py")
        self.cloudConnection_path = os.path.join(self.parentDir_path, "cloud_connection.py")
        self.systemMonitoring_path = os.path.join(self.parentDir_path, "system_monitoring.py")

        self.webcamRecorder_command = "{0} {1}".format(self.python_path, self.webcamRecorder_path)
        self.cloudConnection_command = "{0} {1}".format(self.python_path, self.cloudConnection_path)
        self.systemMonitoring_command = "{0} {1}".format(self.python_path, self.systemMonitoring_path)

        self.webcamRecorder_output = os.path.join(self.parentDir_path, "log_webcam_recorder.txt")
        self.cloudConnection_output = os.path.join(self.parentDir_path, "log_cloud_connection.txt")

    def addCron(self, cron_str, command_str, outputFile_path=None):
        """ Add new crontab to cronList

        Parameters
        ----------
        cron_str : str
            time the crontab should be executed (cron format: *(min) *(h) *(day) *(month) *(day of week)).
        command_str : str
            command should be executed on system.
        outputFile_path : str
            path to file the output should be written to. 
            If outputFile_path is none the output will be ignored.
        """
        cron = cron_str + " " + command_str
        if not outputFile_path == None:
            cron += " > " + outputFile_path 
        self.cronList.append(cron)

    def updateCron(self, index, cron_str, command_str, outputFile_path=None):
        """ Update existing crontab in CronList

        Parameters
        ----------
        index : int
            index where the crontab was stored in the CronList (from 0 to len(CronList)-1)
        cron_str : str
            time the crontab should be executed (cron format: *(min) *(h) *(day) *(month) *(day of week)).
        command_str : str
            command should be executed on system.
        outputFile_path : str
            path to file the output should be written to. 
            If outputFile_path is none the output will be ignored.
        """
        cron = ""
        if index > len(self.cronList)-1: 
            return False
        cron = cron_str + " " + command_str
        if not outputFile_path == None:
            cron += " " + outputFile_path 
        self.cronList[index] = cron
        return True

    def writeCronToFile(self):
        """ Write crontabs from CronList to txt file.
        """
        if os.path.exists(self.outputFile_path):
            os.remove(self.outputFile_path)
        with open(self.outputFile_path, mode='a') as f:
            for cron in self.cronList:
                f.write(cron + "\n")
        return True

def updateCrontabInSystem(cronFile_path):
    """ Reload the system crontabs from crontab file (only Linux).
    """
    if os.path.exists(cronFile_path):
        os.system("crontab {0}".format(cronFile_path))
        return True
    return False

if __name__ == '__main__':
    handler = CronHandler()
    videoLen = 10
    if videoLen > 0 and videoLen < 300:
        handler.webcamRecorder_command += " --videoLength {}".format(videoLen)
    # run WebCamRecorder every 10 minutes
    handler.addCron(handler.cron_choices["every_10min"], 
                    handler.webcamRecorder_command, 
                    handler.webcamRecorder_output)

    # run cloundConnection every day at 00:05 AM
    handler.addCron(handler.cron_choices["every_day_00_05"], 
                    handler.cloudConnection_command, 
                    handler.cloudConnection_output)

    # run system_monitoring every 2 minutes
    handler.addCron(handler.cron_choices["every_2min"], 
                    handler.systemMonitoring_command)
    
    handler.writeCronToFile()

    # works on linux only
    updateCrontabInSystem(handler.outputFile_path)
