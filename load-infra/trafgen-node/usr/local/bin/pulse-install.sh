#!/bin/bash

sudo apt-get install -y  \
	pulseaudio pulseaudio-utils \
	libasound2 libalsaplayer0 \
	apulse alsa-utils alsa-tools \
	alsa-oss libasound2-plugins


usermod -aG pulse-access root

systemctl enable pulseaudio.service
systemctl start pulseaudio.service

PULSE_CLIENT_CONFIG=/opt/pulseaudio.client.conf
cat >>$PULSE_CLIENT_CONFIG<<EOF
default-server = unix:/tmp/pulseaudio.socket
# Prevent a server running in the container
autospawn = no
daemon-binary = /bin/true
# Prevent the use of shared memory
enable-shm = false

EOF

chmod +x $PULSE_CLIENT_CONFIG
chown pulse:pulse $PULSE_CLIENT_CONFIG
