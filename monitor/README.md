# Monitor

## Setup

- Install [Docker](https://www.docker.com/)
- Install [Grizzly](https://grafana.github.io/grizzly/)
- Configure Grizzly
  - `grr config set grafana.url http://localhost:3000`
  - `grr config set grafana.user admin`
  - `grr config set grafana.token secret`
  - `grr config set targets Dashboard,Dashboardfolder,Datasource`

- Edit `prometheus-config/prometheus.yml` to replace `localhost` by the
  `<wazo-ip>`

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
