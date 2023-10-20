FROM nginx:1.25.2

RUN apt-get update && apt-get install -y vim

COPY cluster.conf /etc/nginx/conf.d/default.conf
COPY pilot.conf /etc/nginx/conf.d/pilot.conf
COPY nginx.conf.generated /etc/nginx/nginx.conf
COPY certs /etc/ssl/certs/

CMD [ "nginx", "-s", "start" ]

