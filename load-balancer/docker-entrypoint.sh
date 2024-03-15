#!/usr/bin/bash

# Signal setup
stop_nginx() {
  echo "Arrêt de Nginx..."
  nginx -s quit
  exit $?
}

trap 'stop_nginx' SIGTERM

echo "Load balancer initialization..."

if [ -z "$CONNECT_TIMEOUT" ]; then
    export CONNECT_TIMEOUT=60
fi
if [ -z "$READ_TIMEOUT" ]; then
    export READ_TIMEOUT=600
fi

CLUSTER_CONF=/etc/nginx/conf.d/cluster.conf
CLUSTER_TPL=/startup/cluster.conf.tpl
sed -e "s/__CONNECT_TIMEOUT__/$CONNECT_TIMEOUT/g" -e "s/__READ_TIMEOUT__/$READ_TIMEOUT/g" $CLUSTER_TPL > $CLUSTER_CONF

PILOT_CONF=/etc/nginx/conf.d/pilot.conf
PILOT_TPL=/startup/pilot.conf.tpl
sed -e "s/__CONNECT_TIMEOUT__/$CONNECT_TIMEOUT/g" -e "s/__READ_TIMEOUT__/$READ_TIMEOUT/g" $PILOT_TPL > $PILOT_CONF

# Need to match the number of cluster nodes deployed
if [ -z "$TRAFGEN_NODES" ]; then
    export TRAFGEN_NODES=1
fi
# Need to match the number of containers per cluster node 
if [ -z "$LAST_CONTAINER" ]; then
    export LAST_CONTAINER=0
fi

export CONTAINERS=$(($LAST_CONTAINER + 1))
export CLUSTER_SIZE=$(($CONTAINERS * $TRAFGEN_NODES))

/startup/gen-lb-config.sh $LAST_CONTAINER $TRAFGEN_NODES

echo "Starting Nginx..."
nginx -g "daemon off;"

sleep infinity