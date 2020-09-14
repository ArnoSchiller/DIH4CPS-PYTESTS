"""
CronHandler: This class creates crontab files and the crontabs can be added to 
linux system. 

Requirements:
- os, sys (allready installed)

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v1.0.0
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                   Date:
v0.0.1           See v1 (cronHandler) for more informations.        06.08.2020\n
v1.0.0      (AS) Updated to v2. removed recorder from crontabs.     07.09.2020\n
v1.0.0      (AS) Removed WebcamRecorder. Using JobClient now.       14.09.2020\n
v1.0.1      (AS) Set CloudConnection to every 6 hours because       14.09.2020\n
                using direct upload yet. If there were any problems           \n
                uploading one file, this call should upload file.             \n
    
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

        self.jobClient_path = os.path.join(self.parentDir_path, "job_client_record.py")
        self.jobClient_path_command = "{0} {1}".format(self.python_path, self.jobClient_path)
        self.jobClient_path_output = os.path.join(self.parentDir_path, "log_job_client.txt")

        self.cloudConnection_path = os.path.join(self.parentDir_path, "cloud_connection.py")
        self.cloudConnection_command = "{0} {1}".format(self.python_path, self.cloudConnection_path)
        self.cloudConnection_output = os.path.join(self.parentDir_path, "log_cloud_connection.txt")

        self.systemMonitoring_path = os.path.join(self.parentDir_path, "system_monitoring.py")
        self.systemMonitoring_command = "{0} {1}".format(self.python_path, self.systemMonitoring_path)


    def addCron(self, cron_str, command_str, outputFile_path=None):
        """ Add new crontab to cronList

        Parameters
        ----------
        cron_str : str
            time the crontab should be executed 
            (cron format: *(min) *(h) *(day) *(month) *(day of week)).
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
            index where the crontab was stored in the CronList 
            (from 0 to len(CronList)-1)
        cron_str : str
            time the crontab should be executed 
            (cron format: *(min) *(h) *(day) *(month) *(day of week)).
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
    ### file recording 
    # send video record job to main process


    ### cloud connection 
    # run cloundConnection every day at 00:05 AM
    command = handler.cloudConnection_command + " --today"
    handler.addCron(handler.cron_choices["every_day_00_05"], 
                    command, 
                    handler.cloudConnection_output)

    """
    # run cloundConnection every 30 minutes
    handler.cloudConnection_command += " --today"
    handler.addCron(handler.cron_choices["every_30min"], 
                    handler.cloudConnection_command, 
                    handler.cloudConnection_output)
                    
    # run cloundConnection every 2 hours
    handler.cloudConnection_command += " --today"
    handler.addCron(handler.cron_choices["every_2hour_00"], 
                    handler.cloudConnection_command, 
                    handler.cloudConnection_output)
    """

    ### system monitoring
    # run system_monitoring every 2 minutes
    handler.addCron(handler.cron_choices["every_2min"], 
                    handler.systemMonitoring_command)
    
    handler.writeCronToFile()

    # works on linux only
    updateCrontabInSystem(handler.outputFile_path)
