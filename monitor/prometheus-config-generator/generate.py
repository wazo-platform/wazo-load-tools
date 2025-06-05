#!/usr/bin/env python3
# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import contextlib
import os
import sys

from jinja2 import Environment, FileSystemLoader


def parse_cli_args(argv):
    parser = argparse.ArgumentParser(
        description='Generate prometheus configuration file'
    )
    parser.add_argument(
        '-s',
        '--wazo-host',
        help='Wazo host serveur. Use commas to separate multiple values.',
        required=True,
    )
    parser.add_argument(
        '-e',
        '--edge-host',
        help='Edge host serveur. Use commas to separate multiple values.',
    )
    parser.add_argument(
        '-t',
        '--load-testing',
        help='Generate entry for load testing metrics.',
        action='store_true',
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Output file to write. Default: stdout',
    )
    parsed_args = parser.parse_args(argv)

    wazo_hosts = parsed_args.wazo_host.split(',')
    result = {
        'wazo_hosts': wazo_hosts,
        'edge_hosts': [],
        'load_testing': parsed_args.load_testing or False,
        'output': parsed_args.output or None,
    }
    if parsed_args.edge_host:
        result['edge_hosts'] = parsed_args.edge_host.split(',')

    return result


def load_config(args):
    return parse_cli_args(args)


@contextlib.contextmanager
def _open_output_file(output):
    if not output:
        yield sys.stdout
    else:
        with open(output, 'w') as f:
            yield f


def main():
    config = load_config(sys.argv[1:])

    environment = Environment(loader=FileSystemLoader([os.path.dirname(__file__)]))
    template = environment.get_template('prometheus.yaml.jinja2')
    result = template.render(
        wazo_servers=[{'host': host} for host in config['wazo_hosts']],
        edge_servers=[{'host': host} for host in config['edge_hosts']],
        load_testing=config['load_testing'],
    )
    with _open_output_file(config['output']) as output_file:
        output_file.write(result)


if __name__ == '__main__':
    main()
