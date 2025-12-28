#!/bin/bash

BR_CORE='br-clab-core'
BR_INT='br-clab-int'

sudo ip link add $BR_CORE type bridge
sudo ip link set $BR_CORE up

sudo ip link add $BR_INT type bridge
sudo ip link set $BR_INT up