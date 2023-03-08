FROM python:3.11.1-bullseye

RUN apt-get update && apt-get install -y git

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ws-client.py /usr/bin/ws-client.py
COPY runner.py /usr/bin/runner.py


CMD ["sleep", "infinity"]