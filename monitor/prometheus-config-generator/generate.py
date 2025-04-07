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
        help='Wazo host serveur',
        required=True,
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Output file to write. Default: stdout',
    )
    parsed_args = parser.parse_args(argv)

    result = {
        'wazo_host': parsed_args.wazo_host,
        'output': parsed_args.output or None,
    }

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
        servers=[{'host': config['wazo_host']}],
    )
    with _open_output_file(config['output']) as output_file:
        output_file.write(result)


if __name__ == '__main__':
    main()
