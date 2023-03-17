#!/bin/bash -x

docker run -d --rm --name=ddns-master --net=host -v /opt/bind9/configuration/bind:/etc/bind ddns-master
