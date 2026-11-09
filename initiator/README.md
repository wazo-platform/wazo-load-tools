# Initiator

This directory contains scripts to prepare and configure a fresh Wazo
Platform server. These scripts automate system initialization, API access
configuration, and generate a reusable configuration file for subsequent
provisioning steps (e.g., user creation).

## Usage

## Configure Server

Install tools, the prometheus exporter plugin and the profiler. The script
reads `profiler/config.alloy`, so run it from a copy of this directory:

```shell
scp -r ../initiator root@<wazo-ip>:/tmp/
ssh root@<wazo-ip> bash /tmp/initiator/setup-system.sh
```

### Profiler

[Grafana Alloy](https://grafana.com/docs/alloy/latest/) profiles the CPU of
every process with eBPF and pushes to the load monitor
[Pyroscope](https://grafana.com/docs/pyroscope/latest/), with
`asterisk-dbgsym` for readable Asterisk frames. It runs at every boot.

Its labels follow the ones Prometheus derives from the EC2 tags: `service_name`
matches the process-exporter groups, and `instance` is the `FQDN` environment
variable (the hostname when unset), or `ephemeral` with a `testid` when
`LOAD_TEST_ID` is set. Set them with a systemd drop-in, then restart Alloy:

```shell
cat > /etc/systemd/system/alloy.service.d/labels.conf <<EOF
[Service]
Environment=LOAD_TEST_ID=<test-id>
EOF
systemctl daemon-reload
systemctl restart alloy
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
