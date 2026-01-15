import json
import time
import paramiko

USERNAME = "root"
PASSWORD = "admin"
INTERVAL = 60

PE1_IP = "192.168.0.1"
PE2_IP = "192.168.0.2"
GW1_IP = "192.168.0.3"
GW2_IP = "192.168.0.4"

ALL_PEERS = [PE1_IP, PE2_IP, GW1_IP, GW2_IP]

CU1_NET = "192.0.2.0/24"
CU2_NET = "192.51.100.0/24"

with open("traffic-matrices.json", "r") as f:
    traffic_matrices = json.load(f)

matrix_index = 0

def configure_bgp_params(gw_ip, route_map_name, bucket):
    cmds = ['configure terminal']

    seq = 10

    if not bucket:
        return

    for entry in bucket:
        prefix = entry
        pl_name = f'PL-{prefix.replace("/", "_")}'
        cmds.append(f'ip prefix-list {pl_name} permit {prefix}')
        cmds.append(f'route-map {route_map_name} permit {seq}')
        cmds.append(f' match ip address prefix-list {pl_name}')
        cmds.append(f' set local-preference 200')
        seq += 10

    for peer_ip in ALL_PEERS:
        if peer_ip != gw_ip: 
            cmds.append(f'router bgp 65020')
            cmds.append(f' neighbor {peer_ip} route-map {route_map_name} out')

    cmds.append('end')

    vtysh_cmd = 'vtysh ' + ' '.join([f'-c "{c}"' for c in cmds])

    print(f"Executing the following command in GW {gw_ip}:")
    print(vtysh_cmd)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(gw_ip, username=USERNAME, password=PASSWORD)
    stdin, stdout, stderr = ssh.exec_command(vtysh_cmd)

    print(f"=== Output from {gw_ip} ===")
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh.close()

while True:
    time.sleep(INTERVAL)

    current_matrix = traffic_matrices[matrix_index]
    
    bucket1 = []
    bucket2 = []
    total1 = 0
    total2 = 0

    assigned_destinations = set()

    print(f"Retrieving traffic matrix:")
    for entry in current_matrix:
        dst = entry["to"]
        traffic = entry["expected-traffic"]

        print(f"{entry['from']} -> {dst} : {traffic}")

        if dst in assigned_destinations:
            if dst in bucket1:
                total1 += traffic
            else:
                total2 += traffic
        else:
            if total1 <= total2:
                total1 += traffic
                bucket1.append(dst)
            else:
                total2 += traffic
                bucket2.append(dst)
            
            assigned_destinations.add(dst)

    print(f"Bucket1: {bucket1}, total1: {total1}")
    print(f"Bucket2: {bucket2}, total2: {total2}")

    # bucket1 → GW1 (UP1)
    configure_bgp_params(
        gw_ip=GW1_IP,
        route_map_name='SET-LP-UP1',
        bucket=bucket1
    )

    # bucket2 → GW2 (UP2)
    configure_bgp_params(
        gw_ip=GW2_IP,
        route_map_name='SET-LP-UP2',
        bucket=bucket2
    )

    matrix_index = (matrix_index + 1) % len(traffic_matrices)
    time.sleep(INTERVAL)
