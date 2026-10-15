#!/usr/bin/env python3
# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
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
    },
}
_LINES_PAGE_SIZE = 500


def parse_cli_args(argv):
    parser = argparse.ArgumentParser(
        description=(
            'Create an agent for each user created from a CSV import, numbered'
            ' after the user extension and linked to the user, as member of the'
            ' callees queue'
        )
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
    parser.add_argument(
        '-n',
        '--number',
        type=int,
        help='Only create agents for the first <number> users of the file (default: all)',
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
    if parsed_args.number is not None:
        result['number'] = parsed_args.number

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


def list_lines(confd_client):
    offset = 0
    while True:
        lines = confd_client.lines.list(limit=_LINES_PAGE_SIZE, offset=offset)['items']
        yield from lines
        if len(lines) < _LINES_PAGE_SIZE:
            return
        offset += _LINES_PAGE_SIZE


def main():
    config = load_config(sys.argv[1:])
    auth_client = AuthClient(**config['auth'])
    confd_client = ConfdClient(**config['confd'])
    token = auth_client.token.new(expiration=3600)['token']
    confd_client.set_token(token)
    confd_client.tenant_uuid = config['tenant_uuid']

    with open(config['created_users_file']) as f:
        users = json.load(f)['created']
    if 'number' in config:
        users = users[: config['number']]

    extens = {
        line_user['uuid']: line['extensions'][0]['exten']
        for line in list_lines(confd_client)
        for line_user in line['users']
    }
    queue_id = config['queue_id']
    for user in users:
        exten = extens[user['user_uuid']]
        agent = confd_client.agents.create({'number': exten})
        confd_client.users(user['user_uuid']).add_agent(agent)
        confd_client.queues(queue_id).add_agent_member(agent)


if __name__ == '__main__':
    main()
