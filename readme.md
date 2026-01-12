# Network Provisioning and Automation
Group project for Advanced Computer Networking course, MSc in Computer Engineering, Università di Pisa, A.Y. 2025/2026

## TODO
 - Decidere cosa fare della rete di management:
    - Decidere se lasciarla nella vrf deafult o in una separata (usare env: CLAB_VRF_MGMT come nell'esercizio del Virdis)
        - Sarebbe meglio metterla in VRF separate secondo me MA non so se poi con SSH si comanda comunque tutto (credo di si ma è da controllare comunque)
    - Quantomeno togliere la default route che va sulla management

 - Ho messo ip route replace negli Alpine (per la default route), perchè ip route add fa conflitto (anche su nodo appena creato). Direi che è sufficiente dirlo nella documentazione, replace fa semplicemenete add se non c'è niente, altrimenti fa flush+add
 - **TASK 3**
   - decidere come implemetare la matrice di traffico: semplice file direi che può andar bene
   - algoritmo che da matrice di traffico restituisce i percorsi scelti 
        - es: per 203.0.133.0/24 usare uscita GW2
        - es: per 192.0.100.0/24 usare uscita PE2 (obbligato), pubblicare in uscita solo a GW1
   - installare le regole nei quattro router dell'AS centrale via SSH
   - testare bene se è tutto funzionante correttamente
 
## Description
Network to implement:
![Base structure](./img/project-base.jpg)
Chosen configuration:
![Network structure](./img/project.jpg)

## Repository structure
Compact:
```
.
├───config
│   ├───frr
│   ├───alpine
│   ├───mngr
│   └───startup
├───doc
├───img
└───template
    └───data
```
Extended:
```
.
│   acn.clab.yml
│   br.sh
│   clean.sh
│   launch.sh
│   controller.py
│   readme.md
│
├───config
│   │   linux-host-cfg.sh
│   │
│   ├───alpine
│   │       alp-cfg.sh
│   │
│   ├───frr
│   │       daemons
│   │       frr-cfg.sh
│   │       vtysh.conf
│   │
│   ├───mngr
│   │       main.py
│   │
│   └───startup
│           *.conf
│           *.sh
│
├───doc
│       ACN Project description.pdf
│
├───img
│       *.drawio
│       *.png
│       *.jpg
│
└───template
    │   generator.py
    │   requirements.txt
    │   template_alp.j2
    │   template_frr.j2
    │
    └───data
            *.yaml
```

## Project deployment

The entire project can be deployed by launching the dedicated script `launch.sh`:
```bash
./launch.sh
```
Options available for the launch script:
```bash
> ./launch.sh -h
Usage: ./launch.sh [OPTIONS]

Options (no arguments required):
  -i, --images      Build images (default: NO)
  -c, --clean       Clean previous launch (default: NO)
  -b, --bridge      Create bridges (default: NO)
  -t, --template    Compile templates (default: NO)
  -h, --help        Show this help message and exit
```

The network can be destoryed by launching the dedicated script `clean.sh`:
```bash
./shell/clean.sh
```
In the following part we describe the steps carried in the launch script.
### Build images
 - Via the provided script: `./shell/images.sh`.
 - Manually:
    1. Create image for FRR node (it must contain OpenSSH package to allow ssh access) It runs the following command:
        ```bash
        docker build -t frr-ssh:10.4.1 ./config/frr
        ```
    2. Create image for manager node (it must contain paramiko package to allow programmatic ssh). It runs the following command:
        ```bash
        docker build -t manager-img ./config/mngr
        ```
Note that `frr-ssh:10.4.1` and `manager-img` are the name of the images used in `acn.clab.yml`
### Create bridges
  - Via the provided script `./shell/bridge.sh`
  - Manually:
    ```bash
    sudo ip link add br-clab-core type bridge
    sudo ip link set br-clab-core up

    sudo ip link add br-clab-int type bridge
    sudo ip link set br-clab-int up
    ```
Note that `br-clab-core` and `br-clab-int` are the name of the bridges used in `acn.clab.yml`

### Deploy
Deploy the network with containerlab
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
Then open one of the proposed addresses with a browser

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
- Access node (alternatives):
    ```bash
    docker exec -it <node-name> sh
    ```
    ```bash
    docker exec -it <node-name> vtysh
    ```
    ```bash
    ssh root@<node-mgmt-address>
    (password)> admin 
    ```
- Exit shell:
    ```bash
    exit
    ```

#### Useful commands
 - Interfaces
    - Show all available commands: `Node# show interface ?`
    - Show brief summary: `Node# show interface brief`
    - Show interfaces description: `Node# show interface description`
 - IP
    - Show all available commands: `Node# show ip ?`
    - Show routing table: `Node# show ip route`
    - Show BGP entries: `Node# show ip bgp`
    - Show OSPF entries: `Node# show ip ospf`
 - BGP
    - Show all available commands: `Node# show bgp ?`
    - Show brief summary: `Node# show bgp summary`
    - Show neighbors in detail: `Node# show bgp neighbors`

### Alpine nodes
- Access node
    ```bash
    docker exec -it <node-name> sh
    ```
    ```bash
    ssh root@<node-mgmt-address>
    (password)> admin 
    ```
- Exit shell:
 `ctrl`+`p`+`q`

#### Useful commands
- Show interfaces:
    - Full:  `/ # ip [addr | address]`
    - Specific:  `/ # ip [addr | address] show dev <interface name>`
