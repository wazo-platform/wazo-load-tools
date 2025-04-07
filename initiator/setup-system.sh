#!/usr/bin/env bash
set -e
set -u  # fail if variable is undefined
set -o pipefail  # fail if command before pipe fails

PLUGIN_BRANCH="${1:-master}"

echo 'Installing debug tools...'
apt-get update
apt-get install -y htop

echo 'Configuring postgresql debug...'
echo 'log_min_duration_statement = 0' >  /etc/postgresql/13/main/conf.d/wazo-acceptance-debug.conf
systemctl reload postgresql

WAZO_SERVICES=(
    'wazo-agentd'
    'wazo-agid'
    'wazo-amid'
    'wazo-auth'
    'wazo-call-logd'
    'wazo-calld'
    'wazo-chatd'
    'wazo-confd'
    'wazo-confgend'
    'wazo-dird'
    'wazo-phoned'
    'wazo-plugind'
    'wazo-provd'
    'wazo-setupd'
    'wazo-sysconfd'
    'wazo-webhookd'
    'wazo-websocketd'
)

enable_debug() {
    service_name=$1
    echo "Configuring $service_name debug..."
    if [ "$service_name" == "wazo-provd" ]; then
        echo "general: {verbose: true}" > "/etc/$service_name/conf.d/debug.yml"
    else
        echo "debug: true" > "/etc/$service_name/conf.d/debug.yml"
    fi
    systemctl restart "$service_name"
}

for wazo_service in "${WAZO_SERVICES[@]}"; do
    enable_debug "$wazo_service"
done

apt-get install -y wazo-plugind-cli
wazo-plugind-cli -c "install git https://github.com/wazo-platform/wazo-prometheus-exporter-plugin --ref $PLUGIN_BRANCH"
