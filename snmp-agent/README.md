[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)

<p align="center"><img src="https://github.com/sonata-nfv/tng-communications-pilot/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# SNMP agent Communication
This folder contains the required configuration to install and configure an SNMP agent server and the required SNMP services inside the VNFs in order to monitor different values required from the service.  

## Dependencies

- **Ansible v2.5**
```
[sudo] apt install ansible
```

## Folder structure

| Folder | Comment |
| --- | --- |
| `roles/snmp-agent-communications` | Element to gather the SNMP values from the other VNFs and provides them as SNMP variables |
| `roles/snmpd` | SNMP installed in the different VNFs to gather the information |
| `vars` | Configuration for the SNMP server |
| `hosts.yml` | Contains information about the different machines involved in the installation process carried out by the Ansible |
| `snmp-agent-communication-playbook.yml` | The `snmp agent` service and the `snmpd service` can be deployed in the remote servers using this Ansible playbook  |
| `snmp-agent-communications.py` | Script in charge of gathering the information in WAAC and MS VNF |
| `snmp-agent-communications.yml` | Contains information about the different SNMP servers installed in the VNFs so that all the information can be gathered by the SNMP proxy |

## Installation with Ansible
Both the `snmp agent service` and the `snmpd` service can be deployed in the remote servers using the Ansible playbook included in this folder.

### Steps to configure the system
1. Configure hosts where to install the service in the file `hosts.yml`
1. Configure system and SNMP-related variables in the file `vars/common.yml`
1. Configure the `/etc/ansible/hosts` with the VNF-RP details:

	```
	[vnf-rp]
	[IP ansible_ssh_user=ubuntu ansible_python_interpreter=/usr/bin/python3 ansible_become_pass=5GT4NG0 ansible_ssh_private_key_file=/home/ubuntu/.ssh/id_rsa
	```

	or this in case of using a file to authenticate:

	```
	[vnf-rp]
	[IP ansible_ssh_user=ubuntu ansible_python_interpreter=/usr/bin/python3 ansible_ssh_private_key_file=<path_to_key_file>
	```

1. Launch the playbook command. It is possible to install the VNFs one by one using the tags or all of them in the same execution by omitting the tags. The command must be called this way:

	```
	ansible-playbook snmp-agent-communication-playbook.yml --inventory-file hosts.yml --tags <VNF ID to deploy the service>  
	```
	
	The valid tag values ( < VNF ID to deploy the service > ) are as follows:
	- **vnf-rp**: Installation in the VNF reverse Proxy. This tag instructs the installation of both the `SNMP Agent service` and `snmpd` with the configuration needed to offer the BW (bandwith), PL (Packet Loss) and Jitter values from the VNF-MS and the user load (registered and provisioned users) from VNF-WAC.
	- **vnf-wac**: Installation in the VNF WAC. It installs `snmpd` with the configuration needed to offer the BW (bandwith), PL (Packet Loss) and Jitter values. This values are read by the SNMP agent deployed in VNF-RP. The SNMP agent service processes the data from all the instances of the WAC to offer a single figure to the monitoring system.
	- **vnf-ms** (VNF-MS): Installation in the VNF MS of the `snmpd` with the configuration needed to offer the BW (bandwith), PL (Packet Loss) and Jitter values. This values are read by the SNMP agent deployed in VNF-RP. The SNMP agent service processes the data from all the instances of the MS to offer a single figure to the monitoring system.

#### Relevant considerations
Please note that this script is intended for an initial setup. The deployed VNFs must already contain the right snmpd configuration. For example, the configuration file of the SNMP agent must be updated by the SSM when a new VNF-WAC or VNF-MS are provisioned.

#### SNMP configuration file
The behaviour of this script is configured in YAML file `snmp-agent-communications.yml`. By default it is located in the same folder as the script and the name will be the same ended in .yml. The list below contains all the mandatory fields which need to be provisioned:

- **List of VNF-WAC to be monitored**
	This list will contain he IPs or hostnames of the VNF-WAC instances accesible from the VNF-RP and which have to be monitored. These values are expected to be updated by the FSM.

	```
	vnf-wac:
	- 192.168.56.102
	```

- **List of VNF-WAC to be monitored.**
	This list will contain he IPs or hostnames of the VNF-MS instances accesible from the VNF-RP and which have to be monitored. These values are expected to be updated by the FSM.

	```
	vnf-ms:
	- 192.168.56.102
	- 192.168.56.102
	```

- **Media network interface OID.**
	This is the OID the interface which handles the media (the one which needs to be monitored to check the quality of the service).
	**This parameter may depend on the final deployment, so please check that the OID corresponds to the interface which is handling the media. Using a different OID will prevent the system from scaling in and out according to the consumed BW.**

	```
	oid_media_network_interface: .1.3.6.1.2.1.2.2.1.11.2
	```

- **Polling interval.**
	This value represents the polling interval used to get values from the VNFs. Please note that a very low interval can lead to high load in the system.

	```
	polling_interval: 30 
	```

- **SNMP security parameters.**
	These parameters below are the SNMP security credentials which will be used to access the SNMP variables. Please note that only SNMPv3 is supported. `auth_and_privay` is the recommended security mode.

	```
	security_level: auth_with_privacy
	security_username: quobis
	auth_protocol: SHA 
	auth_password: asterisk
	privacy_protocol: AES
	privacy_password: asterisk
	```

- **Internal settings (default values can be normally used safely).**
	The fields below define where the calculated values are going to be stored. If the path does not exist, it will be created. Please note that the `snmp-agent-communication.py` must have permissions to write in the defined folder.

	```
	stats_file_path : /tmp/
	bw_file : bw.txt
	pl_file : pl.txt
	jitter_file : jitter.txt  
	```

## Services offered

Ansible installs the SNMP service so that the instances of the Communication pilot are able to provide a pool of features enabling monitoring.

### SNMP agent service

The script `snmp-agent-communication.py` is used to read the values from WAC and MS VNFs and stores them in simple text files, so that they can be read by scripts called by `snmpd`. This means that this script just reads the values from the VNFs, normalizes them and calculates the mean values before storing them.  

This is a Python 3 script not compatible with Python 2.X.

### SNMP monitoring of processes

The `snmpd` daemon also enables the monitoring of process and the check of the current values as OID variables. As a first approach, to monitor the availability of the video-conference service, the pm2 daemon is going to be monitored. This process is in charge of launching all the Node processes required to get the service working and also watchs the running processes to restart services when they crash. 

In order to achieve this we only need to add one line per process in the file: `/etc/snmp/snmpd.conf`:

**Process Monitoring:** `proc pm2-God-Daemon 1 1`

**Note:** During our test we detected that the process names with whitespaces are not correctly monitored. In order to work around this we changed the name which is used to launch pm2 setting an environment variable in the systemctl script (`/etc/systemd/system/pm2-root.service`):

`Environment=PM2_DAEMON_TITLE=pm2-God-Daemon`
