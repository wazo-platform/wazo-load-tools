#!/bin/bash

apt install -y build-essential ruby-dev
ruby --version
gem install fluentd --no-doc
gem install fluent-plugin-prometheus
fluentd --version

mkdir /etc/fluentd

cp fluentd.conf /etc/fluentd/fluentd.conf


cat <<EOF >/etc/systemd/system/fluentd.service
[Unit]
Description=Fluentd
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=0

[Service]
User=root
Group=root
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=fluentd --config /etc/fluentd/fluentd.conf

[Install]
WantedBy=multi-user.target
EOF

systemctl enable fluentd
systemctl start fluentd
systemctl status fluentd

curl http://localhost:24231/metrics
