# Monitor

## Setup

- Install [Docker](https://www.docker.com/)
- Install [Grizzly](https://grafana.github.io/grizzly/)
- Configure Grizzly
  - `grr config set grafana.url http://localhost:3000`
  - `grr config set grafana.user admin`
  - `grr config set grafana.token secret`
  - `grr config set targets Dashboard,Dashboardfolder,Datasource`

- Generate prometheus configuration file

  ```sh
  pip install -r ./prometheus-config-generator/requirements.txt
  ./prometheus-config-generator/generate.py --wazo-host <wazo-ip> -o prometheus-config/prometheus.yml
  ```

## Run Environment

- Start containers: `docker compose up -d`
- Import dashboards: `grr apply grafana-resources`
- Connect to `http://localhost:3000`

## Edit Dashboards

- Edit dashboard using `grr` or in grafana
- Pull changes: `grr pull grafana-resources`

## Review Dashboards

To review dashboards with production data, you can use `grr`:

- Configure Grizzly
  - `grr config set grafana.url http://<production>`
  - `grr config set grafana.user admin`
  - `grr config set grafana.token <token or password>`

- `grr serve grafana-resources`
- Open `http://localhost:8080`

## Infra

Contains terraform files to build monitor instance and its dependencies

```sh
terraform init
terraform plan -var-file=<file>
terraform apply -var-file=<file>
```
