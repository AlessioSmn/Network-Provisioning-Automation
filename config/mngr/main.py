import json
import time
import paramiko

USERNAME = "root"
PASSWORD = "admin"
INTERVAL = 60

MY_AS = 65020

PE1_IP = "192.168.100.11"
PE2_IP = "192.168.100.12"
GW1_IP = "192.168.100.21"
GW2_IP = "192.168.100.22"

lo_ip_map = {
    PE1_IP : "192.168.0.1",
    PE2_IP : "192.168.0.2",
    GW1_IP : "192.168.0.3",
    GW2_IP : "192.168.0.4"
}

UP1_IP = "172.16.0.2"
UP2_IP = "172.16.1.2"
UP1_AS = 65541
UP2_AS = 65542

ALL_PEERS = [PE1_IP, PE2_IP, GW1_IP, GW2_IP]

CU1_NET = "192.0.2.0/24"
CU2_NET = "192.51.100.0/24"

with open("traffic-matrices.json", "r") as f:
    traffic_matrices = json.load(f)

matrix_index = 0

def configure_bgp_params(gw_ip, route_outbound_map_name, route_inbound_map_name, bucket, other_gw, other_inbound_map_name):
    my_up = UP1_IP if gw_ip == GW1_IP else UP2_IP
    other_up = UP2_IP if gw_ip == GW1_IP else UP1_IP
    my_up_as = UP1_AS if gw_ip == GW1_IP else UP2_AS
    other_up_as = UP2_AS if gw_ip == GW1_IP else UP1_AS

    cmds = ['configure terminal']

    seq = 10

    if not bucket:
        return

    for entry in bucket:
        prefix = entry
        pl_name = f'PL-{prefix.replace("/", "_")}'
        cmds.append(f'ip prefix-list {pl_name} permit {prefix}')

        if(entry == CU1_NET or entry == CU2_NET):
            cmds.append(f'route-map {route_inbound_map_name} permit {seq}')
        else:
            cmds.append(f'route-map {route_outbound_map_name} permit {seq}')
        
        cmds.append(f' match ip address prefix-list {pl_name}')

        if(entry == CU1_NET or entry == CU2_NET):
            cmds.append(f' set metric 50')
        else:
            cmds.append(f' set local-preference 200')

        seq += 10

    cmds.append(f'route-map {route_outbound_map_name} permit 999')

    for peer_ip in ALL_PEERS:
        if peer_ip != gw_ip: 
            cmds.append(f'router bgp {MY_AS}')
            cmds.append(f' neighbor {peer_ip} remote-as {MY_AS}')
            cmds.append(f' neighbor {peer_ip} route-map {route_inbound_map_name} out')

    cmds.append(f' neighbor {my_up} remote-as {my_up_as}')
    cmds.append(f' neighbor {my_up} route-map {route_outbound_map_name} in')

    cmds.append('end')

    vtysh_cmd = "vtysh \\\n" + " \\\n".join([f'    -c "{c}"' for c in cmds])

    print(f"Executing the following command in GW {gw_ip}:")
    print(vtysh_cmd)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(lo_ip_map[gw_ip], username=USERNAME, password=PASSWORD)
    stdin, stdout, stderr = ssh.exec_command(vtysh_cmd)

    for peer_ip in ALL_PEERS:
        if peer_ip != gw_ip:
            cmd = f"vtysh -c 'clear ip bgp {peer_ip} soft in'"
            print(cmd)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.channel.recv_exit_status()
            out = stdout.read().decode()
            err = stderr.read().decode()
            if out:
                print(f"[{peer_ip}] OUT: {out}")
            if err:
                print(f"[{peer_ip}] ERR: {err}")

    print(f"=== Output from {gw_ip} ===")
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh.close()

    cmds = ['configure terminal']

    seq = 10

    # necessario settare un valore di MED più altro (default 0) anche sull'altro gateway

    for entry in bucket:
        prefix = entry
        pl_name = f'PL-{prefix.replace("/", "_")}'
        cmds.append(f'ip prefix-list {pl_name} permit {prefix}')

        if(not(entry == CU1_NET or entry == CU2_NET)):
            continue
            
        cmds.append(f'route-map {other_inbound_map_name} permit {seq}')
        
        cmds.append(f' match ip address prefix-list {pl_name}')
            
        cmds.append(f' set metric 100')

        seq += 10

    cmds.append(f'route-map {other_inbound_map_name} permit 999')
    
    cmds.append(f'router bgp {MY_AS}')

    cmds.append(f' neighbor {other_up} remote-as {other_up_as}')
    cmds.append(f' neighbor {other_up} route-map {other_inbound_map_name} out')

    for peer_ip in ALL_PEERS:
        if peer_ip != other_gw: 
            cmds.append(f'router bgp {MY_AS}')
            cmds.append(f' neighbor {peer_ip} remote-as {MY_AS}')
            cmds.append(f' neighbor {peer_ip} route-map {other_inbound_map_name} out')

    cmds.append('end')

    vtysh_cmd = "vtysh \\\n" + " \\\n".join([f'    -c "{c}"' for c in cmds])

    print(f"Executing the following command in GW {other_gw}:")
    print(vtysh_cmd)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(lo_ip_map[other_gw], username=USERNAME, password=PASSWORD)
    stdin, stdout, stderr = ssh.exec_command(vtysh_cmd)

    print(f"=== Output from {other_gw} ===")
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh.close()

time.sleep(30)
while True:

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
        route_outbound_map_name='SET-LP-GW1',
        route_inbound_map_name='SET-MED-GW1',
        bucket=bucket1,
        other_gw=GW2_IP,
        other_inbound_map_name='SET-MED-GW2'
    )

    # bucket2 → GW2 (UP2)
    configure_bgp_params(
        gw_ip=GW2_IP,
        route_outbound_map_name='SET-LP-GW2',
        route_inbound_map_name='SET-MED-GW2',
        bucket=bucket2,
        other_gw=GW1_IP,
        other_inbound_map_name='SET-MED-GW1'
    )

    matrix_index = (matrix_index + 1) % len(traffic_matrices)
    time.sleep(3000)
