# Initiator

This directory contains scripts to prepare and configure a fresh Wazo
Platform server. These scripts automate system initialization, API access
configuration, and generate a reusable configuration file for subsequent
provisioning steps (e.g., user creation).

## Usage

## Configure Server

Install tools and enable debug on wazo services

```shell
cat setup-system.sh | ssh <wazo-ip>
```

## Configure Wazo

Initialize wazo server by creating default resources.
The script will generate a configuration file used by by other scripts in the
`generator` directory to create and manage users.

```shell
./setup-wazo.py -s <wazo-ip> -p <password> -o ../generator/users/config.yml
```

### Specific Environment

Configure wazo for specific environment

```shell
# Not behind SIP proxy
./setup-wazo-noproxy.py -s <wazo-ip> -p <password>

# Behind SIP proxy
./setup-wazo-proxy.py -s <wazo-ip> -p <password>
```
