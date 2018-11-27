[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)

<p align="center"><img src="https://github.com/sonata-nfv/tng-communications-pilot/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# SNMP agent Communication

## snmp-agent-communication.py
This script will read  values from WAC and MS VNFs and stores the values in simple text files so that it can be read by scripts called by `snmpd`. This means that this script just read the values from the VNF, normalizes and calculate a mean of the values and stores them in files.  
This is a Python 3 script not compatible with Python 2.X.


### Configuration file
The behaviour of this script is configured in YAML file. By default it is located in the same folder as the script and the name will be the same ended in `.yml`.
Below you can find all the mandatory fields which need to be provisioned:

This list will contain he IPs or hostnames of the VNF-WAC instances accesible from the VNF-RP and which have to be monitored. These values are expected to be updated by the SSM.

```
vnf-wac:
 - 192.168.56.102
```

This list will contain he IPs or hostnames of the VNF-MS instances accesible from the VNF-RP and which have to be monitored. These values are expected to be updated by the SSM.
```
vnf-ms:
 - 192.168.56.102
 - 192.168.56.102
```

This is the OID the interface which handles the media (the one which needs to be monitored to check the quality of the service). This may depend on the final deployment.
```
oid_media_network_interface: .1.3.6.1.2.1.2.2.1.11.2
```

This value represents the polling interval used to get values from the  VNFs. Please note that a very low interval can lead to high load in the system.
```
polling_interval: 30 
```

These parameters below are the SNMP security credentials which will be used to access the SNMP variables. Please note that only SNMPv3 is supported. auth_and_privay is the recommended security mode.

```
security_level: auth_with_privacy
security_username: quobis
auth_protocol: SHA 
auth_password: asterisk
privacy_protocol: AES
privacy_password: asterisk
```

The fields below define where the calculated values are going to be stored. If the path does not exist it will be created. Please note that the `snmp-agent-communication.py`
must have permissions to write in the defined folder.

```
stats_file_path : /tmp/
bw_file : bw.txt
pl_file : pl.txt
jitter_file : jitter.txt  
```


