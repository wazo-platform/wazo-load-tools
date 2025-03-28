# Initiator

## setup-system

Install tools and enable debug on wazo services

```shell
cat setup-system.sh | ssh <wazo-ip>
```

## setup-wazo

Initialize wazo server by creating default resources
The script will generate a configuration file used by users generators

```shell
./setup-wazo.py -s <wazo-ip> -p <password> -o ../generator/users/config.yml
```
