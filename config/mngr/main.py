import json
import time
import paramiko
import re

USERNAME = "root"
PASSWORD = "admin"

# matrices are read with a defer of
INTERVAL = 180

MY_AS = 65020

PE1_IP = "192.168.100.11"
PE2_IP = "192.168.100.12"
GW1_IP = "192.168.100.21"
GW2_IP = "192.168.100.22"

# {lo_ip -> core_ip} this map is important, since mngr-node doesnt know about lo_ip
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
CU2_NET = "198.51.100.0/24"

# launch clear ip bgp cmd for desiderated peer inside ssh client specified
def clear_bgp(peer_ip, ssh):
    cmd = f"vtysh -c 'clear ip bgp {peer_ip} soft in' -c 'clear ip bgp {peer_ip} soft out'"
    print(cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(f"[{peer_ip}] OUT: {out}")
    if err:
        print(f"[{peer_ip}] ERR: {err}")


def configure_filtering(gw_ip, route_inbound_map_name, bucket):
    my_up = UP1_IP if gw_ip == GW1_IP else UP2_IP
    my_up_as = UP1_AS if gw_ip == GW1_IP else UP2_AS
    
    cmds = ['configure terminal']

    seq = 10

    for entry in bucket:
        # to internet route, not interesting here
        if not (entry == CU1_NET or entry == CU2_NET):
            continue

        # buiding filter using route map
        
        prefix = entry
        pl_name = f'PL-{prefix.replace("/", "_")}'
        
        cmds.append(f'ip prefix-list {pl_name} permit {prefix}')
            
        cmds.append(f'route-map {route_inbound_map_name} deny {seq}')
        
        cmds.append(f' match ip address prefix-list {pl_name}')

        seq += 10
    
    # catch-all route map
    cmds.append(f'route-map {route_inbound_map_name} permit 999')

    # appling the route map
    cmds.append(f'router bgp {MY_AS}')
    cmds.append(f' neighbor {my_up} remote-as {my_up_as}')
    cmds.append(f' neighbor {my_up} route-map {route_inbound_map_name} out')
    cmds.append('end')

    vtysh_cmd = "vtysh \\\n" + " \\\n".join([f'    -c "{c}"' for c in cmds])

    print(f"Executing the following command in GW {gw_ip}:")
    print(vtysh_cmd)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(lo_ip_map[gw_ip], username=USERNAME, password=PASSWORD)
    stdin, stdout, stderr = ssh.exec_command(vtysh_cmd)

    # refresh bgp updates
    for peer_ip in ALL_PEERS:
        if peer_ip != gw_ip:
            clear_bgp(peer_ip=peer_ip, ssh=ssh)

    clear_bgp(peer_ip=my_up, ssh=ssh)

    print(f"=== Output from {gw_ip} ===")
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh.close()


def configure_bgp_local_pref(gw_ip, route_outbound_map_name, bucket):
    # finds which my up is
    my_up = UP1_IP if gw_ip == GW1_IP else UP2_IP
    my_up_as = UP1_AS if gw_ip == GW1_IP else UP2_AS

    cmds = ['configure terminal']

    seq = 10

    for entry in bucket:
        # from internet route, not interesting here
        if(entry == CU1_NET or entry == CU2_NET):
            continue
        
        prefix = entry
        pl_name = f'PL-{prefix.replace("/", "_")}'
        
        # buiding preference using route map

        cmds.append(f'ip prefix-list {pl_name} permit {prefix}')
            
        cmds.append(f'route-map {route_outbound_map_name} permit {seq}')
        
        cmds.append(f' match ip address prefix-list {pl_name}')

        cmds.append(f' set local-preference 200')

        seq += 10

    # catch all preference
    cmds.append(f'route-map {route_outbound_map_name} permit 999')

    # appling the route map
    cmds.append(f'router bgp {MY_AS}')
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

    # refresh bgp updates
    for peer_ip in ALL_PEERS:
        if peer_ip != gw_ip:
            clear_bgp(peer_ip=peer_ip, ssh=ssh)

    clear_bgp(peer_ip=my_up, ssh=ssh)

    print(f"=== Output from {gw_ip} ===")
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh.close()

def remove_all_route_maps(ip):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(lo_ip_map[ip], username=USERNAME, password=PASSWORD)

        cmd = "vtysh -c 'show route-map'"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()

        route_maps = set(
            re.findall(r"^route-map:\s+(\S+)", output, re.MULTILINE)
        )

        if not route_maps:
            print(f'No route maps in {ip}')
            return

        cmds = ['configure terminal']

        for rm in route_maps:
            cmds.append(f"no route-map {rm}")

        cmds.append("end")

        vtysh_cmd = "vtysh \\\n" + " \\\n".join([f'    -c "{c}"' for c in cmds])
        stdin, stdout, stderr = ssh.exec_command(vtysh_cmd)

        print(f"Removed route-maps: {', '.join(route_maps)}")

    finally:
        ssh.close()


with open("traffic-matrices.json", "r") as f:
    traffic_matrices = json.load(f)

matrix_index = 0

# sleep 30s to ensure network fully operation (a regime)
time.sleep(30)

iter = 1

while True:

    current_matrix = traffic_matrices[matrix_index]
    
    """
    (Remember each entry of the traffic matrices provides the expeteced-traffic from a net_i to a net_j)

    The greedy alghoritm exploits 2 buckets to determine the best traffic distribution across upstream links. In particular, it works like this:
        1. retrieve a route
        2. between the 2 buckets, the one with the less amount of expected-traffic is selcted
        3. the route is inserted in the bucket and the total amount of traffic of the bucket is added with this route one's
        4. if there are still other routes -> goto point-1, otherwise end

    At the end, bucket1 will be used to determine which routes must have a 200 local-pref in GW1 (to-internet routes) and which routes must be filtered in 
        GW2 (from-internet routes). The opposite goes for bucket2.

    Extra: suppose we store a route from CU1 to internet and then a route from CU2 to internet, 
        -> the route from CU2 to internet must be served from the same GW of the previous one.
        It's not possible to have GW1 serving (CU1 -> net) and GW2 (CU2 -> net) (unless using other techniques such as traffic engineering or segment routing)
        This means that routes with the same destination must go into the same bucket.
    """

    print(f"\n##########################################\nCONFIGURING BGP PARAMETERS ITER {iter}\n##########################################\n")
    
    bucket_gw1 = []
    bucket_gw2 = []
    total1 = 0
    total2 = 0

    assigned_destinations = set()

    for entry in current_matrix:
        dst = entry["to"]
        traffic = entry["expected-traffic"]

        if dst in assigned_destinations:
            if dst in bucket_gw1:
                total1 += traffic
            else:
                total2 += traffic
        else:
            if total1 <= total2:
                total1 += traffic
                bucket_gw1.append(dst)
            else:
                total2 += traffic
                bucket_gw2.append(dst)
            
            assigned_destinations.add(dst)

    print(f"Bucket1: {bucket_gw1}, total1: {total1}")
    print(f"Bucket2: {bucket_gw2}, total2: {total2}")

    # bucket1 is used to set local-pref in GW1
    configure_bgp_local_pref(
        gw_ip=GW1_IP,
        route_outbound_map_name='SET-LP-GW1',
        bucket=bucket_gw1
    )

    # bucket2 is used to set local-pref in GW2
    configure_bgp_local_pref(
        gw_ip=GW2_IP,
        route_outbound_map_name='SET-LP-GW2',
        bucket=bucket_gw2
    )

    # bucket2 is used to impose filters in GW1 
    configure_filtering(
        gw_ip=GW1_IP,
        route_inbound_map_name='SET-FILTERING-GW1',
        bucket=bucket_gw2
    )

    # bucket1 is used to impose filters in GW2
    configure_filtering(
        gw_ip=GW2_IP,
        route_inbound_map_name='SET-FILTERING-GW2',
        bucket=bucket_gw1
    )

    matrix_index = (matrix_index + 1) % len(traffic_matrices)
    time.sleep(INTERVAL)
    remove_all_route_maps(GW1_IP)
    remove_all_route_maps(GW2_IP)   

    iter += 1
