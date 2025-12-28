# Network Provisioning and Automation
Group project for Advanced Computer Networking course, MSc in Computer Engineering, Università di Pisa, A.Y. 2025/2026

## TODO
 - Fare uno script che banalmente lancia `python ./generator.py ./data/ce1.yaml` con tutti gli yaml presenti, per evitare di farlo a mano
    - Volendo si pò fare un banale script che fa:
    1. Lancia ./br.sh
    2. Crea tutti gli startup-config
    3. Fa sudo containerlab redeploy
 - Fare scrivere le risultanti startup config direttamente in /config/startup, così da non dover copiare e incollare ogni volta
    - Formalizzare la struttura delle cartelle che ho messo per ora totalmente a caso
 - Decidere cosa fare della rete di management:
    - Ha senso tenerla per entrare con ssh ma rompe il cazzo
    - Non so se mettendola in una diversa vrf poi si accede comunque a tutto
    - Quantomeno togliere la default route che va sulla management
 - BGP:
    - Mettere nel template
    - Mettere le informazioni BGP in tutti gli .yaml

## Description
TODO
![Base structure](./img/project-base.jpg)
Our structure:
![Network structure](./img/project.jpg)

## Repository structure
```
.
├───config
│   ├───frr
│   └───startup
├───doc
├───img
└───template
    └───data
```

## Project deployment
### Deploy

1. Create bridges  
  Note that `br-clab-core` and `br-clab-int` are the name of the bridges used in `acn.clab.yml`
  - Via the provided script `br.sh`
  - Manually:
    ```bash
    sudo ip link add br-clab-core type bridge
    sudo ip link set br-clab-core up

    sudo ip link add br-clab-int type bridge
    sudo ip link set br-clab-int up
    ```

2. Deploy the network with containerlab
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