
#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

__metaclass__ = type
import pprint
from sys import api_version
import requests
from ansible.module_utils.basic import AnsibleModule
from distutils.version import LooseVersion
import json


#https://docs.ansible.com/ansible/latest/dev_guide/testing_documentation.html#testing-module-documentation

DOCUMENTATION = r'''
---
module: check_mk

short_description: Add host to check_mk trought API REST

version_added: "1.0.0"

description: Permit to add host with the CheckMK API REST, the are various options to customize the add.

options:
    hostname:
        description: This is the name of the host you want to add.
        required: true
        type: str
    url:
        description: This is the URL of the checkmk server.
        required: true
        type: str
    username:
        description: This is the username of the automation user who will interract with the API.
        required: true
        type: str
    secret: 
        description: This is the secret of the automation user  
        required: true
        type: str
    folder:
        description: Indicate which check_mk folder you want to put your host in   
        required: false
        type: str
        default: /
    state:
        description: Indicate to add or delete the host  
        required: false
        type: str
        default: present
    discover_services:
        description: 
          - Indicate if you want to discover the services of the host
          - See https://docs.checkmk.com/latest/en/rest_api.html
        required: false
        type: str
        default: ""
        choices:
          - new
          - remove
          - fix_all
          - refresh
          - only_host_labels
    activate_changes:
        description: Indicate if you want to commit the changes you bring  
        required: false
        type: bool
        default: True
    trustcerts:
        description: Indicate if you trust the certificate of the URL will be used  
        required: false
        type: bool
        default: True
    
author:
    - Ramuskay (@ramuskay)

'''

EXAMPLES = r'''
- name : Add host to check_mk server
  check_mk:
    hostname: myhost
    url: http://example.com/check_mk
    username: automation
    secret: 123456789
    state: present
  delegate_to: localhost
'''

RETURN = r'''
'''


class CMK:
    def __init__(self, module):
        self.module = module
        for key,value in module.params.items():
            setattr(self, key, value)
        self.sitename = self.url.split("/")[3]
        self.api =  self.url + "/check_mk/api/1.0"
        self.session = requests.session()
        self.session.headers['Authorization'] = f"Bearer "+ self.username + " " + self.secret
        self.session.headers['Accept'] = 'application/json' 
        self.api_web = self.url + "/check_mk/webapi.py?_username=" + self.username + "&_secret=" + self.secret
        self.websession = requests.Session()
        self.changed = False
    
    def apiAction(self,api,json={},method="post",params={},failed=True):
        if method=="post":
            resp = self.session.post(api,params=params, 
                headers={
                    "Content-Type": 'application/json',  # (required) A header specifying which type of content is in the request/response body.
                },
                json=json,verify=self.trustcerts)
        elif method=="delete":
            resp = self.session.delete(api,params=params, 
                headers={
                    "Content-Type": 'application/json',  # (required) A header specifying which type of content is in the request/response body.
                },
                json=json,verify=self.trustcerts)        
        else:
            print
            resp = self.session.get(api,params=params, 
                headers={
                    "Content-Type": 'application/json',  # (required) A header specifying which type of content is in the request/response body.
                },
                json=json,verify=self.trustcerts)

        print(resp.status_code)
        if resp.status_code == 200 or resp.status_code == 204:
            return True
        elif failed is True:
            self.module.fail_json(msg=resp.json())
        else:
            return False         


    def verifExist(self):   
        url = f"{self.api}/objects/host_config/{self.hostname}"
        return self.apiAction(url,failed=False,method='get')

    
    def createHost(self):
        url = f"{self.api}/domain-types/host_config/collections/all"
        json={'host_name' : self.hostname}
        if self.folder:
            json['folder'] = self.folder
        if self.attributes:
            json['attributes'] = self.attributes
        self.changed = True
        return self.apiAction(url,json=json)


    def deleteHost(self):
        url = f"{self.api}/objects/host_config/{self.hostname}"
        self.changed = True
        return self.apiAction(url,method="delete")

    def discoveryHost(self):

        ## It doesn't work with Checkmk Free Edition 2.1.0b9
        ## See https://forum.checkmk.com/t/rest-api-problem-with-service-discovery/31724
        resp = self.session.post(
            f"{self.api}/objects/host/{self.hostname}/actions/discover_services/invoke",
            headers={
                "Content-Type": 'application/json',  # (required) A header specifying which type of content is in the request/response body.
            },
            json={'mode': self.discover_services}
        )
        # resp = self.websession.post(self.api_web + "&action=discover_services&mode=" + self.discover_services, data={"hostname": self.hostname},verify=self.trustcerts,)
                
        if resp.status_code == 200 or resp.status_code == 204:
            self.changed = True
            return True
        else:
            raise RuntimeError(pprint.pformat(resp.json()))

    def activateChanges(self):
        
        url = f"{self.api}/domain-types/activation_run/actions/activate-changes/invoke"
        json = {'redirect': False,'sites': [self.sitename],'force_foreign_changes': False}
        return self.apiAction(url,json=json)

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        hostname = dict(type='str',require=True), 
        url = dict(type='str',require=True), 
        username = dict(type='str',require=True), 
        secret = dict(type='str',require=True), 
        folder = dict(type='str', default="/"),
        attributes = dict(type="dict"),
        state = dict(type='str',default="present"),
        activate_changes= dict(type='bool',default=True), 
        trustcerts= dict(type='bool', default=True),
        discover_services = dict(type='str',choices=["new", "remove", "fixall", "refresh"]) 
    )

    result = dict(
        changed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )


    
    obj = CMK(module)

    obj.verifExist()

    if module.check_mode:
        module.exit_json(**result)

    if obj.verifExist() and module.params['state'] == "absent":
        result['delete']=obj.deleteHost()
    elif not obj.verifExist() and module.params['state'] == "present":
        result['create']=obj.createHost()
        obj.discover_services = "new"
        obj.discoveryHost()
    elif module.params['discover_services']: 
        obj.discoveryHost()

    
    if obj.changed is True and obj.activate_changes is True:
        obj.activateChanges()

    
    result['changed'] = obj.changed

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()








