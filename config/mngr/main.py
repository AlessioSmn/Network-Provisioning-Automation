import os
import sys
import time
import paramiko

# Print version
print(f"Python is active. Version: {sys.version}")

ROUTER_IP = "192.168.0.1"
USERNAME = "root"
PASSWORD = "admin"
INTERVAL = 100

def set_hostname(hostname):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
        hostname=ROUTER_IP,
        username=USERNAME,
        password=PASSWORD,
        look_for_keys=False,
        allow_agent=False
    )

    cmd = 'vtysh -c "configure terminal" -c "ip route 1.2.3.4/32 null0" -c "end"'

    stdin, stdout, stderr = client.exec_command(cmd)

    out = stdout.read().decode()
    err = stderr.read().decode()

    if out:
        print(out)
    if err:
        print(err)

    client.close()

i = 0
while True:
    time.sleep(INTERVAL)
    hostname = f"router-loop-{i % 2}"
    print(f"[+] Setting hostname to: {hostname}")
    set_hostname(hostname)
    i += 1
