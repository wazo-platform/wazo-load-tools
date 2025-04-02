#!/usr/bin/env python3
# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging
import sys

from wazo_auth_client import Client as AuthClient
from wazo_plugind_client import Client as PlugindClient

MINUTE = 60


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
        'password': None,
    },
    'plugind': {
        'host': 'localhost',
        'verify_certificate': False,
    },
    'exporter_plugin': {
        'url': 'https://github.com/wazo-platform/wazo-prometheus-exporter-plugin',
        'branch': 'master',
    }
}

def parse_cli_args(argv):
    parser = argparse.ArgumentParser(description='Setup a wazo server')
    parser.add_argument(
        '-s',
        '--host',
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
    parser.add_argument(
        '-b',
        '--branch',
        help='Git branch to use for the plugin installation'
    )
    parsed_args = parser.parse_args(argv)

    result = {}
    if parsed_args.host:
        result['host'] = parsed_args.host
    if parsed_args.password:
        result['password'] = parsed_args.password
    if parsed_args.output:
        result['output'] = parsed_args.output
    if parsed_args.branch:
        result['git_branch'] = parsed_args.branch

    return result

def load_config(args):
    cli_config = parse_cli_args(args)
    config = _DEFAULT_CONFIG | cli_config
    if config.get('host'):
        config['auth']['host'] = config['host']
        config['plugind']['host'] = config['host']
    if config.get('password') and not config['auth']['password']:
        config['auth']['password'] = config['password']
    if config.get('git_branch'):
        config['exporter_plugin']['branch'] = config['git_branch']

    if not config['auth'].get('password'):
        raise Exception('Missing password')

    return config


def main():
    config = load_config(sys.argv[1:])
    auth_client = AuthClient(**config['auth'])
    plugind_client = PlugindClient(**config['plugind'])

    token = auth_client.token.new(expiration=15 * MINUTE)['token']
    plugind_client.set_token(token)

    plugind_client.plugins.install(
        method='git',
        options={
            'url': config['exporter_plugin']['url'],
            'ref': config['exporter_plugin']['branch'],
        },
        reinstall=True,
    )


if __name__ == '__main__':
    main()
