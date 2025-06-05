# Generator

This directory provides a suite of scripts designed to create and manage test
users on a Wazo Platform server. These tools facilitate the bulk generation of
user accounts, their provisioning on the server, and their organization into
groups, streamlining the process of setting up test environments for load
testing and development purposes.

## Usage

### Users

Generate and create wazo users

The `config.yml` file can be manually created or generated from
`initiator/setup-wazo.sh`. Example of configuration file:

```yml
tenant_uuid: 769e37ba-a9fb-4c4d-bc21-23716338fa6b
global_sip_template_uuid: 3898a4a0-3af7-41f0-a3c4-7d2ef67d2b36
internal_context: ctx-loadG3IDVQ-internal-7e6207f2-d1f7-49d4-a976-b6ff7aea79c6
incall_context: ctx-loadG3IDVQ-incall-543bccd5-31ba-4e86-9201-81e64e3d375e
incall_prefix: '123'
group_uuid: f72d2ffb-65ae-41e3-8421-9a509242757b
```

#### Generate Users

Create a file with the desired number of test users:

```shell
./users/generate-users.py -n10 -f csv -c users/config.yml -o users/users.csv
```

#### Create Users

Provision the generated users onto the Wazo server:

```shell
./users/create-users.py -s <wazo-ip> -p <password> -u users/users.csv -f csv -c users/config.yml
```
