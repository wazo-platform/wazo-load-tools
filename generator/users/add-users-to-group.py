#!/usr/bin/env python3
# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import json
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
    'output': None,  # (default: stdout)
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
        description='Create wazo users via REST API based on an input file (CSV or JSON)'
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
        '-o',
        '--output',
        help='Output file to write. Default: stdout',
    )
    parser.add_argument(
        '-c',
        '--extra-config',
        help='Custom configuration file (ex: for clients connection)',
    )
    parser.add_argument(
        '-u',
        '--created-users-file',
        help='File with all generated users',
    )
    parsed_args = parser.parse_args(argv)

    result = {}
    if parsed_args.host:
        result['host'] = parsed_args.host
    if parsed_args.password:
        result['password'] = parsed_args.password
    if parsed_args.output:
        result['output'] = parsed_args.output
    if parsed_args.extra_config:
        result['extra_config'] = parsed_args.extra_config
    if parsed_args.created_users_file:
        result['created_users_file'] = parsed_args.created_users_file

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
    token = auth_client.token.new(expiration=3600)['token']
    confd_client.set_token(token)
    confd_client.tenant_uuid = config['tenant_uuid']

    with open(config['created_users_file']) as f:
        created_users = json.load(f)

    members = {
        'users': {'uuid': user['user_uuid'] for user in created_users['created']}
    }
    body = {
        'label': 'callees',
        'max_calls': 100,
        'ring_in_use': False,
        'ring_strategy': 'memorized_round_robin',
        'members': members,
    }
    group = confd_client.groups.create(body)

    with open(config['output'], 'w') as f:
        json.dump(f, group)


if __name__ == '__main__':
    main()
