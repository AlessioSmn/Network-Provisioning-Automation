for i in $(seq 1 16); do
    ip link add lo$i type dummy
    ip link set lo$i up
done