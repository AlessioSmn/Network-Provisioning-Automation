#!/bin/bash

echo -n
echo "Building FRR-SSH image"
docker build -t frr-ssh:10.4.1 ./config/frr

echo -n
echo "Building manager image"
docker build -t manager-img ./config/mngr