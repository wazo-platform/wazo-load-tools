#!/usr/bin/env python3
# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml
import click

from jinja2 import Environment, FileSystemLoader

@click.command()
@click.option(
    '--config',
    help='Configuration file for the config generator',
    default='/etc/prometheus/templates/prometheus-template-config.yml',
)
@click.option(
    '--template-dir',
    default='/etc/prometheus/templates',
    help='Directory where the templates live',
)
@click.option(
    '--template-name',
    default='prometheus.yml.jinja2',
    help='Name of the template to render',
)
@click.option(
    '--output',
    '-o',
    default='/etc/prometheus/prometheus.yml',
    help='Location of the generated file',
)
def main(config, template_dir, template_name, output):
    with open(config) as f:
        conf = yaml.safe_load(f)
    environment = Environment(
        loader=FileSystemLoader([template_dir]),
    )
    template = environment.get_template(template_name)
    with open(output, 'w') as f:
        f.write(
            template.render(
                stacks=conf['wazo-stack'],
                edges=conf['wazo-edge'],
            )
        )


if __name__ == '__main__':
    main()
