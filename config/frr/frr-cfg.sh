#!/bin/bash

# ================ Main script execution

echo "=-=-=-= FRR initialization =-=-=-="

echo "======= Install SSH Server ======="
apk add openssh

echo "======= SSH Key generation ======="
ssh-keygen -A
echo "root:admin" | chpasswd

# VRF Management (if specified)
if [ -n "${CLAB_MGMT_VRF}" ]; then
    # NOTE: uncomment to see if default route will disappeared from default vrf route
    # ip route

    echo "======= VRF Management ======="
    ip link add "${CLAB_MGMT_VRF}" type vrf table 100
    ip link set "${CLAB_MGMT_VRF}" up
    echo "vrf ${CLAB_MGMT_VRF} created and set up"

    ip link set eth0 master "${CLAB_MGMT_VRF}"
    echo "eth0 assigned to vrf ${CLAB_MGMT_VRF}"

    ip route add default via ${CLAB_MGMT_GW} vrf "${CLAB_MGMT_VRF}"
    echo "default route via vrf ${CLAB_MGMT_VRF} (GW ${CLAB_MGMT_GW})"

    # NOTE: uncomment to see if default route has disappeared from default vrf route
    # ip route
fi

# Sleep to let daemons be up
sleep 10

echo "======= Start SSH ======="
VRF_EXEC=""
if [ -n "${CLAB_MGMT_VRF}" ]; then
    VRF_NAME="${CLAB_MGMT_VRF}"
    VRF_EXEC="ip vrf exec ${VRF_NAME}"
fi
$VRF_EXEC sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
$VRF_EXEC /usr/sbin/sshd


echo "======= Save Config ======="
write file

echo "=-=-=-= END =-=-=-="

# NOTE

# watchfrr is automatically started
# /usr/lib/frr/frrinit.sh start

# Configuration is automatically loaded:
# vtysh -f /etc/frr/frr.conf
