# Scenario metrics

WARNING: This readme is only draft documentation before continuing the project
         i.e. It's not expected to be merged as it

This project add metrics about load testing scenario to help to fire alerts
correctly

## Installation

Configure wazo instance to expose new metrics:

```shell
cat > /etc/nginx/locations/https-available/load-test-metrics <<-EOF
location = /api/load-test/metrics {
  default_type text/plain;
  alias /var/www/html/load-test-metrics;
}
EOF

ln -s /etc/nginx/locations/https-available/load-test-metrics /etc/nginx/locations/https-enabled/load-test-metrics
systemctl reload nginx
```

Configure prometheus to fetch those metrics:

```yaml
scrape_configs:
  - job_name: load-test
    scheme: https
    tls_config:
      insecure_skip_verify: true
    metrics_path: /api/load-test/metrics
    static_configs:
      - targets: ['<wazo>:443']
```

## Add or Update Metrics

```shell
cat > /var/www/html/load-test-metrics <<-EOF
load_test_enabled 1
load_test_simultaneous_calls 30
EOF
```
