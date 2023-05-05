#!/usr/bin/env python3
import asyncio
import yaml
import queue
import paramiko
import sys
from abc import ABC, abstractmethod

mock = False
wda = False

class RemoteControl():
    def __init__(self, host, keyFile):
        self.host = host
        self.keyFile = keyFile

        self.channel = None

    def connect(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.host, username='root', key_filename=self.keyFile, timeout=5)
            transport = client.get_transport()
            self.channel = transport.open_session()
        except Exception as e:
            raise Exception(e)

    def run(self, command):
        #self.channel.exec_command('python script.py > /dev/null 2>&1 &')
        self.channel.exec_command(command)

    def disconnect(self):
        self.channel.close()


class Command(ABC):
    """Abstract class for command factory"""
    @abstractmethod
    def connect(self):
        pass
    @abstractmethod
    def execute(self):
        pass
    @abstractmethod
    def disconnect(self):
        pass

class DockerComposeStart(Command):
    """Command used to start a specific container that belongs to the load farmework."""
    def __init__(self, host, container, compose, keyFile):
        self.container = container
        self.compose = compose
        self.command = f"docker-compose -f {self.compose} start {self.container}"
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        self.remoteControl.run(self.command)


class DockerComposeStop(Command):
    """Command used to stop a specific container that belongs to the load farmework."""
    def __init__(self, host, container, compose, keyFile):
        self.container = container
        self.compose = compose
        self.command = f"docker-compose -f {self.compose} stop {self.container}"
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        self.remoteControl.run(self.command)

class DockerComposeRetart(Command):
    """Command used to restart a specific container that belongs to the load farmework."""
    def __init__(self, host, container, compose, keyFile):
        self.container = container
        self.compose = compose
        self.command = f"docker-compose -f {self.compose} restart {self.container}"
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        self.remoteControl.run(self.command)


class ExecCmd(Command):
    """Command used to start websocket clients to subscribe RabbitMQ events"""
    def __init__(self, host, container, cmd, keyFile):
        self.container = container
        self.command =  f'docker exec -d {self.container} bash -c \'{cmd}\' > /dev/null 2>&1 &'
        print(f"CMD: {self.command}")
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        self.remoteControl.run(self.command)

class ExecWda(Command):
    """Command used to start websocket clients to subscribe RabbitMQ events"""
    def __init__(self, host, container, cmd, keyFile, env=None):
        self.container = container
        if not env:
            raise Exception("Missing env variables")

        self.command =  f' echo docker exec -e SERVER={env["SERVER"]} -e LOGIN={env["LOGIN"]} -e PASSWORD={env["PASSWORD"]} -e SESSION_DURATION={env["SESSION_DURATION"]} -d {self.container} bash -c \'{cmd}\' > /dev/null 2>&1 &'
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        self.remoteControl.run(self.command)
class MockCmd(Command):
    """Command used as a mock command that prints infosuvicorn main:app --reload."""

    def __init__(self, host, container, cmd, keyFile, env=None):
        self.container = container
        if not env:
            raise Exception("Missing env variables")

        self.command =  f' echo docker exec -e SERVER={env["SERVER"]} -e LOGIN={env["LOGIN"]} -e PASSWORD={env["PASSWORD"]} -e SESSION_DURATION={env["SESSION_DURATION"]} -d {self.container} bash -c \'{cmd}\' > /dev/null 2>&1 &'
        self.host =  host
        

    def connect(self):
        pass

    def disconnect(self):
        pass

    def execute(self):
        print(f"HOST:      {self.host}")
        print(f"CONTAINER: {self.container}")
        print(f"CMD:       {self.command}")

def get_command(node, keyFile):

    if 'host' not in node:
        raise KeyError('Missing required key "host"')
    host = node['host']

    if 'container' not in node:
        raise KeyError('Missing required key "container"')
    container = node['container']

    if 'cmd' not in node:
        raise KeyError('Missing required key "cmd"')
    command = node['cmd']

    env = node.get("env")

    if mock:
        return MockCmd(host, container, command, keyFile, env)
    if wda:
        return ExecWda(host, container, command, keyFile, env)
    
    return ExecCmd(host, container, command, keyFile)


async def process_node(node, ttl, compose, forever, channel, keyFile):
    """
    Coroutine that connects, processes and disconnect from the remote host. Connection duration 
    is based on the TTL
    """
    if 'host' not in node:
        raise KeyError('Missing required key "host"')
    host = node['host']
    if 'container' not in node:
        raise KeyError('Missing required key "container"')
    container = node['container']

    msg = "started"
    if container == "callee":
        msg = await channel.get()
    if msg != "started":
        print(f"quitting due to receiving: {msg}")
        return

    cmd = get_command(node, keyFile)
    # Connection to the remote host 
    cmd.connect()

    if container == "caller":
        await channel.put("started")
        print("sent: started")

    # Execute instruction to the remote host
    cmd.execute()
    # ssh connection is closed after the execution
    cmd.disconnect()

    # Await on the TTL
    await asyncio.sleep(ttl)

    if not forever: 
        # restart the container to end the running tests
        cmd = DockerComposeRetart(host, container, compose, keyFile)
        cmd.connect()
        cmd.execute()
        cmd.disconnect()


async def process_load(load, keyFile):
    """
    Coroutine that processes a workload by creating a process_node coroutine for each node.
    This coroutine setup an additional queue that could be used for node coroutines
    to synchrinize.
    """
    nodes = load.get('load')
    ttl = load.get('ttl')
    compose = load.get('compose')
    forever = load.get('forever')
    coroutines = []

    # create a queue that will allow coroutine to send status.
    q = asyncio.Queue()

    # Loop for creating a coroutine for each node in the workload.
    for node in nodes:
        coroutine = asyncio.create_task(process_node(node, ttl, compose, forever, q, keyFile))
        coroutines.append(coroutine)

    # The coroutine is waiting for all coroutines terminate
    await asyncio.gather(*coroutines)

async def orchestrator(queue, keyFile):
    """
    This coroutine consumes a queue containing the workload.
    When the orchestrator dequeue a load it sends it to the coroutine
    in charge of processing the load.
    """
    while True:
        # Waiting for a workload
        load = queue.get()
        print(load)

        # Workload processing
        await process_load(load, keyFile)
        queue.task_done()

        # break when the queue is empty
        if queue.empty():
            break


def parse_config(yml):
    """
    parse_config takes the config yaml file as argument.
    It processes each load and put them into the queue.
    """
    q = queue.Queue()
    try:
        with open(yml, "r") as f:
            trafgen = yaml.safe_load(f)
        for load in trafgen["loads"]:
            q.put(load)
    except FileNotFoundError as e:
        print(e)
        sys.exit()

    return q

def main(loads_file, keyFile):
    q = parse_config(loads_file)
    loop = asyncio.get_event_loop()

    # call orchestrator with the work load
    loop.run_until_complete(orchestrator(q, keyFile))
    loop.close()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        loads_file = sys.argv[1]
        keyFile = sys.argv[2]
        main(loads_file, keyFile)
    elif len(sys.argv) == 4:
        loads_file = sys.argv[1]
        keyFile = sys.argv[2]
        if "mock" == sys.argv[3]:
            mock = True
        if "wda" == sys.argv[3]:
            wda = True
        main(loads_file, keyFile)

    else:
        main("trafgen.yml", "~/.ssh/id_rsa.pub")