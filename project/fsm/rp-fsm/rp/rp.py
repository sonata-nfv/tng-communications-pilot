"""
Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO
ALL RIGHTS RESERVED.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
Neither the name of the SONATA-NFV, 5GTANGO
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.
This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the SONATA
partner consortium (www.sonata-nfv.eu).
This work has been performed in the framework of the 5GTANGO project,
funded by the European Commission under Grant number 761493 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the 5GTANGO
partner consortium (www.5gtango.eu).
"""

import logging
import yaml
import time
from smbase.smbase import smbase
try:
    from rp import ssh
except:
    import ssh

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("fsm-start-stop-configure")
LOG.setLevel(logging.DEBUG)
logging.getLogger("son-mano-base:messaging").setLevel(logging.INFO)


class rpFSM(smbase):

    def __init__(self, connect_to_broker=True):
        """
        :param specific_manager_type: specifies the type of specific manager
        that could be either fsm or ssm.
        :param service_name: the name of the service that this specific manager
        belongs to.
        :param function_name: the name of the function that this specific
        manager belongs to, will be null in SSM case
        :param specific_manager_name: the actual name of specific manager
        (e.g., scaling, placement)
        :param id_number: the specific manager id number which is used to
        distinguish between multiple SSM/FSM that are created for the same
        objective (e.g., scaling with algorithm 1 and 2)
        :param version: version
        :param description: description
        """

        self.sm_id = "sonfsmcommunication-pilotrp-vnfcss1"
        self.sm_version = "0.1"

        super(self.__class__, self).__init__(sm_id=self.sm_id,
                                             sm_version=self.sm_version,
                                             connect_to_broker=connect_to_broker)

    def on_registration_ok(self):

        # The fsm registration was successful
        LOG.debug("Received registration ok event.")

        # send the status to the SMR
        status = 'Subscribed, waiting for alert message'
        message = {'name': self.sm_id,
                   'status': status}
        self.manoconn.publish(topic='specific.manager.registry.ssm.status',
                              message=yaml.dump(message))

        # Subscribing to the topics that the fsm needs to listen on
        topic = "generic.fsm." + str(self.sfuuid)
        self.manoconn.subscribe(self.message_received, topic)
        LOG.info("Subscribed to " + topic + " topic.")

    def message_received(self, ch, method, props, payload):
        """
        This method handles received messages
        """

        # Decode the content of the message
        request = yaml.load(payload)

        # Don't trigger on non-request messages
        if "fsm_type" not in request.keys():
            LOG.info("Received a non-request message, ignoring...")
            return

        # Create the response
        response = None

        # the 'fsm_type' field in the content indicates for which type of
        # fsm this message is intended.
        if str(request["fsm_type"]) == "start":
            LOG.info("Start event received: " + str(request["content"]))
            response = self.start_event(request["content"])

        if str(request["fsm_type"]) == "stop":
            LOG.info("Stop event received: " + str(request["content"]))
            response = self.stop_event(request["content"])

        if str(request["fsm_type"]) == "configure":
            LOG.info("Config event received: " + str(request["content"]))
            response = self.configure_event(request["content"])

        # If a response message was generated, send it back to the FLM
        LOG.info("Response to request generated:" + str(response))
        topic = "generic.fsm." + str(self.sfuuid)
        corr_id = props.correlation_id
        self.manoconn.notify(topic,
                             yaml.dump(response),
                             correlation_id=corr_id)
        return

    def start_event(self, content):
        """
        This method handles a start event.
        """

        # Dummy content
        response = {'status': 'completed'}
        return response

    def stop_event(self, content):
        """
        This method handles a stop event.
        """

        # Dummy content
        response = {'status': 'completed'}
        return response

    def configure_event(self, content):
        """
        This method handles a configure event. The configure event changes the configuration
        of the nginx and modifies it whenever a new VNF-WAC or VNF-MS is added or removed
        from the system.
        """

        # Extract VNF-RP management IP and VNF-WAC internal IP
        wac_ip_list = []
        wac_ip = ''
        rp_ip = ''
        ms_ip = ''
        ds_ip = ''
        bs_ip = ''

        for vnfr in content['vnfrs']:
            if vnfr['virtual_deployment_units'][0]['vdu_reference'][:3] == 'wac':
                for cp in vnfr['virtual_deployment_units'][0]['vnfc_instance'][0]['connection_points']:
                    if cp['id'] == 'internal':
                        wac_ip_list.append(cp['interface']['address'])
                        break

            if vnfr['virtual_deployment_units'][0]['vdu_reference'][:2] == 'rp':
                for cp in vnfr['virtual_deployment_units'][0]['vnfc_instance'][0]['connection_points']:
                    if cp['id'] == 'mgmt':
                        rp_ip = cp['interface']['address']
                        break


            if vnfr['virtual_deployment_units'][0]['vdu_reference'][:2] == 'ms':
                for cp in vnfr['virtual_deployment_units'][0]['vnfc_instance'][0]['connection_points']:
                    if cp['id'] == 'internal':
                        ms_ip = cp['interface']['address']
                        break

            if vnfr['virtual_deployment_units'][0]['vdu_reference'][:2] == 'ds':
                for cp in vnfr['virtual_deployment_units'][0]['vnfc_instance'][0]['connection_points']:
                    if cp['id'] == 'internal':
                        ds_ip = cp['interface']['address']
                        break

            if vnfr['virtual_deployment_units'][0]['vdu_reference'][:2] == 'bs':
                for cp in vnfr['virtual_deployment_units'][0]['vnfc_instance'][0]['connection_points']:
                    if cp['id'] == 'internal':
                        bs_ip = cp['interface']['address']
                        break

        LOG.info('rp ip: ' + rp_ip)
        LOG.info('ms ip: ' + ms_ip)
        LOG.info('ds ip: ' + ds_ip)
        LOG.info('bs ip: ' + bs_ip)

        # Initiate SSH connection with the VM
        ssh_client = ssh.Client(rp_ip, username='ubuntu', logger=LOG,
                                key_filename='/root/rp/sandbox.pem', retries=40)

        # Remove server IP address
        ssh_client.sendCommand(
            "sudo sed  -i -r '/server ((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|\s|$)){4}.*$/d' /etc/nginx/sites-enabled/wac-nginx.conf")

        # Include VNF-WAC IP address
        for wacIP in wac_ip_list:
            ssh_client.sendCommand("sudo sed -i '/hash \$remote\_addr\;/ a " +
                                    "\  server " + wacIP + " max_fails=2 fail_timeout=5s;" + "' /etc/nginx/sites-enabled/wac-nginx.conf")

            ssh_client.sendCommand("sudo sed -i -r '/upstream wac_pushreg \{/ a \  server " + wacIP + ":8228;' /etc/nginx/sites-enabled/wac-nginx.conf")
            wac_ip = wacIP

        # Change SFU1 IP
        ssh_client.sendCommand("sudo sed -r -i '/\:9030\/socket.io/c\        proxy_pass http\:\/\/" + ms_ip + "\:9030\/socket.io\/\;' /etc/nginx/sites-enabled/wac-nginx.conf")

        # copy template file to be modified with sed command
        ssh_client.sendCommand("sudo cp /opt/health-script/health.sh.template /opt/health-script/health.sh")
        # Change health.sh
        ssh_client.sendCommand(
            "sudo sed -i 's/DS_IP/" + ds_ip + "/g' /opt/health-script/health.sh")
        ssh_client.sendCommand(
            "sudo sed -i 's/WAC_IP/" + wac_ip + "/g' /opt/health-script/health.sh")
        ssh_client.sendCommand(
            "sudo sed -i 's/MS_IP/" + ms_ip + "/g' /opt/health-script/health.sh")
        ssh_client.sendCommand(
            "sudo sed -i 's/BS_IP/" + bs_ip + "/g' /opt/health-script/health.sh")

        ssh_client.sendCommand("screen -d -m /opt/health-script/health.sh")
        # Restart the service with new configuration applied
        ssh_client.sendCommand("sudo systemctl restart nginx")

        if ssh_client.connected:
            response = {'status': 'COMPLETED', 'error': 'None'}
        else:
            response = {'status': 'FAILED', 'error': 'FSM SSH connection failed'}
        return response


def main():
    rpFSM()


if __name__ == '__main__':
    main()
