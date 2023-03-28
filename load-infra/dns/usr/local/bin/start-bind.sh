#!/bin/bash -x
docker stop ddns-master
docker rm ddns-master

docker run -d --rm --name=ddns-master \
    --net=host \
    -v /opt/bind9/configuration/zones:/etc/bind/zones \
    --mount type=bind,source=/opt/bind9/configuration/named.conf,target=/etc/bind/named.conf \
    --mount type=bind,source=/opt/bind9/configuration/named.conf.default-zones,target=/etc/bind/named.conf.default-zones \
    --mount type=bind,source=/opt/bind9/configuration/named.conf.local,target=/etc/bind/named.conf.local \
    --mount type=bind,source=/opt/bind9/configuration/named.conf.options,target=/etc/bind/named.conf.options \
    ddns-master
