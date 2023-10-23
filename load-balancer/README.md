# load balancer

This load balancer allows to clusterize the docker fleet that is used for the load testing.

## This load balancer has two aims:
1 - Act as a reverse proxy for the pilot
2 - Get a cluster with round robin of wlapi.

## Generating an image for a load-balancer
1 - It can be convenient in order to debug a wlapi image to create  load balancer configuration with a single node.
you need to move to the `load-balancer/` directory that contains the `makefile`
```
make build LAST_CONTAINER=0 TRAFGEN_NODES=1
rm *.generated
rm -rf certs
mkdir certs
openssl genrsa -out certs/server.key 2048
openssl req -new -key certs/server.key -out certs/server.csr -subj "/CN=example.com"
openssl x509 -req -in certs/server.csr -signkey certs/server.key -out certs/server.pem -days 36500
Certificate request self-signature ok
subject=CN = example.com
./gen-lb-config.sh 0 1
docker build -t trafgen-lb-1:0.0.3 -f Dockerfile .
[+] Building 1.0s (13/13) FINISHED                                                                                                                                                                                                                                         docker:default
 => [internal] load build definition from Dockerfile                                                                                                                                                                                                                                 0.0s
 => => transferring dockerfile: 425B                                                                                                                                                                                                                                                 0.0s
 => [internal] load .dockerignore                                                                                                                                                                                                                                                    0.0s
 => => transferring context: 2B                                                                                                                                                                                                                                                      0.0s
 => [internal] load metadata for docker.io/library/nginx:1.25.2                                                                                                                                                                                                                      0.8s
 => [internal] load build context                                                                                                                                                                                                                                                    0.0s
 => => transferring context: 3.92kB                                                                                                                                                                                                                                                  0.0s
 => [1/8] FROM docker.io/library/nginx:1.25.2@sha256:b4af4f8b6470febf45dc10f564551af682a802eda1743055a7dfc8332dffa595                                                                                                                                                                0.0s
 => CACHED [2/8] RUN apt-get update && apt-get install -y vim                                                                                                                                                                                                                        0.0s
 => CACHED [3/8] COPY index.html /usr/share/nginx/html/index.html                                                                                                                                                                                                                    0.0s
 => CACHED [4/8] COPY cluster.conf /etc/nginx/conf.d/default.conf                                                                                                                                                                                                                    0.0s
 => CACHED [5/8] COPY pilot.conf /etc/nginx/conf.d/pilot.conf                                                                                                                                                                                                                        0.0s
 => CACHED [6/8] COPY resolv.conf /etc/resolv.conf.override                                                                                                                                                                                                                          0.0s
 => CACHED [7/8] COPY nginx.sh /usr/local/bin/nginx.sh                                                                                                                                                                                                                               0.0s
 => [8/8] COPY certs /etc/ssl/certs/                                                                                                                                                                                                                                                 0.0s
 => exporting to image                                                                                                                                                                                                                                                               0.0s
 => => exporting layers                                                                                                                                                                                                                                                              0.0s
 => => writing image sha256:c3655265a3339bd02dbae87df8b13acc4bec06f13011de475a7a75c8850d1fd2                                                                                                                                                                                         0.0s
 => => naming to docker.io/library/trafgen-lb-1:0.0.3
```
you can test the new image:
```
$ make run LAST_CONTAINER=0 TRAFGEN_NODES=1

docker stop trafgen-lb
Error response from daemon: No such container: trafgen-lb
make: [makefile:23: stop] Error 1 (ignored)
docker run -d -p 9999:443 -p 9998:80 --rm --name trafgen-lb trafgen-lb-1:0.0.3
cd878c200ea43fc7d2d0ea22c386f98c105a6fbfa315fd7a573fd3ef19b5623c
```
```
$ docker ps

CONTAINER ID   IMAGE                COMMAND                  CREATED         STATUS         PORTS                                                                            NAMES
cd878c200ea4   trafgen-lb-1:0.0.3   "/docker-entrypoint.…"   4 seconds ago   Up 3 seconds   0.0.0.0:9998->80/tcp, :::9998->80/tcp, 0.0.0.0:9999->443/tcp, :::9999->443/tcp   trafgen-lb
```

