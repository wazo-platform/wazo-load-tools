# wazo-load-tools

> [!IMPORTANT]
> Previous tools have been archived under the
> [`legacy`](https://github.com/wazo-platform/wazo-load-tools/tree/legacy) tag
> and should be referenced for any new scripts or projects in this repository.

## Provision new server

1. Install a fresh wazo server
2. Execute:

  ```shell
  pip install -r initiator/requirements.txt
  pip install -r generator/users/requirements.txt
  cat initiator/setup-system.sh | ssh <wazo-host>
  initiator/setup-wazo.py \
    --host <wazo-host> \
    --password <password> \
    --output generator/users/config.yml
  generator/users/generate-users.py \
    --number<#users> \
    --extra-config generator/users/config.yml \
    --format csv \
    --output generator/users/users.csv
  generator/users/create-users.py \
    --host <wazo-host> \
    --password <password> \
    --users-file generator/users/users.csv \
    --format csv \
    --extra-config generator/users/config.yml \
    --output generator/users/created-users.json
  genetator/users/add-users-to-group.py
    --host <wazo-host> \
    --password <password> \
    --created-users-file generator/users/created-users.json \
    --extra-config generator/users/config.yml
  ```
