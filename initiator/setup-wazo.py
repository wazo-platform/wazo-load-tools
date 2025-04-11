#!/usr/bin/env python3
# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import contextlib
import logging
import random
import string
import sys
import time

import requests
import yaml
from wazo_auth_client import Client as AuthClient
from wazo_confd_client import Client as ConfdClient
from wazo_setupd_client import Client as SetupdClient

logger = logging.getLogger('stevedore')
logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

HOUR = 60 * 60
_DEFAULT_CONFIG = {
    'output': None,  # (default: stdout)
    'setupd': {
        'host': 'localhost',
        'verify_certificate': False,
    },
    'auth': {
        'host': 'localhost',
        'verify_certificate': False,
        'username': 'root',
        'password': None,
    },
    'confd': {
        'host': 'localhost',
        'verify_certificate': False,
    },
}


def parse_cli_args(argv):
    parser = argparse.ArgumentParser(description='Setup a wazo server')
    parser.add_argument(
        '-s',
        '--host',
        help='Host to reach Wazo server',
    )
    parser.add_argument(
        '-t',
        '--tenant',
        help='Host to reach Wazo server',
    )
    parser.add_argument(
        '-p',
        '--password',
        help='Password to initiate wazo',
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Output file to write config used to generate users. Default: stdout',
    )
    parsed_args = parser.parse_args(argv)

    result = {}
    if parsed_args.host:
        result['host'] = parsed_args.host
    if parsed_args.tenant:
        result['tenant_uuid'] = parsed_args.tenant
    if parsed_args.password:
        result['setup_password'] = parsed_args.password
    if parsed_args.output:
        result['output'] = parsed_args.output

    return result


def load_config(args):
    cli_config = parse_cli_args(args)
    config = _DEFAULT_CONFIG | cli_config
    if config.get('host'):
        config['auth']['host'] = config['host']
        config['confd']['host'] = config['host']
        config['setupd']['host'] = config['host']
    if config.get('setup_password') and not config['auth']['password']:
        config['auth']['password'] = config['setup_password']
    elif config['auth']['password']:
        config['setup_password'] = config['auth']['password']
    else:
        raise Exception('Missing password')
    return config


@contextlib.contextmanager
def _open_output_file(output):
    if not output:
        yield sys.stdout
    else:
        with open(output, 'w') as f:
            yield f


def _random_name(n):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(n)
    )


def main():
    config = load_config(sys.argv[1:])
    auth_client = AuthClient(**config['auth'])
    confd_client = ConfdClient(**config['confd'])
    setupd_client = SetupdClient(**config['setupd'])

    body = {
        'engine_language': 'en_US',
        'engine_license': True,
        'engine_password': config['setup_password'],
    }
    setupd_client.setup.create(body)

    token = auth_client.token.new(expiration=12 * HOUR)['token']
    auth_client.set_token(token)

    tenant = auth_client.tenants.new(name=f'load-{_random_name(6)}')

    confd_client.set_token(token)
    confd_client.tenant_uuid = tenant['uuid']

    for _ in range(5):
        # Wait wazo-confd async tenant creation
        try:
            confd_tenant = confd_client.tenants.get(tenant['uuid'])
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                time.sleep(2)
                continue
            raise
        break

    webrtc_sip_template_uuid = confd_tenant['webrtc_sip_template_uuid']
    global_sip_template_uuid = confd_tenant['global_sip_template_uuid']

    body = {
        'label': 'internal',
        'type': 'internal',
        'user_ranges': [{'start': '10000', 'end': '99999'}],
    }
    internal_context = confd_client.contexts.create(body)

    incall_prefix = '123'
    body = {
        'label': 'incoming',
        'type': 'incall',
        'user_ranges': [
            {
                'start': f'{incall_prefix}10000',
                'end': f'{incall_prefix}99999',
            }
        ],
    }
    incall_context = confd_client.contexts.create(body)

    body = {
        'label': 'loadtester',
        'name': 'loadtester',
        "templates": [{"uuid": global_sip_template_uuid}],
        'auth_section_options': [
            ["username", "loadtester"],
            ["password", "loadtester"],
        ],
        "outbound_auth_section_options": [
            ["username", "loadtester"],
            ["password", "loadtester"],
        ],
    }
    trunk_endpoint_sip = confd_client.endpoints_sip.create(
        body, tenant_uuid=tenant['uuid']
    )

    body = {
        'name': 'loadtester',
        'context': incall_context['name'],
        'outgoing_caller_id_format': '+E164',
    }
    load_tester_trunk = confd_client.trunks.create(body, tenant_uuid=tenant['uuid'])

    confd_client.trunks(load_tester_trunk).add_endpoint_sip(trunk_endpoint_sip)

    user_generator_config = {
        'tenant_uuid': tenant['uuid'],
        'webrtc_sip_template_uuid': webrtc_sip_template_uuid,  # only to support format: json
        'internal_context': internal_context['name'],
        'incall_context': incall_context['name'],
        'incall_prefix': incall_prefix,
    }

    with _open_output_file(config['output']) as output_file:
        yaml.dump(user_generator_config, output_file)


if __name__ == '__main__':
    main()
