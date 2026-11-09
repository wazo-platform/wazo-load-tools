#!/usr/bin/env bash
set -e
set -u  # fail if variable is undefined
set -o pipefail  # fail if command before pipe fails

PROMETHEUS_PLUGIN_BRANCH="${1:-master}"
INITIATOR_DIR="$(dirname "$(readlink -f "$0")")"

echo 'Installing debug tools...'
apt-get update
apt-get install -y htop

# Useful for debugging new load scenarios, but excessive for continuous runs.
# echo 'Configuring postgresql debug...'
# echo 'log_min_duration_statement = 0' > /etc/postgresql/15/main/conf.d/wazo-acceptance-debug.conf
# systemctl reload postgresql
#
# WAZO_SERVICES=(
#     'wazo-agentd'
#     'wazo-agid'
#     'wazo-amid'
#     'wazo-auth'
#     'wazo-call-logd'
#     'wazo-calld'
#     'wazo-chatd'
#     'wazo-confd'
#     'wazo-confgend'
#     'wazo-dird'
#     'wazo-phoned'
#     'wazo-plugind'
#     'wazo-provd'
#     'wazo-setupd'
#     'wazo-sysconfd'
#     'wazo-webhookd'
#     'wazo-websocketd'
# )
#
# enable_debug() {
#     service_name=$1
#     echo "Configuring $service_name debug..."
#     if [ "$service_name" == "wazo-provd" ]; then
#         echo "general: {verbose: true}" > "/etc/$service_name/conf.d/debug.yml"
#     else
#         echo "debug: true" > "/etc/$service_name/conf.d/debug.yml"
#     fi
#     systemctl restart "$service_name"
# }
#
# for wazo_service in "${WAZO_SERVICES[@]}"; do
#     enable_debug "$wazo_service"
# done

apt-get install -y wazo-plugind-cli
wazo-plugind-cli install git https://github.com/wazo-platform/wazo-prometheus-exporter-plugin --ref "$PROMETHEUS_PLUGIN_BRANCH"

echo 'Installing profiler...'
apt-get install -y curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://apt.grafana.com/gpg.key -o /etc/apt/keyrings/grafana.asc
echo 'deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main' > /etc/apt/sources.list.d/grafana.list
apt-get update
apt-get install -y alloy asterisk-dbgsym
install -m 0644 "$INITIATOR_DIR/profiler/config.alloy" /etc/alloy/config.alloy
# eBPF needs root; the limits keep the profiler from skewing the load
mkdir -p /etc/systemd/system/alloy.service.d
cat > /etc/systemd/system/alloy.service.d/profiling.conf <<'EOF'
[Service]
User=root
CPUQuota=50%
MemoryMax=1G
EOF
systemctl daemon-reload
systemctl enable alloy
systemctl restart alloy
