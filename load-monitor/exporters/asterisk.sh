#!/bin/bash

cat <<EOF >/etc/asterisk/prometheus.conf 
[general]
enabled = yes
core_metrics_enabled = yes
uri = metrics
EOF


cat <<EOF >/etc/asterisk/http.d/20-wazo.conf
[general]
enabled=yes
enablestatic=yes
bindaddr=0.0.0.0
bindport=5039
prefix=
servername=Wazo PBX
sessionlimit=1000
EOF

systemctl restart asterisk.service
