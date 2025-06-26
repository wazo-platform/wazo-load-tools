#!/usr/bin/env python3
# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging
import sys

import yaml
from wazo_auth_client import Client as AuthClient
from wazo_confd_client import Client as ConfdClient

logger = logging.getLogger('stevedore')
logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

_DEFAULT_CONFIG = {
    'auth': {
        'host': 'localhost',
        'verify_certificate': False,
        'username': 'root',
        'password': 'secret',
    },
    'confd': {
        'host': 'localhost',
        'verify_certificate': False,
    },
}


def parse_cli_args(argv):
    parser = argparse.ArgumentParser(
        description='Setup wazo specific configuration on no SIP proxy environment'
    )
    parser.add_argument(
        '-s',
        '--host',
        help='Host to reach Wazo server',
    )
    parser.add_argument(
        '-p',
        '--password',
        help='Password to connect on wazo (e.g. root password)',
    )
    parser.add_argument(
        '-c',
        '--extra-config',
        help='Custom configuration file (ex: for clients connection)',
    )
    parsed_args = parser.parse_args(argv)

    result = {}
    if parsed_args.host:
        result['host'] = parsed_args.host
    if parsed_args.password:
        result['password'] = parsed_args.password
    if parsed_args.extra_config:
        result['extra_config'] = parsed_args.extra_config

    return result


def load_config(args):
    cli_config = parse_cli_args(args)
    config = _DEFAULT_CONFIG | cli_config
    if config.get('host'):
        config['auth']['host'] = config['host']
        config['confd']['host'] = config['host']
    if config.get('password'):
        config['auth']['password'] = config['password']
    if extra_config_file := config.get('extra_config'):
        with open(extra_config_file) as f:
            extra_config = yaml.load(f, Loader=yaml.SafeLoader)
            return _DEFAULT_CONFIG | extra_config | cli_config
    return _DEFAULT_CONFIG | cli_config


def main():
    config = load_config(sys.argv[1:])
    auth_client = AuthClient(**config['auth'])
    confd_client = ConfdClient(**config['confd'])
    token = auth_client.token.new(expiration=360)['token']
    confd_client.set_token(token)
    confd_client.tenant_uuid = config['tenant_uuid']

    confd_tenant = confd_client.tenants.get(config['tenant_uuid'])
    global_sip_tpl_uuid = confd_tenant['global_sip_template_uuid']
    global_sip_tpl = confd_client.endpoints_sip_templates.get(global_sip_tpl_uuid)
    global_sip_tpl['endpoint_section_options'].append(['rewrite_contact', 'yes'])
    confd_client.endpoints_sip_templates.update(global_sip_tpl)


if __name__ == '__main__':
    main()
