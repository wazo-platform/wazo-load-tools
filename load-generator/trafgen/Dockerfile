From python:3.11.1-bullseye

RUN apt-get update && apt-get install -y git
RUN mkdir /trafgen 

WORKDIR /trafgen

RUN  git clone https://github.com/wazo-platform/xivo-load-tester.git