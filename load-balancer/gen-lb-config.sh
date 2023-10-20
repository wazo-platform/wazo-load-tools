#!/bin/bash
LAST_PORT=${1-0}
TRAFGEN_NODES=${2-1}

OUTPUT=nginx.conf.generated
cat >$OUTPUT<<'EOF'
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                      '\$status \$body_bytes_sent "\$http_referer" '
                      '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;
    upstream pilot {
	    server orchestrator.load.wazo.io:9990;
    }
    upstream backend {
EOF

UPSTREAMS_FILE=upstreams
start_port=9900
for x in $(seq 1 $TRAFGEN_NODES); do
	for y in $(seq 0 $LAST_PORT); do
		port=$(( $start_port + $y ))
cat >>$OUTPUT<<EOF
		server trafgen$x.load.wazo.io:$port;
EOF
	done
done
cat >>$OUTPUT<<EOF
    }
    include /etc/nginx/conf.d/*.conf;
}
EOF
