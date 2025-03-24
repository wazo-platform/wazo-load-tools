#!/usr/bin/env python3
# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import contextlib
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


def create_users_csv(confd_client, users_file, output_file):
    with open(users_file) as f:
        content = f.read()

    result = confd_client.users.import_csv(content, encoding='utf-8', timeout=1800)
    output_file.write(json.dumps(result, indent=2))


def create_users_json(confd_client, users_file):
    raise NotImplementedError()


def parse_cli_args(argv):
    parser = argparse.ArgumentParser(
        description='Create wazo users via REST API based on an input file (CSV or JSON)'
    )
    parser.add_argument(
        '-u',
        '--users-file',
        required=True,
        help='File with all generated users',
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
        '-f',
        '--format',
        default='csv',
        choices=['json', 'csv'],
        help='Input file format',
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
    parsed_args = parser.parse_args(argv)

    result = {}
    if parsed_args.host:
        result['host'] = parsed_args.host
    if parsed_args.password:
        result['password'] = parsed_args.password
    if parsed_args.format:
        result['format'] = parsed_args.format
    if parsed_args.users_file:
        result['users_file'] = parsed_args.users_file
    if parsed_args.output:
        result['output'] = parsed_args.output
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


@contextlib.contextmanager
def _open_output_file(output):
    if not output:
        yield sys.stdout
    else:
        with open(output, 'w') as f:
            yield f


def main():
    config = load_config(sys.argv[1:])
    auth_client = AuthClient(**config['auth'])
    confd_client = ConfdClient(**config['confd'])
    token = auth_client.token.new(expiration=3600)['token']
    confd_client.set_token(token)
    confd_client.tenant_uuid = config['tenant_uuid']
    with _open_output_file(config['output']) as output_file:
        if config['format'] == 'json':
            create_users_json(confd_client, config['users_file'], output_file)
        elif config['format'] == 'csv':
            create_users_csv(confd_client, config['users_file'], output_file)
        else:
            raise NotImplementedError()


if __name__ == '__main__':
    main()
