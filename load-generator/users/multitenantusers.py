#!/usr/bin/env python3
# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import argparse
import time

from uuid import uuid4

from wazo_auth_client import Client as AuthClient
from wazo_confd_client import Client as ConfdClient


NB_TENANTS=2000
NB_USERS_PER_TENANT=1
EXPIRATION=3600*12
EXTENSION_START=1000
INCALL_PREFIX='111111'

def count_digits(n):
    if n == 0:
        return 1
    count = 0
    while n != 0:
        count += 1
        n = n // 10
    return count
    

tenant_suffix_len = count_digits(NB_TENANTS)
user_suffix_lemn = count_digits(NB_USERS_PER_TENANT)

def create_tenant(auth_client, n):
    suffix = '{}-{}'.format(
        str(n).zfill(tenant_suffix_len),
        uuid4(),
    )
    tenant = auth_client.tenants.new(
        name=f'tenant-{suffix}',
    )
    return tenant


def create_user(confd_client, n, incall_context_name, context_name, sip_template_uuid, tenant_uuid, tenant_slug):
    print('slug', tenant_slug)
    with open('user.json.tpl', 'r') as f:
        raw_payload = f.read()
    raw_payload = raw_payload.replace('__SEQUENCE__', str(n))
    raw_payload = raw_payload.replace('__TENANT_SLUG__', tenant_slug)
    raw_payload = raw_payload.replace('__EXTENSION__', str(EXTENSION_START + n))
    raw_payload = raw_payload.replace('__INCALL_PREFIX__', INCALL_PREFIX)
    raw_payload = raw_payload.replace('__INCALL_CONTEXT__', incall_context_name)
    raw_payload = raw_payload.replace('__WEBRTC_UUID__', sip_template_uuid)
    raw_payload = raw_payload.replace('__CONTEXT__', context_name)

    payload = json.loads(raw_payload)

    user = confd_client.users.create(payload, tenant_uuid=tenant_uuid)
    print('Created user', user)


def wait_for_template(confd_client, tenant_uuid):
    for _ in range(20):
        response = confd_client.endpoints_sip_templates.list(
            search='global',
            tenant_uuid=tenant_uuid,
        )
        for template in response['items']:
            return template['uuid']
        time.sleep(0.5)


    

def create_tenants(auth_client, confd_client):
    for n in range(NB_TENANTS):
        tenant = create_tenant(auth_client, n)
        slug = tenant['slug']
        incall_context = confd_client.contexts.create(
            {
                'enabled': True,
                'label': 'Incall',
                'type': 'incall',
                'incall_ranges': [
                    {
                        'start': INCALL_PREFIX+'0000',
                        'end': INCALL_PREFIX+'9999',
                    },
                ],
            },
            tenant_uuid=tenant['uuid'],
        )
        internal_context = confd_client.contexts.create(
            {
                'enabled': True,
                'label': 'Internal',
                'type': 'internal',
                'user_ranges': [
                    {
                        'start': '0000',
                        'end': '9999',
                    },
                ],
            },
            tenant_uuid=tenant['uuid'],
        )
        outcall_contert = confd_client.contexts.create(
            {
                'enabled': True,
                'label': 'Outcall',
                'type': 'outcall',
            },
            tenant_uuid=tenant['uuid']
        )
        sip_template_uuid = wait_for_template(
            confd_client,
            tenant['uuid'],
        )
        if not sip_template_uuid:
            raise Exception('Failed to get the sip template')
        for i in range(NB_USERS_PER_TENANT):
            create_user(
                confd_client,
                i,
                incall_context['name'],
                internal_context['name'],
                sip_template_uuid,
                tenant['uuid'],
                slug,
            )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('--hostname')
    return parser.parse_args()


def main():
    args = parse_args()
    auth_client = AuthClient(
        args.hostname,
        username=args.username,
        password=args.password,
        https=True,
        verify_certificate=False,
    )
    token = auth_client.token.new('wazo_user', expiration=EXPIRATION)['token']
    auth_client.set_token(token)
    confd_client = ConfdClient(
        args.hostname,
        token=token,
        https=True,
        verify_certificate=False,
    )
    create_tenants(auth_client, confd_client)


if __name__ == '__main__':
    main()
