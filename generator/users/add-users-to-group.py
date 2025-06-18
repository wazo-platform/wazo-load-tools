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
    'auth': {
        'host': 'localhost',
        'verify_certificate': False,
        'username': 'root',
        'password': 'secret',
    },
    'confd': {
        'host': 'localhost',
        'verify_certificate': False,
        'timeout': 20,  # Adding thousands users to a group can takes > 10s
    },
}


def parse_cli_args(argv):
    parser = argparse.ArgumentParser(
        description='Assign users created from a CSV import to a group'
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
        users = json.load(f)['created']

    members = [
        {'uuid': user['user_uuid'], 'priority': i} for i, user in enumerate(users)
    ]
    group_uuid = config['group_uuid']
    confd_client.groups(group_uuid).update_user_members(members)


if __name__ == '__main__':
    main()
