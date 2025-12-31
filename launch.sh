#!/bin/bash

# bridge creation
./br.sh

# creating all startup-config
for file in template/data/*.yaml; do
    python3 template/generator.py "$file"
done

# launch emulated network
sudo containerlab deploy