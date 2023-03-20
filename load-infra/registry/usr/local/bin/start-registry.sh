#!/bin/bash
docker run -d -p 5000:5000 --restart=always -v /opt/registry/images:/var/lib/registry --name registry registry:2
