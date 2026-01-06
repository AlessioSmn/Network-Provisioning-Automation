#!/bin/bash

# Function to get IP addresses and default gateways
get_mgmt_info() {
  mgmt_ipv4_addr=$(ip -4 addr show eth0 | grep inet | awk '{print $2}')
  mgmt_default_ipv4_nh=$(ip route | grep '^default' | awk '{print $3}')
  mgmt_ipv6_addr=$(ip -6 addr show | grep -E '^\s*inet6.*global' | awk '{print $2}')
  mgmt_default_ipv6_nh=$(ip -6 route | grep '^default' | awk '{print $3}')
}

# Function to configure VRF
configure_vrf() {
  sysctl -w net.ipv6.conf.all.keep_addr_on_down=1
  ip link add ${CLAB_MGMT_VRF} type vrf table 1
  ip link set dev ${CLAB_MGMT_VRF} up
  ip link set dev eth0 master ${CLAB_MGMT_VRF}
}

# Function to configure FRR
configure_frr() {
  vtysh << EOF
configure terminal
interface eth0
ip address ${mgmt_ipv4_addr}
exit
write
EOF
}

# ================ Main script execution

echo "======= FRR initialization ======="
/usr/lib/frr/frrinit.sh start

# echo "======= Get management info ======="
# get_mgmt_info

echo "======= Install SSH Server ======="
apk add openssh

echo "======= SSH Key generation ======="
ssh-keygen -A
echo "root:admin" | chpasswd

echo "======= Start SSH ======="
sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
/usr/sbin/sshd

# echo "======= Management interface config ======="
# configure_frr

echo "======= END ======="
