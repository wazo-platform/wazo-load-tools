#!/bin/bash

sudo apt-get install -y  \
	pulseaudio pulseaudio-utils \
	libasound2 libalsaplayer0 \
	apulse alsa-utils alsa-tools \
	alsa-oss libasound2-plugins

cat >>/etc/systemd/system/pulseaudio.service<<EOF
[Unit]
Description=PulseAudio Setup
After=network.target

[Service]
ExecStartPre=/bin/bash -c "if [ -e /tmp/pulseaudio.socket ]; then rm -f /tmp/pulseaudio.socket; fi"
ExecStart=/bin/bash -c "sudo pulseaudio --system --realtime --disallow-exit --disallow-module-loading=0 --disable-shm=0 --log-level=debug &"
ExecStartPost=/bin/bash -c "while [ ! -e /tmp/pulseaudio.socket ]; do sleep 1; pactl load-module module-native-protocol-unix socket=/tmp/pulseaudio.socket; done"
ExecStop=/bin/bash -c "sudo pkill pulseaudio && sleep 2 && sudo rm -f /tmp/pulseaudio.socket"
Type=oneshot
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

usermod -aG pulse-access root

systemctl enable pulseaudio.service
systemctl start pulseaudio.service