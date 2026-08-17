#!/usr/bin/env python3
# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import concurrent.futures
import contextlib
import csv
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
    'client_id': 'load-tester-mobile',
    'workers': 10,
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

# Forces the push path without webrtc=yes, which Asterisk cannot be stopped
# from pairing with DTLS/AVPF/ICE, leaving an endpoint sipp cannot answer.
# The dialplan file must be installed in /etc/asterisk/extensions_extra.d/.
_PREPROCESS_SUBROUTINE = 'wazo-loadtest-mobile'

# No OPTIONS pinging in the middle of sipp scenarios
_AOR_SECTION_OPTIONS = [
    ['qualify_frequency', '0'],
]


def provision_user(auth_client, confd_client, user, client_id):
    sip_username = user['sip_username']

    token_data = auth_client.token.new(
        'wazo_user',
        expiration=3600,
        session_type='mobile',
        access_type='offline',
        client_id=client_id,
        username=user['username'],
        password=user['password'],
    )
    user_uuid = token_data['metadata']['uuid']

    _set_preprocess_subroutine(confd_client, user_uuid)

    # The fake FCM token is the SIP username so the push proxy knows which sipp
    # user to register without any lookup. PUT is update-or-create in wazo-auth.
    auth_client.external.update('mobile', user_uuid, {'token': sip_username})

    return {'user_uuid': user_uuid, 'sip_username': sip_username}


def _set_preprocess_subroutine(confd_client, user_uuid):
    # Minimal body: a GET-then-PUT of the full body is rejected when it holds
    # both deprecated and current fields (e.g. call_record_enabled)
    confd_client.users.update(
        {'uuid': user_uuid, 'preprocess_subroutine': _PREPROCESS_SUBROUTINE}
    )


def disable_template_qualify(confd_client, template_uuid):
    # All generated users share the tenant's global SIP template. Re-run this
    # script if confd regenerates the tenant templates, which resets options.
    template = confd_client.endpoints_sip_templates.get(template_uuid)
    if _merge_options(template['aor_section_options'], _AOR_SECTION_OPTIONS):
        confd_client.endpoints_sip_templates.update(template)


def _merge_options(existing_options, wanted_options):
    existing_keys = {key for key, _ in existing_options}
    missing = [option for option in wanted_options if option[0] not in existing_keys]
    existing_options.extend(missing)
    return bool(missing)


def parse_cli_args(argv):
    parser = argparse.ArgumentParser(
        description=(
            'Provision users for the mobile push workflow: per user, set the '
            'wazo-loadtest-mobile preprocess subroutine (forces the push '
            'path), create a mobile refresh token and register a fake FCM '
            'token (= SIP username)'
        )
    )
    parser.add_argument(
        '-u',
        '--users-file',
        required=True,
        help='Generated users CSV file (from generate-users.py)',
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
        '-w',
        '--workers',
        type=int,
        help='Number of users provisioned in parallel',
    )
    parsed_args = parser.parse_args(argv)

    result = {}
    if parsed_args.host:
        result['host'] = parsed_args.host
    if parsed_args.password:
        result['password'] = parsed_args.password
    if parsed_args.users_file:
        result['users_file'] = parsed_args.users_file
    if parsed_args.output:
        result['output'] = parsed_args.output
    if parsed_args.extra_config:
        result['extra_config'] = parsed_args.extra_config
    if parsed_args.workers:
        result['workers'] = parsed_args.workers

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
    auth_client.set_token(token)
    confd_client.set_token(token)
    confd_client.tenant_uuid = config['tenant_uuid']

    disable_template_qualify(confd_client, config['global_sip_template_uuid'])
    logger.info(
        'Qualify disabled on SIP template %s', config['global_sip_template_uuid']
    )

    with open(config['users_file']) as f:
        users = list(csv.DictReader(f))

    provisioned = []
    failed = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=config['workers']
    ) as executor:
        futures = {
            executor.submit(
                provision_user, auth_client, confd_client, user, config['client_id']
            ): user
            for user in users
        }
        for future in concurrent.futures.as_completed(futures):
            user = futures[future]
            try:
                result = future.result()
            except Exception:
                logger.exception('Failed to provision %s', user['sip_username'])
                failed.append(user['sip_username'])
                continue
            logger.info('Provisioned mobile for %s', result['sip_username'])
            provisioned.append(result)

    provisioned.sort(key=lambda result: result['sip_username'])
    with _open_output_file(config['output']) as output_file:
        output_file.write(json.dumps({'provisioned': provisioned}, indent=2))

    if failed:
        logger.error('%d/%d users failed: %s', len(failed), len(users), failed)
        sys.exit(1)


if __name__ == '__main__':
    main()
