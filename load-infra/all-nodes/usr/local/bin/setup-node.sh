#!/bin/bash

apt-get update
apt-get upgrade -y
mkdir -p src bin /etc/apt/keyrings

apt-get update
apt-get install -y \
	tmux \
	ca-certificates \
	curl \
	gnupg \
	lsb-release \
	curl \
	wget \
	git \
	jq \
	vim \
	python3-pip




install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo   "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" |   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
sudo apt-get install -y  docker-ce \
	docker-ce-cli \
	containerd.io \
	docker-buildx-plugin \
	docker-compose-plugin

ln -s /usr/libexec/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose

