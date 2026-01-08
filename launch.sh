#/bin/bash

# bridge creation
echo -n
echo "========= (1) - Bridge creation ========="
./br.sh

# creating all startup-config
echo -n
echo "========= (2) - Startup-config files ========="
for file in template/data/*.yaml; do
    python3 template/generator.py "$file"
done

# Make sh executable
echo -n
echo "========= (3) - Chmod ========="
for shfile in config/startup/*.sh; do
    chmod +x "$shfile"
    echo File "$shfile" is executable
done

# Clear previous intance
echo -n
echo "========= (4) - CLAB Destory ========="
sudo containerlab destroy --cleanup -t acn.clab.yml

# Print container possibly left out
docker ps -a | grep acn-prj | awk '{print $1}' | xargs -r docker rm -f
docker volume ls | grep acn-prj | awk '{print $2}' | xargs -r docker volume rm
ip netns | grep clab
ip netns | grep acn-prj

# launch emulated network
echo -n
echo "========= (4) - CLAB Deploy ========="
sudo containerlab deploy -t acn.clab.yml