and to know which trafgen node is served by the load balancer:
```
$ docker exec -ti trafgen-lb cat /etc/nginx/nginx.conf| grep trafgen
                server trafgen1.load.wazo.io:9900;
```
2 - If you want to get the load balancer serving the whole cluster
For example you have 10 trafgen nodes operating 100 containers (0 - 99)
```
$ make build LAST_CONTAINER=99 TRAFGEN_NODES=10

rm *.generated
rm -rf certs
mkdir certs
openssl genrsa -out certs/server.key 2048
openssl req -new -key certs/server.key -out certs/server.csr -subj "/CN=example.com"
openssl x509 -req -in certs/server.csr -signkey certs/server.key -out certs/server.pem -days 36500
Certificate request self-signature ok
subject=CN = example.com
./gen-lb-config.sh 99 10
docker build -t trafgen-lb-1000:0.0.3 -f Dockerfile .
[+] Building 0.6s (14/14) FINISHED                                                                                                                                                                                                                                         docker:default
 => [internal] load build definition from Dockerfile                                                                                                                                                                                                                                 0.0s
 => => transferring dockerfile: 424B                                                                                                                                                                                                                                                 0.0s
 => [internal] load .dockerignore                                                                                                                                                                                                                                                    0.0s
 => => transferring context: 2B                                                                                                                                                                                                                                                      0.0s
 => [internal] load metadata for docker.io/library/nginx:1.25.2                                                                                                                                                                                                                      0.3s
 => [1/9] FROM docker.io/library/nginx:1.25.2@sha256:b4af4f8b6470febf45dc10f564551af682a802eda1743055a7dfc8332dffa595                                                                                                                                                                0.0s
 => [internal] load build context                                                                                                                                                                                                                                                    0.0s
 => => transferring context: 41.71kB                                                                                                                                                                                                                                                 0.0s
 => CACHED [2/9] RUN apt-get update && apt-get install -y vim                                                                                                                                                                                                                        0.0s
 => CACHED [3/9] COPY index.html /usr/share/nginx/html/index.html                                                                                                                                                                                                                    0.0s
 => CACHED [4/9] COPY cluster.conf /etc/nginx/conf.d/default.conf                                                                                                                                                                                                                    0.0s
 => CACHED [5/9] COPY pilot.conf /etc/nginx/conf.d/pilot.conf                                                                                                                                                                                                                        0.0s
 => [6/9] COPY nginx.conf.generated /etc/nginx/nginx.conf                                                                                                                                                                                                                            0.0s
 => [7/9] COPY resolv.conf /etc/resolv.conf.override                                                                                                                                                                                                                                 0.0s
 => [8/9] COPY nginx.sh /usr/local/bin/nginx.sh                                                                                                                                                                                                                                      0.0s
 => [9/9] COPY certs /etc/ssl/certs/                                                                                                                                                                                                                                                 0.0s
 => exporting to image                                                                                                                                                                                                                                                               0.1s
 => => exporting layers                                                                                                                                                                                                                                                              0.1s
 => => writing image sha256:1b243f77d5e2c680c085960d631034ff20293a774ae1a71f65c345026f328a89                                                                                                                                                                                         0.0s
 => => naming to docker.io/library/trafgen-lb-1000:0.0.3                                     
```

run it with:
```
$ make run LAST_CONTAINER=99 TRAFGEN_NODES=10
docker stop trafgen-lb
trafgen-lb
docker run -d -p 9999:443 -p 9998:80 --rm --name trafgen-lb trafgen-lb-1000:0.0.3
727b90ba0812d5abbec838d1e55d8b0d77f9d50f4a615b5104fd746c2054fba8
```

And you can validate there are 1000 upstreams defined:
```
$ docker exec -ti trafgen-lb cat /etc/nginx/nginx.conf| grep -c trafgen
1000
```
3 - The image will be generated with certificates.
