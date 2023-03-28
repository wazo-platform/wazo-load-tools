#!/bin/bash

chown -R bind /etc/bind && /usr/sbin/named -d 1 -g -c /etc/bind/named.conf -u bind
