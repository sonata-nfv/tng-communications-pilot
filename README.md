[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)

<p align="center"><img src="https://github.com/sonata-nfv/tng-communications-pilot/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# Communications pilot

The communications pilot aims to elaborate on the usability of 5GTANGO platform to provide a complete video conference service which handles real-time traffic using the 5GTANGO platform. Currently, the pilot focuses on the development of components that use the 5GTANGO platform for these four use cases:

1. Best-effort video-conference services
1. Premium video-conference services (Gold and Silver QoS)
1. Edge video-conference services
1. Video-conference scaling out/in services

## Folder structure

| Folder | Comment |
| --- | --- |
| `project/comm-pilot/sources/` | Project definition |
| `project/comm-pilot/sources/nsd` | Service descriptors |
| `project/comm-pilot/sources/vnfd` | Function descriptors |
| `project/scripts` | Scripts used to build the testing probes |
| `project/fsm` | FSMs used to configure the VNFs |
| `project/ssm` | SSM used to configure the NS |
| `snmp-agent` | SNMP ansible deployement in the service |

## Use cases description

### Best-effort video-conference services

This use case considers a network service which provides real-time communication capabilities to enable functionalities like video-conference, IM and other real-time collaboration tools. The service is deployed in the core of the operational infrastructure.

<p align="center"><img src="https://github.com/sonata-nfv/tng-communications-pilot/wiki/images/case1.png" /></p>

### Premium video-conference services (Gold and Silver QoS)

Video-conference service is sensitive to some of the QoS measures, such as bandwidth, packet loss or RTT. In this, we might consider offering two kind of services: one for premium users (Gold) with high QoS requirements and another one for free users (Silver) with lower QoS requirements. 

<p align="center"><img src="https://github.com/sonata-nfv/tng-communications-pilot/wiki/images/case2.png" /></p>

### Edge video-conference services

In this use case, we consider the improvement of the service through taking into account the delay-sensitive VNF, such as the VNF-MS.

<p align="center"><img src="https://github.com/sonata-nfv/tng-communications-pilot/wiki/images/case3.png" /></p>

### Video-conference scaling out/in services

The last use case, considers the need to increment the number of instances of some of the VNF.

<p align="center"><img src="https://github.com/sonata-nfv/tng-communications-pilot/wiki/images/case4.png" /></p>

## Network Service Components

The network service is composed by 5 VNF which are:

* VNF-RP: Reverse Proxy exposing the service and performing the load balance.
* VNF-WAC: Server managing the WebRTC communication.
* VNF-BS: Backend services needed by the system.
* VNF-DS: Dispatcher.
* VNF-MS: Media server.

## Test components 

The following scripts are used to generate probes able to test the services. More information about them can be found in the wiki page of the project. 
* **users.py:** Python script used to generate or remove users through the service REST API. 
* **check-registered-users.py:** Python script used to retrieve the number of registered users in the service.

## Lead Developers
The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

* Antón Román Portabales (anton.roman@quobis.com)
* Ana Pol González (ana.pol@quobis.com)
* Daniel Vila Falcón (daniel.vila@quobis.com)
