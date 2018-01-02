from jinja2 import Environment
from jinja2 import FileSystemLoader
import os
import requests
import json

from time import gmtime, strftime

DIR_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
JSON_TEMPLATES = Environment(loader=FileSystemLoader(DIR_PATH + '/json_templates'))
SNAPSHOT_PATH = DIR_PATH + '/snapshots'


class ApicController:
    token = ""
    url = ""

    def get_token(self, username, password):
        """
        Returns authentication token
        :param url:
        :param username:
        :param password:
        :return:
        """
        template = JSON_TEMPLATES.get_template('login.j2.json')
        payload = template.render(username=username, password=password)
        auth = self.makeCall(p_url='/api/aaaLogin.json', data=payload, method="POST").json()
        login_attributes = auth['imdata'][0]['aaaLogin']['attributes']
        return login_attributes['token']

    def makeCall(self, p_url, method, data=""):
        cookies = {'APIC-Cookie': self.token}
        if method == "POST":
            response = requests.post(self.url + p_url, data=data, cookies=cookies, verify=False)
        elif method == "GET":
            response = requests.get(self.url + p_url, cookies=cookies, verify=False)
        if 199 < response.status_code < 300:
            return response
        else:
            raise Exception(json.loads(response.text)['imdata'][0]['error']['attributes']['text'])

    def getSwitches(self, pod_dn):
        switches = self.makeCall(
            p_url='/api/node/mo/' + pod_dn + '.json?query-target=children&target-subtree-class=fabricNode&query-target-filter=and(ne(fabricNode.role,"controller"))',
            method="GET").json()['imdata']
        return switches

    def getPods(self):
        pods = self.makeCall(p_url='/api/node/class/fabricPod.json', method="GET").json()['imdata']
        return pods

    def saveSnapshot(self, switch_dn, filename, type):
        """
        Saves the configuration of interfaces
        :param switch_dn:
        :return:
        """
        if type == "interfaces":
            interfaces = self.makeCall(
                p_url='/api/node/class/' + switch_dn + '/l1PhysIf.json?rsp-subtree=children&rsp-subtree-class=ethpmPhysIf&order-by=l1PhysIf.id',
                method="GET").json()['imdata']
            apic_dir = self.url.replace("http:", "").replace("https:", "").replace("/", "")
            if not os.path.isdir(SNAPSHOT_PATH + "/" + apic_dir):
                os.makedirs(SNAPSHOT_PATH + "/" + apic_dir)
            snapshot_file = open(
                SNAPSHOT_PATH + "/" + apic_dir + "/interfaces-" + filename + "_" + strftime("%Y-%m-%d-%H-%M-%S",
                                                                                 gmtime()) + ".txt", 'w')
            for interface in interfaces:
                for attribute in interface['l1PhysIf']["attributes"].keys():
                    snapshot_file.write(attribute + "=" + interface['l1PhysIf']["attributes"][attribute] + "\n")
                snapshot_file.write("\n")

            snapshot_file.close()
        elif type == "isis-routes":
            isis_routes = self.makeCall(
                p_url='/api/node/mo/' + switch_dn + '/sys/isis/inst-default/dom-overlay-1.json?query-target=subtree&target-subtree-class=isisRoute&order-by=isisRoute.pfx',
                method="GET").json()['imdata']
            apic_dir = self.url.replace("http:", "").replace("https:", "").replace("/", "")
            if not os.path.isdir(SNAPSHOT_PATH + "/" + apic_dir):
                os.makedirs(SNAPSHOT_PATH + "/" + apic_dir)
            snapshot_file = open(
                SNAPSHOT_PATH + "/" + apic_dir + "/isisroute-" + filename + "_" + strftime("%Y-%m-%d-%H-%M-%S",
                                                                                 gmtime()) + ".txt", 'w')
            for route in isis_routes:
                snapshot_file.write(route['isisRoute']["attributes"]["pfx"])
                snapshot_file.write("\n")

            snapshot_file.close()
