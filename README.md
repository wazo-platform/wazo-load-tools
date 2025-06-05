# wazo-load-tools

This is a collection of scripts and utilities for provisioning and load-testing
[Wazo Platform](https://wazo-platform.org) servers.

## Repository Structure

> [!IMPORTANT]
> Older tools have been archived under the
> [`legacy`](https://github.com/wazo-platform/wazo-load-tools/tree/legacy) tag
> and should be referenced before writing new scripts or adding projects in this
> repository.

The repository is organized into several directories, each serving a different
role:

- `initiator`: Scripts for bootstrapping a Wazo server, including system setup
  and basic API configuration.
- `generator`: Tools for defining, generating, and creating test users. Supports
  CSV and JSON output formats and includes helpers for group assignment.
- `monitor`: Environment to collect performance metrics during high-load
  scenarios.

These tools are intended for internal testing, development, and validation
purposes only.

## Getting Started

Each directory includes its own `README.md` with specific usage instructions.

Below is a typical usage example that chains the tools together and demonstrates
how output from one step feeds into the next.

1. Install a fresh wazo server
2. Run the following commands:

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
