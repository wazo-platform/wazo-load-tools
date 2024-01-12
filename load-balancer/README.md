# Building load balancer images
This load balancer allows to clusterize the docker fleet that is used for the load testing.

## 1 This load balancer has two aims:
1 - Act as a reverse proxy for the pilot
2 - Get a cluster with round robin of wlapi.


## 2 Handling versionning system
the load balancer images follow the semver pattern
`major.minor.patch`
### 2.1 Showing the current version
```
$ make show-version
Current version is: 1.0.9
```

By default the  versionning management system is setup to bump a patch
### 2.2 Bumping manually the version
Here we'll bump the patch number
```
$ make bump-version
$ make show-version
Current version is: 1.0.10
```
If you need to bump the minor version:
```
$ make bump-version SEMVER=minor
$ make show-version
Current version is: 1.1.0
```
If you need to bump the minor version:
```
$ make bump-version SEMVER=major
load-balancer$ make show-version
Current version is: 2.0.0
```
### 2.3 manually set a version
```
$ make show-version
Current version is: 1.0.0
$ make set-version NEW_VERSION=1.0.9
$ make show-version
Current version is: 1.0.9
```



## 3 Generating an image for a load-balancer
### 3.1 single node cluster

1 - It can be convenient in order to debug a wlapi image to create  load balancer configuration with a single node.
you need to move to the `load-balancer/` directory that contains the `makefile`

```
$ make build LAST_CONTAINER=0 TRAFGEN_NODES=1
```

```
Certificate request self-signature ok
subject=CN = example.com
[+] Building 1.0s (11/11) FINISHED                                                                                                                                        docker:default
 => [internal] load build definition from Dockerfile                                                                                                                                0.0s
 => => transferring dockerfile: 312B                                                                                                                                                0.0s
 => [internal] load .dockerignore                                                                                                                                                   0.0s
 => => transferring context: 2B                                                                                                                                                     0.0s
 => [internal] load metadata for docker.io/library/nginx:1.25.2                                                                                                                     0.8s
 => [1/6] FROM docker.io/library/nginx:1.25.2@sha256:b4af4f8b6470febf45dc10f564551af682a802eda1743055a7dfc8332dffa595                                                               0.0s
 => [internal] load build context                                                                                                                                                   0.0s
 => => transferring context: 4.67kB                                                                                                                                                 0.0s
 => CACHED [2/6] RUN apt-get update && apt-get install -y vim                                                                                                                       0.0s
 => CACHED [3/6] COPY cluster.conf /etc/nginx/conf.d/default.conf                                                                                                                   0.0s
 => CACHED [4/6] COPY pilot.conf /etc/nginx/conf.d/pilot.conf                                                                                                                       0.0s
 => [5/6] COPY nginx.conf.generated /etc/nginx/nginx.conf                                                                                                                           0.0s
 => [6/6] COPY certs /etc/ssl/certs/                                                                                                                                                0.0s
 => exporting to image                                                                                                                                                              0.1s
 => => exporting layers                                                                                                                                                             0.1s
 => => writing image sha256:aa4947b3d7eaf5687fe07f9aded712e34c507e664dfc56138a127035fcb7965d                                                                                        0.0s
 => => naming to docker.io/library/trafgen-lb-1:1.0.10    
```
``
### Full node cluster
2 - If you want to get the load balancer serving the whole cluster
For example you have 10 trafgen nodes operating 100 containers (0 - 99)
```
$ make build LAST_CONTAINER=99 TRAFGEN_NODES=10
Certificate request self-signature ok
subject=CN = example.com
[+] Building 0.9s (11/11) FINISHED                                                                                                                                                                                                                                                 docker:default
 => [internal] load build definition from Dockerfile                                                                                                                                                                                                                                         0.0s
 => => transferring dockerfile: 314B                                                                                                                                                                                                                                                         0.0s
 => [internal] load .dockerignore                                                                                                                                                                                                                                                            0.0s
 => => transferring context: 2B                                                                                                                                                                                                                                                              0.0s
 => [internal] load metadata for docker.io/library/nginx:1.25.2                                                                                                                                                                                                                              0.7s
 => [1/6] FROM docker.io/library/nginx:1.25.2@sha256:b4af4f8b6470febf45dc10f564551af682a802eda1743055a7dfc8332dffa595                                                                                                                                                                        0.0s
 => [internal] load build context                                                                                                                                                                                                                                                            0.0s
 => => transferring context: 41.74kB                                                                                                                                                                                                                                                         0.0s
 => CACHED [2/6] RUN apt-get update && apt-get install -y vim                                                                                                                                                                                                                                0.0s
 => CACHED [3/6] COPY cluster.conf /etc/nginx/conf.d/default.conf                                                                                                                                                                                                                            0.0s
 => CACHED [4/6] COPY pilot.conf /etc/nginx/conf.d/pilot.conf                                                                                                                                                                                                                                0.0s
 => [5/6] COPY nginx.conf.generated /etc/nginx/nginx.conf                                                                                                                                                                                                                                    0.0s
 => [6/6] COPY certs /etc/ssl/certs/                                                                                                                                                                                                                                                         0.0s
 => exporting to image                                                                                                                                                                                                                                                                       0.1s
 => => exporting layers                                                                                                                                                                                                                                                                      0.0s
 => => writing image sha256:4c0e609ea590f8abae5e8ced5f9cda587369ece073607833023f0d591d5a8320                                                                                                                                                                                                 0.0s
 => => naming to docker.io/library/trafgen-lb-1000:1.0.11    
```

## Running an image
```
$ make run 
cd878c200ea43fc7d2d0ea22c386f98c105a6fbfa315fd7a573fd3ef19b5623c
```
or 
```
$ make run IMAGE_NAME=$(cat .last_image_built)

e3a82811a63080de2f149e0a0d3457a21e5d1b3e40cf9a30de295593b567f502
`