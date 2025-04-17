#!/usr/bin/env python3
# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import contextlib
import csv
import json
import logging
import sys

import yaml

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

_DEFAULT_CONFIG = {
    'output': None,  # (default: stdout)
    'extra_config': 'config.yml',
    'users_range_start': 10000,
    'internal_context': 'internal',
    'incall_context': 'from-externe',
    'incall_prefix': '1234',
    'global_sip_template_uuid': None,
    'email': 'dev@wazo.io',
}


def generate_user(config, index):
    context = config['internal_context']
    incall_context = config['incall_context']
    incall_prefix = config['incall_prefix']
    global_sip_template_uuid = config['global_sip_template_uuid']
    email_user, email_domain = config['email'].split('@', 1)
    exten = f'{config["users_range_start"] + index}'
    email = f'{email_user}+user{index}@{email_domain}'
    return {
        'firstname': 'User',
        'lastname': f'{index}',
        'caller_id': f'"User {index}"',
        'subscription_type': 1,
        'email': email,
        'auth': {
            'username': email,
            'password': 'secret',
        },
        'incalls': [
            {
                'extensions': [
                    {
                        'exten': f'{incall_prefix}{exten}',
                        'context': incall_context,
                    }
                ]
            }
        ],
        'lines': [
            {
                'context': context,
                'endpoint_sip': {
                    'label': exten,
                    'name': exten,
                    'templates': [{'uuid': global_sip_template_uuid}],
                    'auth_section_options': [
                        ['username', exten],
                        ['password', exten],
                    ],
                },
                'extensions': [{'exten': exten}],
            }
        ],
        'voicemail': {
            'number': exten,
            'context': context,
        },
    }


def generate_users_json(config, number, output_file):
    users = {'items': []}
    for index in range(0, number):
        user = generate_user(config, index)
        users['items'].append(user)

    json.dump(users, output_file)


def generate_users_csv(config, number, output_file):
    fieldnames = [
        'firstname',
        'lastname',
        'email',
        'username',
        'password',
        'subscription_type',
        'exten',
        'context',
        'line_protocol',
        'sip_username',
        'sip_password',
        'incall_exten',
        'incall_context',
        'voicemail_name',
        'voicemail_number',
        'voicemail_context',
    ]
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    for index in range(0, number):
        user = generate_user(config, index)
        sip_auth_options = user['lines'][0]['endpoint_sip']['auth_section_options']
        row = {
            'firstname': user['firstname'],
            'lastname': user['lastname'],
            'email': user['email'],
            'username': user['auth']['username'],
            'password': user['auth']['password'],
            'subscription_type': user['subscription_type'],
            'exten': user['lines'][0]['extensions'][0]['exten'],
            'context': user['lines'][0]['context'],
            'line_protocol': 'sip',  # Association to webrtc_sip_template is done internally
            'sip_username': sip_auth_options[0][1],
            'sip_password': sip_auth_options[1][1],
            'incall_exten': user['incalls'][0]['extensions'][0]['exten'],
            'incall_context': user['incalls'][0]['extensions'][0]['context'],
            'voicemail_name': user['voicemail']['number'],
            'voicemail_number': user['voicemail']['number'],
            'voicemail_context': user['voicemail']['context'],
        }
        writer.writerow(row)


def parse_cli_args(argv):
    parser = argparse.ArgumentParser(
        description='Generate wazo users file (CSV or JSON) to be used as input for REST API'
    )
    parser.add_argument(
        '-f',
        '--format',
        default='csv',
        choices=['json', 'csv'],
        help='Format to generate CSV',
    )
    parser.add_argument(
        '-n',
        '--number',
        type=int,
        default=10,
        help='The number of user to generate',
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Output file to write. Default: stdout',
    )
    parser.add_argument(
        '-c',
        '--extra-config',
        help='Configuration file with context to generate users',
    )
    parsed_args = parser.parse_args(argv)

    result = {}
    if parsed_args.format:
        result['format'] = parsed_args.format
    if parsed_args.number:
        result['number'] = parsed_args.number
    if parsed_args.output:
        result['output'] = parsed_args.output
    if parsed_args.extra_config:
        result['extra_config'] = parsed_args.extra_config

    return result


def load_config(args):
    cli_config = parse_cli_args(args)
    config = _DEFAULT_CONFIG | cli_config
    if extra_config_file := config['extra_config']:
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
    with _open_output_file(config['output']) as output_file:
        if config['format'] == 'json':
            generate_users_json(config, config['number'], output_file)
        elif config['format'] == 'csv':
            generate_users_csv(config, config['number'], output_file)
        else:
            raise NotImplementedError()


if __name__ == '__main__':
    main()
