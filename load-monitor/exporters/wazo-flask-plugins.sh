#!/bin/bash

apt-get install -y wazo-plugind-cli
wazo-plugind-cli -c "install git https://github.com/wazo-platform/wazo-prometheus-exporter-plugin"
