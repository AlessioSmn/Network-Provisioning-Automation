# Network Provisioning and Automation
Group project for Advanced Computer Networking course, MSc in Computer Engineering, Università di Pisa, A.Y. 2025/2026

## Description
TODO
![Base structure](./img/project-base.jpg)

## Repository structure
```
.
├───config
│   ├───frr
│   └───startup
├───doc
└───img
```


## Project deployment
### Deploy
 - Create bridges  

Note that `br-clab-core` and `br-clab-int` are the name of the bridges used in `acn.clab.yml`
```bash
sudo ip link add br-clab-core type bridge
sudo ip link set br-clab-core up

sudo ip link add br-clab-int type bridge
sudo ip link set br-clab-int up
```
 - Deploy the network with containerlab
```bash
sudo containerlab deploy [-t acn.clab.yml]
```

#### Redeploy
```bash
sudo containerlab redeploy [-t acn.clab.yml]
```

### Show topology
```bash
sudo containerlab graph [--topo -t acn.clab.yml]
```

### Destroy
```bash
sudo containerlab destroy [-t acn.clab.yml]
```
To check if all containers have been destroyed:
```bash
docker ps -a
```
To manually destory containers:
```bash
sudo docker rm -f <container-id>
```

## Containers usage
### FRR nodes
- Access node
    ```bash
    docker exec -it <node-name> vtysh
    ```
- Exit shell:
    ```bash
    exit
    ```
- Show interfaces:
    - Full:  `Node# show [i | int | interfaces]`
    - Brief:  `Node# show [int | interfaces] [b | brief]`
    - Specific:  `Node# show [int | interfaces] <interface name>`

### Alpine nodes
- Access node
    ```bash
    docker exec -it <node-name> sh
    ```
- Exit shell:
 `ctrl`+`p`+`q`
- Show interfaces:
    - Full:  `/ # ip [addr | address]`
    - Specific:  `/ # ip [addr | address] show dev <interface name>`