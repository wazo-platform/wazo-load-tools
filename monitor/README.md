# Monitor

This directory is intended to house environment designed to observe and analyze
the performance of Wazo Platform servers, particularly under simulated load
conditions. These tools assist in identifying system bottlenecks, ensuring
optimal performance, and validating the platform's scalability during testing
scenarios.

## Setup

- Install [Docker](https://www.docker.com/)
- Install [gcx](https://grafana.com/docs/grafana/latest/as-code/observability-as-code/grafana-cli/gcx/installation/)

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
- Give `gcx` a token. Anonymous access is admin, so no login is needed to
  create one. The token lives in the grafana volume: create it again after a
  `docker compose down -v`.

  ```sh
  id=$(curl -s -X POST http://localhost:3000/api/serviceaccounts \
    -H 'Content-Type: application/json' \
    -d '{"name": "gcx", "role": "Admin"}' | jq -r .id)
  key=$(curl -s -X POST "http://localhost:3000/api/serviceaccounts/$id/tokens" \
    -H 'Content-Type: application/json' -d '{"name": "gcx"}' | jq -r .key)
  gcx login load-local --server http://localhost:3000 --token "$key" --yes
  ```

- Import dashboards:
  `gcx resources push --context load-local -p grafana-resources`
- Connect to `http://localhost:3000`

The `Load Tests` folder holds the k6 dashboard
([18030](https://grafana.com/grafana/dashboards/18030-k6-prometheus-native-histograms/)).
It reads trend metrics as native histograms, so the k6 runners must push with
`K6_PROMETHEUS_RW_TREND_AS_NATIVE_HISTOGRAM=true`.

## Edit Dashboards

- Edit dashboard in grafana
- Pull changes: `gcx resources pull --context load-local dashboards folders
  datasources -p grafana-resources -o yaml`

Pulling rewrites every file from the server, so `git diff` shows what changed.
A dashboard belongs to the folder named by its
`metadata.annotations["grafana.app/folder"]`.

## Review Dashboards

To review dashboards with production data, serve the files in this repository
against another instance:

- `gcx login <name> --server http://<production> --token <token> --yes`
- `gcx dev serve --context <name> grafana-resources`
- Open `http://localhost:8080` and pick a dashboard in the index

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

The AMI is resolved from `ami_name_filter` only when the instance is created.
A newer AMI matching the filter does not replace an existing instance. To move
an instance to the latest AMI:

```sh
terraform apply -var-file=<file> -replace=aws_instance.monitor
```

## Alerting Rules

To debug, write or test alerting rules, use `promtool`:

```shell
docker exec prometheus sh -c "promtool test rules /etc/prometheus/tests.yml"
```

- Use `--run <test-name>` to execute specific test
- Use `--debug` to enable debugging and see how many time the alert was
  in "pending" or "firing" state
