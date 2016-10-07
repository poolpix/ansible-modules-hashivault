#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_unseal
version_added: "1.2.0"
short_description: Hashicorp Vault unseal module
description:
    - Module to unseal Hashicorp Vault.
options:
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    verify:
        description:
            - verify TLS certificate
        default: to environment variable VAULT_SKIP_VERIFY
    authtype:
        description:
            - authentication type to use: token, userpass, github, ldap
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
        default: False
    password:
        description:
            - password to login to vault.
        default: False
    key:
        description:
            - vault key shard.
        default: False
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_unseal:
      key: '{{vault_key}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['key'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_unseal(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *

if __name__ == '__main__':
    main()
