"""
SystemMonitoring: This class rules the system monitoring.

Requirements:

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                           Date:
v0.0.1      (AS) First initialize. Added random numbers to test.            10.08.2020\n
"""

from configuration import *
from mqtt_connection import MQTTConnection
import os, time

class SystemMonitoring:
    """ 
    SystemMonitoring: This class rules the system monitoring. Tracked values:
    -
    -
    
    Attributes:
    -----------
    user_name : str
        name of the current system (e.g. test1)
    module_name : str
        name of this class
    """

    user_name = global_user_name
    module_name = "SystemMonitoring"
    
    def __init__(self):
        self.mqtt = MQTTConnection()
        self.msg = "temperature,modul={0},user={1}".format(self.module_name,
                                                                self.user_name)
        pass

    def uploadTemperatures(self):
        temps_str = os.popen("cat /sys/devices/virtual/thermal/thermal_zone*/temp").read()
        types_str = os.popen("cat /sys/devices/virtual/thermal/thermal_zone*/type").read()
        temps = temps_str.split("\n") 
        types = types_str.split("\n")
        index = 0
        while(index < len(temps)-1 and index < len(types)-1):
            print("{}: {}".format(types[index], int(temps[index])/1000))    
            
            msg_temperature = self.msg + ",location={0} temperature={1}".format(types[index],
                                                                        int(temps[index])/1000)
            print(msg_temperature)
            self.mqtt.sendMessage(msg_temperature)
            index += 1

    def uploadSystemMeasurement(self):
        self.uploadTemperatures()
        """         
        cpu_temperature = 20
        msg = "temperature,location=CPU,modul={0},user={1}".format(self.module_name,
                                                                self.user_name)
        cpu_msg = msg + " temperature={}".format(cpu_temperature)
        print(cpu_msg)
        self.mqtt.sendMessage(cpu_msg)
        """

if __name__ == "__main__":
    monitoring = SystemMonitoring()
    monitoring.uploadSystemMeasurement()

    """
    while True:
        monitoring.uploadTemperatures()
        #monitoring.uploadSystemMeasurement()
        time.sleep(2)
    """
