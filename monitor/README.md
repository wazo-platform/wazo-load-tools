# Monitor

This directory is intended to house environment designed to observe and analyze
the performance of Wazo Platform servers, particularly under simulated load
conditions. These tools assist in identifying system bottlenecks, ensuring
optimal performance, and validating the platform's scalability during testing
scenarios.

## Setup

- Install [Docker](https://www.docker.com/)
- Install [Grizzly](https://grafana.github.io/grizzly/)
- Configure Grizzly
  - `grr config set grafana.url http://localhost:3000`
  - `grr config set targets Dashboard,Dashboardfolder,Datasource`

- Declare the hosts to scrape. Prometheus discovers EC2 instances tagged
  `LoadRole` (`wazo` or `edge`) and `Fqdn` in `eu-west-1`, which needs AWS
  credentials: an instance profile on AWS, or exported in the shell that
  starts the containers:

  ```sh
  eval "$(aws configure export-credentials --format env)"
  ```

  Without credentials, discovery logs an error every minute and finds
  nothing; list hosts by hand instead in `prometheus-config/targets/`
  (gitignored):

  ```yaml
  # prometheus-config/targets/stack.yml
  - targets: ['<wazo-ip>:6387']
  # prometheus-config/targets/edge.yml
  - targets: ['<edge-ip>:6387']
  ```

- (Optional) Update Alertmanager configuration file:
  `alertmanager-config/alertmanager.yml`

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

## Terraform

Contains the Terraform files used to provision the orchestrator instance, which
hosts the monitoring services.

The instance is bound to an existing instance profile given by
`iam_instance_profile_name`. Neither the profile nor its role is managed here:
the role must allow `ec2:DescribeInstances` and `ec2:DescribeAvailabilityZones`
for prometheus EC2 discovery. Creating the profile in the same apply as the
instance would race IAM propagation and leave the instance without a role.

```sh
terraform init
terraform plan -var-file=<file>
terraform apply -var-file=<file>
```

## Alerting Rules

To debug, write or test alerting rules, use `promtool`:

```shell
docker exec prometheus sh -c "promtool test rules /etc/prometheus/tests.yml"
```

- Use `--run <test-name>` to execute specific test
- Use `--debug` to enable debugging and see how many time the alert was
  in "pending" or "firing" state
