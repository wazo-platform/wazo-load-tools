server {
    listen 443 ssl;
    server_name pilot.load.wazo.io;
    ssl_certificate /etc/ssl/certs/server.pem;
    ssl_certificate_key /etc/ssl/certs/server.key;

    location / {
        proxy_pass https://pilot;
        proxy_ssl_verify off;
        proxy_connect_timeout __CONNECT_TIMEOUT__s;
        proxy_read_timeout __READ_TIMEOUT__s;
    }
}
