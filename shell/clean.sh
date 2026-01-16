#bin/bash

sudo containerlab destroy --cleanup -t acn.clab.yml

# Removing hostkey from known hosts 
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.101'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.102'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.121'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.122'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.111'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.112'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.131'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.132'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.201'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.202'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.203'
ssh-keygen -f '/home/lorenzo/.ssh/known_hosts' -R '10.255.255.205'

# Print container possibly left out
docker ps -a | grep acn-prj | awk '{print $1}' | xargs -r docker rm -f
docker volume ls | grep acn-prj | awk '{print $2}' | xargs -r docker volume rm
ip netns | grep clab
ip netns | grep acn-prj