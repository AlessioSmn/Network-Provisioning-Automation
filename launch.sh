#/bin/bash

# bridge creation
./br.sh
echo "[1] Bridge created"

# creating all startup-config
for file in template/data/*.yaml; do
    python3 template/generator.py "$file"
done
echo "[2] Startup-config files created"

# launch emulated network
echo "[3] Destroying network"
sudo containerlab destroy

echo "[4] Deploying network"
sudo containerlab deploy
