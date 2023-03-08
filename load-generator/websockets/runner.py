#!/usr/bin/env python3
import csv
import os
import subprocess
import sys

def run(script, host, user, passwd):
    try:
        return  subprocess.check_output([sys.executable, script], shell=True,
                                env={
                                        "HOST_IP":host,
                                        "AUTH_USER":user,
                                        "AUTH_PASSWD":passwd
                                    }, 
                                stderr=subprocess.PIPE).decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        raise ValueError(
            f"Error running {cmd}. stdout: '{e.stdout}'. stderr: '{e.stderr}'")

def process_accounts(accounts):
    with open(accounts, "r") as f:
        for account in csv.reader(f, delimiter=';'):
            yield account[0], account[1]
        

if __name__ == "__main__":
    host = os.getenv("HOST_IP", "http://localhost:8000")
    path = os.getenv("USERS_FILE", "/users.csv")
    if not os.path.exists(path):
        sys.exit(f"{path} is missing")
    
    for user, passwd in process_accounts(path):
        print(f"{user} {passwd}")
        run("/usr/local/bin/ws-client.py",host, user, passwd)
