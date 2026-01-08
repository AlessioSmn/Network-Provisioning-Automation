import os
import sys
import socket
import argparse
import paramiko

NODE_IP_MAP = {
    "n1": "10.255.255.201",
    "n2": "10.255.255.202",
    "n3": "10.255.255.203",

    "mngr": "10.255.255.205",

    "CE1": "10.255.255.101",
    "CE2": "10.255.255.102",

    "PE1": "10.255.255.111",
    "PE2": "10.255.255.112",
    "GW1": "10.255.255.121",
    "GW2": "10.255.255.122",
    
    "UP1": "10.255.255.131",
    "UP2": "10.255.255.132",
}

USERNAME = "root"
PASSWORD = "admin"

CMD_MAP = {
    "bgp sum": "vtysh -c 'show bgp summary'",
    "bgp det": "vtysh -c 'show bgp summary'",
    "int bri": "vtysh -c 'show int brief'",
    "int desc": "vtysh -c 'show int description'",
    "ip route": "vtysh -c 'show ip route'",
}

def run_cmd(host, cmd, timeout=10):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            username=USERNAME,
            password=PASSWORD,
            timeout=timeout,
            banner_timeout=timeout,
            auth_timeout=timeout,
        )
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode(errors="ignore")
        err = stderr.read().decode(errors="ignore")
        return out.strip(), err.strip()
    finally:
        client.close()

def exec_cmd(cmd, targets):
    for name, ip in targets.items():
        try:
            out, err = run_cmd(ip, cmd)
            if out:
                print(f"\n=== {name} ({ip}) ===")
                print(out)
            if err:
                print(f"\n=== {name} ({ip}) === [stderr]")
        except (paramiko.SSHException, socket.error) as e:
            print(f"{name} ({ip}) ERROR: {e}")

def parse_targets(node):
    if node:
        if node not in NODE_IP_MAP:
            print(f"Node not valid: {node}")
            return None
        return {node: NODE_IP_MAP[node]}
    return NODE_IP_MAP

def main():
    # Handle parameters
    parser = argparse.ArgumentParser(description="Network controller")
    
    # Aggiunta dei flag richiesti
    # -n richiede un numero (int), -s richiede una stringa
    parser.add_argument("-n", "--number", type=int, help="TODO Descrizione per il parametro numero")
    parser.add_argument("-s", "--settings", type=str, help="TODO Descrizione per il parametro settings")

    args = parser.parse_args()

    # Esempio di utilizzo dei parametri iniziali
    if args.number:
        print(f"Parametro 'number' ricevuto: {args.number}")
    if args.settings:
        print(f"Parametro 'settings' ricevuto: {args.settings}")

    print("-" * 30)

    # Main loop
    while True:
        print("\nAvailable commands:")
        for k in CMD_MAP:
            print(f"  {k} [node]")
        print("  custom <cmd> [node]")
        print("  exit")


        raw = input("CMD > ").strip()
        if not raw:
            continue

        if raw == "exit":
            break

        parts = raw.split()
        node = None
        cmd = None

        if parts[0] == "custom":
            if len(parts) < 2:
                print("custom <cmd> [node]")
                continue
            node = parts[-1] if parts[-1] in NODE_IP_MAP else None
            cmd = " ".join(parts[1:-1] if node else parts[1:])
        else:
            key = " ".join(parts[:2])
            node = parts[2] if len(parts) == 3 else None
            cmd = CMD_MAP.get(key)

            if not cmd:
                print("Comando non valido")
                continue

        targets = parse_targets(node)
        if targets:
            exec_cmd(cmd, targets)


if __name__ == "__main__":
    main()