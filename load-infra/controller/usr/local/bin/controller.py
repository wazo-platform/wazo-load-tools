#!/usr/bin/env python3
import asyncio
import yaml
import queue
import paramiko
import sys
from abc import ABC, abstractmethod



class RemoteControl():
    def __init__(self, host, keyFile):
        self.host = host
        self.keyfile = keyFile
        self.channel = None

    def connect(self):
        client = paramiko.SSHClient()
        client.connect(self.host, username='root', pkey=self.keyfile, timeout=5)
        transport = client.get_transport()
        self.channel = transport.open_session()

    def run(self, command):
        #self.channel.exec_command('python script.py > /dev/null 2>&1 &')
        self.channel.exec_command(command)

    def disconnect(self):
        self.channel.close()

from abc import ABC, abstractmethod

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
    def __init__(self, host, container, keyFile):
        self.container = container
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        command = f"docker-compose start {self.container}"
        self.remoteControl.run(command)


class DockerComposeStop(Command):
    """Command used to stop a specific container that belongs to the load farmework."""
    def __init__(self, host, container, keyFile):
        self.container = container
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        command =  f"docker-compose stop {self.container}"
        self.remoteControl.run(command)

class DockerComposeRetart(Command):
    """Command used to restart a specific container that belongs to the load farmework."""
    def __init__(self, host, container, keyFile):
        self.container = container
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        command = f"docker-compose restart {self.container}"
        self.remoteControl.run(command)

class ExecSipLoad(Command):
    """Command used to execute a sip scenario."""
    def __init__(self, host, container, scenario, keyFile):
        self.container = container
        self.scenario = scenario
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        command =  f'docker exec -d {self.container} bash -c "export SCENARIO={self.scenario} /trafgen/load.sh" > /dev/null 2>&1 &'
        self.remoteControl.run(command)

class WsClients(Command):
    """Command used to start websocket clients to subscribe RabbitMQ events"""
    def __init__(self, host, container, keyFile):
        self.container = container
        self.remoteControl = RemoteControl(host, keyFile)

    def connect(self):
        self.remoteControl.connect()

    def disconnect(self):
        self.remoteControl.disconnect()

    def execute(self):
        command =  f'docker exec -d {self.container} bash -c "/usr/local/bin/runner.py" > /dev/null 2>&1 &'
        self.remoteControl.run(command)



async def process_node(node, ttl, channel, keyFile):
    """
    Coroutine that connects, processes end disconnect from the remote host. Connection duration 
    is based on the TTL
    """
    host = node['host']
    container = node['container']
    scenario = node['scenario']
    #config = node.get('config')
    #script = node.get('script')
    #cmd = node.get('cmd')


    msg = "started"
    if container == "callee":
        msg = await channel.get()
    if msg != "started":
        print(f"quitting due to receiving: {msg}")
        return

    # Connection to the remote host 
    cmd = ExecSipLoad(host, container, scenario, keyFile)
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

    # restart the container to end the running tests
    cmd = DockerComposeRetart(host, container, keyFile)
    cmd.connect()
    cmd.execute()
    cmd.disconnect()


async def process_load(load, keyFile):
    """
    Coroutine that processes a workload by creating a process_node coroutine for each node.
    """
    nodes = load['load']
    ttl = load['ttl']
    coroutines = []

    # create a queue that will allow coroutine to send status.
    q = asyncio.Queue()

    # Loop for creating a coroutine for each node in the workload.
    for node in nodes:
        coroutine = asyncio.create_task(process_node(node, ttl, q, keyFile))
        coroutines.append(coroutine)

    # The coroutine is waiting for all coroutines terminate
    await asyncio.gather(*coroutines)

async def orchestrator(queue, keyFile):
    """
    This coroutine consumes a queue containing the workload
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
    if len(sys.argv) == 2:
        loads_file = sys.argv[1]
        keyFile = sys.argv[2]
        main(loads_file, keyFile)
    else:
        main("trafgen.yml", "~/.ssh/id_rsa.pub")