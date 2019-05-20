#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json
import sys
from ast import literal_eval

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_azure_secret_engine_config
version_added: "3.17.6"
short_description: Hashicorp Vault azure secret engine config
description:
    - Module to configure an azure secret engine via variables or json file
options:
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    ca_cert:
        description:
            - "path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate"
        default: to environment variable VAULT_CACERT
    ca_path:
        description:
            - "path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate : if ca_cert
             is specified, its value will take precedence"
        default: to environment variable VAULT_CAPATH
    client_cert:
        description:
            - "path to a PEM-encoded client certificate for TLS authentication to the Vault server"
        default: to environment variable VAULT_CLIENT_CERT
    client_key:
        description:
            - "path to an unencrypted PEM-encoded private key matching the client certificate"
        default: to environment variable VAULT_CLIENT_KEY
    verify:
        description:
            - "if set, do not verify presented TLS certificate before communicating with Vault server : setting this
             variable is not recommended except during testing"
        default: to environment variable VAULT_SKIP_VERIFY
    authtype:
        description:
            - "authentication type to use: token, userpass, github, ldap, approle"
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
        default: to environment variable VAULT_USER
    password:
        description:
            - password to login to vault.
        default: to environment variable VAULT_PASSWORD
    mount_point:
        description:
            - name of the secret engine mount name.
        default: 'azure'
    subscription_id:
        description:
            - azure SPN subscription id
    tenant_id:
        description:
            - azure SPN tenant id
    client_id:
        description:
            - azure SPN client id
    client_secret:
        description:
            - azure SPN client secret
    config_file:
        description:
            - alternate way to pass SPN vars. must be json object
    environment:
        description:
            - azure environment. you probably do not want to change this
        default: AzurePublicCloud
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_azure_secret_engine_config:
        subscription_id: 1234
        tenant_id: 5689-1234
        tenant_id: 5689-1234
        client_id: 1012-1234
        client_secret: 1314-1234

    - hashivault_azure_secret_engine_config:
        config_file: /home/drewbuntu/azure-config.json
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='azure')
    argspec['subscription_id'] = dict(required=False, type='str')
    argspec['tenant_id'] = dict(required=False, type='str')
    argspec['client_id'] = dict(required=False, type='str')
    argspec['client_secret'] = dict(required=False, type='str')
    argspec['environment'] = dict(required=False, type='str', default='AzurePublicCloud')
    argspec['config_file'] = dict(required=False, type='str', default=None)
    supports_check_mode=True
    required_together=[['subscription_id', 'client_id', 'client_secret', 'tenant_id']]

    module = hashivault_init(argspec, supports_check_mode, required_together)
    result = hashivault_azure_secret_engine_config(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_azure_secret_engine_config(module):
    params = module.params
    client = hashivault_auth_client(params)
    changed = True
    config_file = params.get('config_file')
    mount_point = params.get('mount_point')

    # if config_file is set, set sub_id, ten_id, client_id, client_secret from file
    # else set from passed args
    if config_file:
        config = json.loads(open(params.get('config_file'), 'r').read())
        tenant_id = config.get('tenant_id')
        subscription_id = config.get('subscription_id')
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')       
    else:
        tenant_id = params.get('tenant_id')
        subscription_id = params.get('subscription_id')
        client_id = params.get('client_id')
        client_secret = params.get('client_secret')

    # check if engine is enabled
    if sys.version_info[0] < 3:
        if (mount_point + "/") not in json.dumps(client.sys.list_mounted_secrets_engines()['data'].keys()):
            return {'failed': True, 'msg': 'secret engine is not enabled', 'rc': 1}
    elif (mount_point + "/") not in client.sys.list_mounted_secrets_engines()['data'].keys():
        return {'failed': True, 'msg': 'secret engine is not enabled', 'rc': 1}
    
    # check if current config matches desired config values, if they match, set changed to false to prevent action
    current = client.secrets.azure.read_config()
    if sys.version_info[0] < 3:
        changed = False
        current_dict = literal_eval(json.dumps(current))
        for k, v in current_dict.items():
            for k2, v2, in params.items():
                if k == k2:
                    if v != v2:
                        changed = True
    else:
        if current.items() < params.items():
            changed = False
    # if configs dont match and checkmode is off, complete the change
    if changed == True and not module.check_mode:
        result = client.secrets.azure.configure(tenant_id=tenant_id, subscription_id=subscription_id, client_id=client_id, client_secret=client_secret, mount_point=mount_point)
    
    return {'changed': changed}


if __name__ == '__main__':
    main()
