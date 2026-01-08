#!/bin/bash

# ================ Main script execution

echo "======= FRR initialization ======="

# watchfrr is automatically started
# /usr/lib/frr/frrinit.sh start

# Sleep to let daemons be up
sleep 5

# Configuration is automatically loaded:
# vtysh -f /etc/frr/frr.conf

echo "======= Save Config ======="
write file

echo "======= Install SSH Server ======="
apk add openssh

echo "======= SSH Key generation ======="
ssh-keygen -A
echo "root:admin" | chpasswd

echo "======= Start SSH ======="
sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
/usr/sbin/sshd

echo "======= END ======="
