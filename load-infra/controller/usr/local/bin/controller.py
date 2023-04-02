#!/usr/bin/env python3
import asyncio
import yaml
import queue
import paramiko
import sys


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



async def process_node(node, ttl, channel):
    """
    Coroutine that connects, processes end disconnect from the remote host. Connection duration 
    is based on the TTL
    """
    host = node['host']
    container = node['container']
    #scenario = node['scenario']
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
    # ...

    # Execute instruction to the remote host
    # ...
    if container == "caller":
        await channel.put("started")
        print("sent: started")


    # Await on the TTL
    await asyncio.sleep(ttl)

    # Disconnect from the remote host
    # ...
    # test by printing
    print(f"=============== {host}")

async def process_load(load):
    """
    Coroutine that processes a work load by creating a process_node coroutine for each node.
    """
    nodes = load['load']
    ttl = load['ttl']
    coroutines = []

    # create a queue that will allow coroutine to send status.
    q = asyncio.Queue()

    # Loop for creating a coroutine for each node in the workload.
    for node in nodes:
        coroutine = asyncio.create_task(process_node(node, ttl, q))
        coroutines.append(coroutine)

    # The coroutine is waiting for all coroutines terminate
    await asyncio.gather(*coroutines)

async def orchestrator(queue):
    """
    This coroutine consumes a queue containing the workload
    """
    while True:
        # Waiting for a workload
        load = queue.get()
        print(load)

        # Workload processing
        await process_load(load)
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

def main(loads_file):
    q = parse_config(loads_file)
    loop = asyncio.get_event_loop()

    # call orchestrator with the work load
    loop.run_until_complete(orchestrator(q))
    loop.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        loads_file = sys.argv[1]
        main(loads_file)
    else:
        main("trafgen.yml")