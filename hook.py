#! /usr/bin/env python2
from requests_kerberos import HTTPKerberosAuth, REQUIRED
from time import sleep

import logging
import os
import requests
import sys

# Create logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# Check for server
if "IPA_SERVER" not in os.environ:
    raise Exception("Missing IPA_SERVER in environment")

# Check for domain
if "IPA_DOMAIN" not in os.environ:
    raise Exception("Missing IPA_DOMAIN in environment")

# If use and password is set, use that
if ("IPA_USER" in os.environ) and ("IPA_PASSWORD" in os.environ):
    print("User")
    IPA_USER = os.environ["IPA_USER"]
    IPA_PASSWORD = os.environ["IPA_PASSWORD"]
else:
    IPA_USER = None
    IPA_PASSWORD = None

IPA_SERVER = os.environ["IPA_SERVER"]
IPA_DOMAIN = os.environ["IPA_DOMAIN"]
TTL = 5


def _call_freeipa(json_operation):
    headers = {'content-type': 'application/json',
               'referer': 'https://%s/ipa' % IPA_SERVER}
    if IPA_USER:
        result = requests.post("https://%s:%s@%s/ipa/session/json" % (IPA_USER, IPA_PASSWORD, IPA_SERVER),
                               data=json_operation,
                               headers=headers,
                               verify='/etc/ipa/ipa.crt')
    else:
        kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED,
                                         sanitize_mutual_error_response=False)
        result = requests.post("https://%s/ipa/session/json" % IPA_SERVER,
                               data=json_operation,
                               headers=headers,
                               auth=kerberos_auth,
                               verify='/etc/ipa/ca.crt')

    retval = result.json()

    if retval['error']:
        return retval
    else:
        return None


# Create DNS-record
def create_txt_record(args):
    entry, token = args[0], args[2]
    if entry.endswith(IPA_DOMAIN):
        entry = entry[:-(len(IPA_DOMAIN)+1)]
    add_dns_entry = """{ "id": 0,
                         "method": "dnsrecord_add/1",
                         "params": [ [ "%s", { "__dns_name__": "_acme-challenge.%s" } ],
                                     { "txtrecord": [ "%s" ],
                                       "dnsttl": %s,
                                       "version": "2.229" } ] }""" % (IPA_DOMAIN, entry, token, TTL)
    ret = _call_freeipa(add_dns_entry)
    if ret:
        logger.error(ret['error']['message'])
    sleep(25)


def delete_txt_record(args):
    entry, token = args[0], args[2]
    if entry.endswith(IPA_DOMAIN):
        entry = entry[:-(len(IPA_DOMAIN)+1)]

    remove_dns_entry = """{ "id": 0,
                            "method": "dnsrecord_del/1",
                            "params": [ [ "%s", { "__dns_name__": "_acme-challenge.%s" } ],
                                        { "txtrecord": [ "%s" ],
                                          "version": "2.229" } ] }""" % (IPA_DOMAIN, entry, token)
    ret = _call_freeipa(remove_dns_entry)
    if ret:
        logger.error(ret['error']['message'])


def deploy_cert(args):
    pass


def main(argv):
    hook_name, args = argv[0], argv[1:]
    ops = {'deploy_challenge': create_txt_record,
           'clean_challenge': delete_txt_record,
           'deploy_cert': deploy_cert, }

    if hook_name in ops.keys():
        logger.info(' + freeipa hook executing: %s', hook_name)
        ops[hook_name](args)
    else:
        logger.debug(' + freeipa hook not executing: %s', hook_name)


if __name__ == '__main__':
    main(sys.argv[1:])
