#!/usr/bin/bash

VERSION=${1:-v1.65.15}

wget https://github.com/sipcapture/heplify/releases/download/$VERSION/heplify
systemctl daemon-reload
systemctl enable heplify-client.service
systemctl start heplify-client.service
