## Implementation
This SSM was implemented in Python 3.4

[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)

<p align="center"><img src="https://github.com/sonata-nfv/tng-communications-pilot/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# SSM
This contains the SSM used by the communications pilot. They will be used to configure all the content received by the VNFs during the instantiation process. This means, content will be expanded with additional information about the VNFs deployment.

## Folder structure

| Folder | Comment |
| --- | --- |
| `base` | Dependencies needed to create the Docker container |
| `videoconference` | SSM file containing defined events |

## Dependencies
* amqp-storm

## Test SSM locally
For now, the SSM has only one event defined, the task_event. In order to test it, we need the `tng-sdk-sm` tool and ...

**Generate the payload**
1. ...

**task_event test**
After this, the SS; can be tested with the following command:

`tng-sm execute --event task --payload <path_to_payload_event> --path <path_fsm_folder>`

## Build and publish the container
Container can already be found published in `anapolg/tng-rp-fsm:latest`. In any form, to build and publish the container go to the fsm folder and execute:

```
docker build --no-cache -f videoconference-ssm/Dockerfile -t <name:tag> .
docker push <name:tag>
```


## Lead Developers
The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

* Antón Román Portabales (anton.roman@quobis.com)
* Ana Pol González (ana.pol@quobis.com)
