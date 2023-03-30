#!/usr/bin/env python3
import paramiko
import scp
import yaml

class remoteControl():
    def __init__(self, host, scenario, script, container, keyfile, command):
        self.host = host
        self.scenario = scenario
        self.script = script
        self.container = container
        self.keyfile = keyfile
        self.command = command

    def connect(self):
        client = paramiko.SSHClient()
        client.connect(self.host, username='root', pkey=self.keyfile, timeout=5)
        transport = client.get_transport()
        self.channel = transport.open_session()

    def run(self):
        #self.channel.exec_command('python script.py > /dev/null 2>&1 &')
        self.channel.exec_command(self.command)
        self.channel.close()

class commandFactory():
    def __init__(self, container, scenario):
        self.container = container
        self.scenario = scenario

    def start(self):
        return f"docker-compose start {self.container}"

    def stop(self):
        return f"docker-compose stop {self.container}"

    def restart(self):
        return f"docker-compose restart {self.container}"

    def exec_sip_load(self):
        return f'docker exec -d {self.container} bash -c "export SCENARIO={self.scenario} /trafgen/load.sh" > /dev/null 2>&1 &'


def parse_config(yml):
    with open(yml, "r") as f:
        trafgen = yaml.safe_load(f)
    for load in trafgen["loads"]:
        yield load


if __name__ == "__main__":
    for load in  parse_config("trafgen.yml"):
        for node in load["load"]:
            print(node)