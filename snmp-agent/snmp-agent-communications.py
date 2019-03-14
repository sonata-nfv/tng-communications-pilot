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
import signal
import sys
from functools import partial
import statistics
import time
import requests
import json


# Global variables
CONFIG= {}
LIST_VNF_MS = []
LIST_VNF_WAC = []
# BW_INTERVAL is defined as a global variable 
# to be able to call it form the signal handler
BW_INTERVAL = None


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
    get the average rate in BITS PER SECOND
    """
    # TODO add exception to this
    interface_octects = session.get(oid)

    # TODO check if the value is valid
    # TODO check if interval is 0 and raise error
    delta_bw = int(interface_octects.value) - int(bw_previous_octects)
    bw_value = delta_bw * 8 / interval 

    # sending 0 as the first value to avoid giving incorrect values 
    if int(bw_previous_octects) is 0:
        return 0,int(interface_octects.value)
 
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

def get_and_write_WAC_provisioned_and_registered_users(list_vnf_wac, oid_registered, oid_provisioned, filename_registered, filename_provisioned):
    """
    get provisioned and registered users from the WAC.
    Since the VNF-WAC gets the value from a single DB from VNF-BS 
    it is not necessary to check all of VNF-WAC instances  
    """ 
    
    # TODO add exception to this
    # We only get the value from the 1st WAC as all of them are exected to be the same

    for vnf_wac_instance_dict in list_vnf_wac:
        registered_users = vnf_wac_instance_dict['snmp_session'].get(oid_registered)
        provisioned_users = vnf_wac_instance_dict['snmp_session'].get(oid_provisioned)

    write_stat_in_file(filename_registered, str(registered_users.value))
    write_stat_in_file(filename_provisioned, str(provisioned_users.value))

    return 

def get_QoS_values_from_MS(list_ip_vnf_ms, qos_REST_port, qos_REST_path, filename_jitter, filename_pl):
    
    if (qos_REST_port != ''): 
        port_string = ':' + qos_REST_port.str()
    else:
        port_string = ''
    
    jitter_list = []
    packetLoss_list = []

    for ip_vnf_wac_instance in list_ip_vnf_ms:
        try:
            response_jitter = requests.get('http://'+ ip_vnf_wac_instance + port_string +'/stats/avg/qos/jitter')
            response_packetLoss = requests.get('http://'+ ip_vnf_wac_instance + port_string +'/stats/avg/qos/packetloss')
        except requests.exceptions.RequestException as e:  
            print(e)
            return

        try:     
            jitter_list.append(json.loads(response_jitter)["jitter"])
            packetLoss_list.append(json.loads(response_packetLoss)["packetLoss"])
        except:
            print('Erro reading QoS API')
            jitter_list.append(0)
            packetLoss_list.append(0)
        
    # we store the max values received from the VNF-MS
    write_stat_in_file(filename_jitter, str(max(jitter_list)))
    write_stat_in_file(filename_pl, str(max(packetLoss_list)))

    return


def write_stat_in_file(filename, value):
    """
    write the current stat value in the defined file
    """
    # TODO capture errors
    file_fh = open(filename,'w')
    file_fh.write(str(value))


def read_stat_in_file(filename):
    """
    read the previous stat value from the defined file
    """
    # TODO capture errors
    file_fh = open(filename,'r')
    return int(file_fh.read())

def load_config(conf_filename):
        """Loads the configuration file.
            Loads all VNFs which are going to be monitored
            the configuration file is expected to be updated automatically
            by the SSM when a new VNF is added/Removed for scale-out scale-in .
        """
        if not conf_filename:
             print("Configuration file must be defined in an environment variable called SNMP_CONF_FILE")
             sys.exit(1)
        if not os.path.exists(conf_filename):
            print("Defined configuration: " + str(conf_filename) + " not found")
            sys.exit(1) 

        with open(conf_filename, "r") as config_file:
            configuration = yaml.load(config_file)
            if not configuration:
                print("Invalid configuration file.")
                sys.exit(1)
            # TODO check if mandatory fileds are present   
            return configuration   

def signal_handler_terminate(sig, frame):
        # Stop the threads gracefully
        BW_INTERVAL.stop() 
        sys.exit(0)

if __name__ == "__main__":
    
    # defining signal handlers to stop the script gracefully
    signal.signal(signal.SIGINT, signal_handler_terminate)
    signal.signal(signal.SIGTERM, signal_handler_terminate)
   
    # getting conf file name from environment variable and loading it   
    conf_filename=os.environ.get('SNMP_CONF_FILE') 
    CONFIG = load_config(conf_filename)
    
    # Check that the path for the stats files exists and has permissions
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
    BW_INTERVAL = Interval(CONFIG['polling_interval'], calculate_mean_bw, args=[LIST_VNF_MS,CONFIG['oid_media_network_interface'],filename,CONFIG['polling_interval']])
    
    #print ("Starting Interval, press CTRL+C to stop. Used interval: " + str(CONFIG['polling_interval']))
    BW_INTERVAL.start() 
    
    # Get provisioned and registered users values
    filename_registered = CONFIG['stats_file_path'] + CONFIG['wac_registered_file']
    filename_provisioned = CONFIG['stats_file_path'] + CONFIG['wac_provisioned_file']
    WAC_INTERVAL = Interval(CONFIG['polling_interval'], get_and_write_WAC_provisioned_and_registered_users , args=[LIST_VNF_WAC,CONFIG['oid_wac_registered_users'],CONFIG['oid_wac_provisioned_users'],filename_registered,filename_provisioned])
    
    WAC_INTERVAL.start()

    # Obtain PL and jitter values
    filename_jitter = CONFIG['stats_file_path'] + CONFIG['jitter_file']
    filename_pl = CONFIG['stats_file_path'] + CONFIG['pl_file']
    QoS_INTERVAL = Interval(CONFIG['polling_interval'] + 5, get_QoS_values_from_MS, args=[CONFIG['vnf-ms'],CONFIG['qos_REST_port'],CONFIG['qos_REST_path'],filename_jitter, filename_pl])

    QoS_INTERVAL.start()

    # loop to be able to capture the signals and stops the threads
    while True:
        time.sleep(1)
   