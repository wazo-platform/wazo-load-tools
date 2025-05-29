# wazo-load-testing-metrics-plugin

**Warning**: This plugin is for load testing only and must not be used in
production due to security risks.

Add load testing metrics. See `metrics` file for more information

## Installation

```sh
wazo-plugind-cli -c "install git https://github.com/wazo-platform/wazo-load-tools --subdirectory monitor/wazo-load-testing-metrics-plugin"
```

Installing this plugin will reload nginx and expose two new endpoints:

- `/api/load-testing/metrics`: Retrieve specific metrics for current load
  testing scenario
- `/api/load-testing/metrics/update`: Upload file to change testing scenario
  metrics

## Uninstallation

```sh
wazo-plugind-cli -c "uninstall wazoplatform/wazo-load-testing-metrics"
```
