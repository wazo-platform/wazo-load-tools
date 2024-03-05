# Configuring wazo load infra nodes
## Table of Contents
- [Configuring wazo load infra nodes](#configuring-wazo-load-infra-nodes)
  - [Table of Contents](#table-of-contents)
  - [1 CA](#1-ca)
    - [1.1 Create the CA](#11-create-the-ca)
      - [1.1.1 Create both at once](#111-create-both-at-once)
      - [1.1.2 Create only ca cert](#112-create-only-ca-cert)
  - [2 docker server](#2-docker-server)
    - [2.1 Create server certs](#21-create-server-certs)
      - [2.2.1 Single server](#221-single-server)
      - [2.2.2 Several servers](#222-several-servers)
    - [2.2 Creating the docker server tarball](#22-creating-the-docker-server-tarball)
      - [2.2.1 Prereqs](#221-prereqs)
      - [2.2.2 generating the tarball](#222-generating-the-tarball)
    - [2.3 Configuring the node](#23-configuring-the-node)
      - [2.3.1 Prereqs](#231-prereqs)
      - [2.3.2 Pushing the config to the node](#232-pushing-the-config-to-the-node)
    - [2.4 Installing the node](#24-installing-the-node)
      - [2.4.1 Prereqs](#241-prereqs)
      - [2.4.2 Executing installation script](#242-executing-installation-script)
  - [3 Docker client](#3-docker-client)
    - [3.1 Client certs](#31-client-certs)
      - [3.1.1 Single client](#311-single-client)
      - [3.2.1 Several clients](#321-several-clients)

## 1 CA

A Docker server consists of a specific Docker configuration that exposes the Docker API to remote hosts. To control which service or entity can use the API remotely, a Docker server is configured with TLS authentication. To achieve this level of security, it's essential to first establish a certificate management system. This system automates and facilitates the delivery of certificates to a Docker server.

### 1.1 Create the CA
The CA is an essential component because it will be used for validating the certifcates between servers and clients.

#### 1.1.1 Create both at once
At the root of the wazo-scalability directory run the following command

```
$ make create-ca
```

```
make[1]: Entering directory '/home/user/src/wazo-scalability-clean/load-infra'
openssl genpkey -algorithm RSA -out certs/ca/ca.key
..+.+..+.........+......+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*....+..+.............+......+........+...+....+...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*....+......+......+..+...+....+...............+.....+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
..+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*.......+.............+.....+.+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*...+.+...+.....+....+..+..........+...+......+.........+......+.....+....+...+..+......+.+.....+...+.+..+.......+.....+...........................+.+..+...+....+.....................+.....+...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
openssl req -x509 -new -nodes -key certs/ca/ca.key -sha256 -days 3650 -out certs/ca/ca.crt -subj "/CN=load.wazo.io"
make[1]: Leaving directory '/home/user/src/wazo-scalability-clean/load-infra'
```

The certficates have been generated in the following folder:
```
$ ls load-infra/certs/ca/
ca.crt  ca.key
```

This needs to be done only once. You'll need to store the ca key and crt in a secure vault, in order to use it later for generating clients and servers certificates.


#### 1.1.2 Create only ca cert
You need to have a ca.key file put in the `load-infra/certs/ca/` folder.
At the root of the wazo-scalability directory run the following command
```
$ make create-ca-crt
```

```
make[1]: Entering directory '/home/user/src/wazo-scalability-clean/load-infra'
openssl req -x509 -new -nodes -key certs/ca/ca.key -sha256 -days 3650 -out certs/ca/ca.crt -subj "/CN=*.load.wazo.io"
make[1]: Leaving directory '/home/user/src/wazo-scalability-clean/load-infra'
```

## 2 docker server
### 2.1 Create server certs
#### 2.2.1 Single server
You need to have a ca.key file put in the `load-infra/certs/ca/` folder.
At the root of the wazo-scalability directory run the following command
```
$ make servers-cert SERVERS="trafgen1.load.wazo.io"
```

```
make[1]: Entering directory '/home/user/src/wazo-scalability-clean/load-infra'
openssl genpkey -algorithm RSA -out certs/servers/trafgen1.load.wazo.io.key
.....+.........+..+.......+...........+....+..+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*..+....+.....+....+..............+...+...+.........+.+...........+.+.........+...+...+..+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*..+.....+.+......+...+......+..+...+.+.....+.+..............+......+..........+.........+.....+.+........+....+......+......+...+......+..+...+.......+..+.......+...+..+....+.....................+......+..+......+.....................+.+..+.+......+...+.....+...+...+.+...........+...+.+......+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
..........+.+......+.....+....+...........+....+...+..+......+.........+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*..+......+.........+.....+.+......+..+.+..+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*...+.....+...+......+.+..................+......+.........+..+............+.+..+....+.....+....+.....+.+........+.+......+......+........+............+.......+...+..+..........+........+...+......................+..+......+.+........+...+.........+.+.........+.........+.....+.........+..........+..+.............+.....+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
openssl req -new -key certs/servers/trafgen1.load.wazo.io.key -out certs/servers/trafgen1.load.wazo.io.csr -subj "/CN=*.load.wazo.io"
openssl x509 -req -in certs/servers/trafgen1.load.wazo.io.csr -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial -out certs/servers/trafgen1.load.wazo.io.crt -days 3650 -sha256
Certificate request self-signature ok
subject=CN = *.load.wazo.io
make[1]: Leaving directory '/home/user/src/wazo-scalability-clean/load-infra'
```
The following files have been created
```
$ tree load-infra/certs/servers/
load-infra/certs/servers/
└── trafgen1.load.wazo.io
    ├── server.crt
    ├── server.csr
    └── server.key

2 directories, 3 files
```

#### 2.2.2 Several servers
You need to have a ca.key file put in the `load-infra/certs/ca/` folder.
At the root of the wazo-scalability directory run the following command
```
$ make servers-cert SERVERS="trafgen1.load.wazo.io trafgen2.load.wazo.io"
```

```
make[1]: Entering directory '/home/user/src/wazo-scalability-clean/load-infra'
openssl genpkey -algorithm RSA -out certs/servers/trafgen1.load.wazo.io.key
.+......+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*..+....+......+.........+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*..+......+...+.....+.+.....+........................+...+....+...............+.....+......+...+.........+.......+...........+....+........+.+.....+....+...+..................+.....+.........+......+.+...+......+..............+...+.......+............+.....................+..............+...+.......+......+..............+.........................+.....+.............+.....+.+......+.....+.+...+......+......+..+............+.+.....+....+...........+...+......+.+..+.+..............+......+.......+..+.+..+...+......+...+.......+......+.........+..................+.................+.+..+.+..+............+.+..+....+...........+.......+.....+............+....+......+...+..+.........+....+..................+.....+.......+..+....+..+....+...+.....+.+...........+................+..+......+................+......+.....+...+....+.....+.......+...+..+...+......+....+...+.....+..................+......+...+.+.....+......+......+.............+.....+....+..+.+..............+...+.+.....+.+........+...+....+...+..+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
...+....+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*.+..+...+.+.....+....+...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*...+.+...+......+......+........+.......+...+...........+...............+....+............+..+.+...............+...........+...+.+..+....+...+..+...+......+.......+...............+........................+......+...+.....+....+.....+.......+.....+.+..............+.+.....+....+..................+......+..............+.+......+...........+...+....+.....+.+......+......+...+............+.....+.......+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
openssl req -new -key certs/servers/trafgen1.load.wazo.io.key -out certs/servers/trafgen1.load.wazo.io.csr -subj "/CN=*.load.wazo.io"
openssl x509 -req -in certs/servers/trafgen1.load.wazo.io.csr -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial -out certs/servers/trafgen1.load.wazo.io.crt -days 3650 -sha256
Certificate request self-signature ok
subject=CN = *.load.wazo.io
make[1]: Leaving directory '/home/user/src/wazo-scalability-clean/load-infra'
make[1]: Entering directory '/home/user/src/wazo-scalability-clean/load-infra'
openssl genpkey -algorithm RSA -out certs/servers/trafgen.load.wazo.io.key
......+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*.......+..+.+......+......+..+......+.........+.......+...+........+..........+........+.........+..........+.....+..........+...+.....+...+....+...........+......+.+........+...............+.+.........+..+..........+............+......+..+...+.+..............+.+......+.................+......+.......+..+...+....+.........+..+.......+...+...+...........+....+.........+...+..+.......+.....+...................+..+...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
...+..........+..+....+...+.....+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*.......+.....+.......+.....+.+........+.+.....+.+..+...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*........+......+.+...........+...............+....+.....+.+...+.........+..+...+................+.....+....+...+..+...+...+..........+...........+...+...+............+...+....+...+......+.........+..+..........+...+.....+......+.+...+...+..+...+.......+............+........+.+.....+......+.+..+......+..........+...........+...+.+...........+...+...+....+...............+.....+.........+......+......+.......+...+.....+.............+.....+......+.+............+.....+......+.......+...............+...+..............+...+.......+..+.+..................+..+...+......+......+..................+....+...........+.+........+......+.......+........+....+...+..+..........+...........+....+..+......+.........+......+.......+......+..+.........+....+........................+........+...+.+...+......+...............+..+.............+..+....+...+...+...+.....+......+.........+......+.+.....+............+.......+.....+.+............+.....+.......+...............+...........+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
openssl req -new -key certs/servers/trafgen.load.wazo.io.key -out certs/servers/trafgen.load.wazo.io.csr -subj "/CN=*.load.wazo.io"
openssl x509 -req -in certs/servers/trafgen.load.wazo.io.csr -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial -out certs/servers/trafgen.load.wazo.io.crt -days 3650 -sha256
Certificate request self-signature ok
subject=CN = *.load.wazo.io
make[1]: Leaving directory '/home/user/src/wazo-scalability-clean/load-infra'
```

### 2.2 Creating the docker server tarball
#### 2.2.1 Prereqs
- CA cert
- server key
- server cert
If you don't meet these prereqs please reach them before starting the tarball



The following files have been created
```
$ tree load-infra/certs/servers/
load-infra/certs/servers/
├── trafgen1.load.wazo.io
│   ├── server.crt
│   ├── server.csr
│   └── server.key
└── trafgen2.load.wazo.io
    ├── server.crt
    ├── server.csr
    └── server.key

3 directories, 6 files
```
#### 2.2.2 generating the tarball
```
$ make tar-docker-server SERVER_NAME="trafgen1.load.wazo.io"
```

```
usr/
etc/
etc/systemd/
etc/systemd/system/
etc/systemd/system/docker.service.d/
etc/systemd/system/docker.service.d/override.conf
etc/docker/
etc/docker/daemon.json
etc/docker/certs/
etc/docker/certs/server.crt
etc/docker/certs/server.csr
etc/docker/certs/server.key
etc/
etc/ws-client/
etc/docker/
etc/docker/daemon.json
etc/resolv.conf
usr/
usr/local/
usr/local/bin/
usr/local/bin/stop-resolconf.sh
usr/local/bin/docker-pull.sh
usr/local/bin/docker-push.sh
usr/local/bin/get-token.sh
usr/local/bin/setup-node.sh
```

the tarball is generated there:
```
$ ls load-infra/docker-server.tar
load-infra/docker-server.tar
```
### 2.3 Configuring the node
#### 2.3.1 Prereqs
- ssh access to the node
- Your ssh key on the remote node
- root privileges to the remote node

#### 2.3.2 Pushing the config to the node
```
$ scp load-infra/docker-server.tar address_ip_to_the_node:/opt/
$ ssh  address_ip_to_the_node bash -c "tar -C / /opt/docker-server.tar"
```
### 2.4 Installing the node
#### 2.4.1 Prereqs
- ssh access to the node
- Your ssh key on the remote node
- root privileges to the remote node

#### 2.4.2 Executing installation script


## 3 Docker client
### 3.1 Client certs
#### 3.1.1 Single client
You need to have a ca.key file put in the `load-infra/certs/ca/` folder.
At the root of the wazo-scalability directory run the following command
```
$ make clients-cert CLIENTS="trafgen1.load.wazo.io"
```

```
make[1]: Entering directory '/home/user/src/wazo-scalability-clean/load-infra'
openssl genpkey -algorithm RSA -out certs/clients/trafgen1.load.wazo.io.key
............+.+...+...+.....+.............+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*..+....+.....+......+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*...+...+..........+.....+.......+..+...+....+.....+..........+...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
...........+.+.....+.+......+..............+...+.+......+......+..+.+..+.......+..+...+...+...+....+...+........+....+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*...+........+...+.+...+..+....+.........+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*...+...+............+........+...+...+.+...+..+...+...+....+...........+...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
openssl req -new -key certs/clients/trafgen1.load.wazo.io.key -out certs/clients/trafgen1.load.wazo.io.csr -subj "/CN=*.load.wazo.io"
openssl x509 -req -in certs/clients/trafgen1.load.wazo.io.csr -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial -out certs/clients/trafgen1.load.wazo.io.crt -days 3650 -sha256
Certificate request self-signature ok
subject=CN = *.load.wazo.io
make[1]: Leaving directory '/home/user/src/wazo-scalability-clean/load-infra'
```

The following file have been created:
```
$ tree load-infra/certs/clients/
load-infra/certs/clients/
└── trafgen1.load.wazo.io
    ├── client.crt
    ├── client.csr
    └── client.key

2 directories, 3 files
```

#### 3.2.1 Several clients
You need to have a ca.key file put in the `load-infra/certs/ca/` folder.
At the root of the wazo-scalability directory run the following command
```
$ make clients-cert CLIENTS="trafgen1.load.wazo.io trafgen2.load.wazo.io"
```

```
make[1]: Entering directory '/home/user/src/wazo-scalability-clean/load-infra'
openssl genpkey -algorithm RSA -out certs/clients/trafgen1.load.wazo.io.key
...........+..+.+.........+.....+...+.......+...+...+..+......+....+.....+.+............+...+.....+......+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*.....+...+.................+...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*....+............+...+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
.....+..+.......+.....+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*..+..+...+......+.............+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*....+.......+..+....+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
openssl req -new -key certs/clients/trafgen1.load.wazo.io.key -out certs/clients/trafgen1.load.wazo.io.csr -subj "/CN=*.load.wazo.io"
openssl x509 -req -in certs/clients/trafgen1.load.wazo.io.csr -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial -out certs/clients/trafgen1.load.wazo.io.crt -days 3650 -sha256
Certificate request self-signature ok
subject=CN = *.load.wazo.io
make[1]: Leaving directory '/home/user/src/wazo-scalability-clean/load-infra'
make[1]: Entering directory '/home/user/src/wazo-scalability-clean/load-infra'
openssl genpkey -algorithm RSA -out certs/clients/trafgen2.load.wazo.io.key
..........+.....+.+...+........+...+.+.....+.+...+............+..+.+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*.......+..+................+..+...+.......+...+........+.+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*.....+..........+...+......+....................+.+........+...+...+............+....+..................+.....+.......+...+..+...+.+.....+.+...+...........+....+...+.................+......+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
.+............+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*....+...+....+........+.+..+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*.+......+.............+..+...+.+..+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
openssl req -new -key certs/clients/trafgen2.load.wazo.io.key -out certs/clients/trafgen2.load.wazo.io.csr -subj "/CN=*.load.wazo.io"
openssl x509 -req -in certs/clients/trafgen2.load.wazo.io.csr -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial -out certs/clients/trafgen2.load.wazo.io.crt -days 3650 -sha256
Certificate request self-signature ok
subject=CN = *.load.wazo.io
make[1]: Leaving directory '/home/user/src/wazo-scalability-clean/load-infra'
```

The following files have been created:
```
$ tree load-infra/certs/clients/
load-infra/certs/clients/
├── trafgen1.load.wazo.io
│   ├── client.crt
│   ├── client.csr
│   └── client.key
└── trafgen2.load.wazo.io
    ├── client.crt
    ├── client.csr
    └── client.key

3 directories, 6 files
```
