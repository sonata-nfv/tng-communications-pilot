#!/usr/bin/python3

#  Copyright (c) 2018 SONATA-NFV, 5GTANGO, UBIWHERE, QUOBIS SL.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO, UBIWHERE, QUOBIS
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).
#
# This work has also been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.5gtango.eu).

# Python packages imports
import logging
import easysnmp
import yaml
import os
import threading
from functools import partial
import statistics
import time


# Global variables
CONFIG= {}
LIST_VNF_MS = []
LIST_VNF_WAC = []

# Constants
CONF_FILE_PATH = 'snmp-agent-communications.yml'


# List of files to store variables
STATS_FILE_PATH = '/var/communications/'
BW_FILE = 'bw.txt'
PL_FILE = 'pl.txt'
JITTER_FILE = 'jitter.txt'


class Interval(object):

    def __init__(self, interval, function, args=[], kwargs={}):
        """
        Runs the function at a specified interval with given arguments.
        """
        self.interval = interval
        self.function = partial(function, *args, **kwargs)
        self.running  = False 
        self._timer   = None 

    def __call__(self):
        """
        Handler function for calling the partial and continuting. 
        """
        self.running = False  # mark not running
        self.start()          # reset the timer for the next go 
        self.function()       # call the partial function 

    def start(self):
        """
        Starts the interval and lets it run. 
        """
        if self.running:
            # Don't start if we're running! 
            return 
            
        # Create the timer object, start and set state. 
        self._timer = threading.Timer(self.interval, self)
        self._timer.start() 
        self.running = True

    def stop(self):
        """
        Cancel the interval (no more function calls).
        """
        if self._timer:
            self._timer.cancel() 
        self.running = False 
        self._timer  = None


def calculate_bw(oid, interval, session, bw_previous_octects):
    """
    calculate the average BW used by a single VNF during the interval process
    it checks the specified OID which provides the BW consumed in bytes
    then the previous value is subsctracted to get the bits (bytes*8) used in 
    the interval. Finally it is divided by the interval in seconds to
    get the average rate in bits per second
    """
    
    interface_octects = session.get(oid)
    # TODO check if the value is valid
    delta_bw = int(interface_octects.value) - int(bw_previous_octects)
    bw_value = delta_bw * 8 / interval 

    return int(bw_value),int(interface_octects.value)
    
def calculate_mean_bw(list_vnf_ms,oid,filename,polling_interval):
    """
    calculate the average BW used by all the VNF-MS during the interval process
    """
    bw_current_values = []
    for vnf_ms_instance_dict in list_vnf_ms:
        bw_value, vnf_ms_instance_dict['bw_previous_octect'] = calculate_bw(oid, polling_interval, vnf_ms_instance_dict['snmp_session'], vnf_ms_instance_dict['bw_previous_octect'])
        bw_current_values.append(bw_value)

    #print("Mean value: "+str(mean(bw_current_values))+" bps")
    write_stat_in_file(filename, str(statistics.mean(bw_current_values)))
    return


def write_stat_in_file(filename, value):
    """
    write the current stat value in the defined file
    """
    file_fh = open(filename,'w')
    file_fh.write(str(value))


def read_stat_in_file(filename):
    """
    read the previous stat value from the defined file
    """
    file_fh = open(filename,'r')
    return int(file_fh.read())

def load_config():
        """Loads the configuration file.
            Loads all VNFs which are going to be monitored
            the configuration file is expected to be updated automatically
            by the SSM when a new VNF is added/Removed for scale-out scale-in .
        """
        if not os.path.exists(CONF_FILE_PATH):
            configuration = {}
            return configuration

        with open(CONF_FILE_PATH, "r") as config_file:
            configuration = yaml.load(config_file)
            if not configuration:
               configuration = {}
               return configuration
            # TODO check if mandatory fileds are present   
            return configuration   

# Read configuration

if __name__ == "__main__":
   
    CONFIG = load_config()
    
    # Check that the path exists
    if not os.path.exists(CONFIG['stats_file_path']):
        os.makedirs(CONFIG['stats_file_path'])

    # Create list of dict with SNMP session object to MS VNFs and bw_previous_octect value
    for vnf_ms_instance in CONFIG['vnf-ms']:
        snmp_session_instance = easysnmp.Session(hostname=vnf_ms_instance,version=3,security_level=CONFIG['security_level'],auth_protocol=CONFIG['auth_protocol'],security_username=CONFIG['security_username'],privacy_protocol=CONFIG['privacy_protocol'],auth_password=CONFIG['auth_password'],privacy_password=CONFIG['privacy_password'])
        LIST_VNF_MS.append({'snmp_session':snmp_session_instance,'bw_previous_octect':0})

    # Create list of dict with SNMP session object to WAC VNFs
    for vnf_wac_instance in CONFIG['vnf-wac']:
        snmp_session_instance = easysnmp.Session(hostname=vnf_wac_instance,version=3,security_level=CONFIG['security_level'],auth_protocol=CONFIG['auth_protocol'],security_username=CONFIG['security_username'],privacy_protocol=CONFIG['privacy_protocol'],auth_password=CONFIG['auth_password'],privacy_password=CONFIG['privacy_password'])
        LIST_VNF_WAC.append({'snmp_session':snmp_session_instance})
    
    filename = CONFIG['stats_file_path'] + CONFIG['bw_file']
    bw_interval = Interval(CONFIG['polling_interval'], calculate_mean_bw, args=[LIST_VNF_MS,CONFIG['oid_media_network_interface'],filename,CONFIG['polling_interval']])
    
    #print ("Starting Interval, press CTRL+C to stop. Used interval: " + str(CONFIG['polling_interval']))
    bw_interval.start() 


    # while True:
    #     try:
    #         time.sleep(0.1)
    #     except KeyboardInterrupt:
    #         print("Shutting down interval ...")
    #         bw_interval.stop()
    #         break



# PL and JITTER

## Janus will already provide the PL and Jitter for each call
## need to get all the values for all the current calls and then calculate the mean. 
## analyze what to do for inbound and outbound streams.


