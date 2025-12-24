## Deploy
sudo containerlab deploy [-t acn.clab.yml]

### Redepoly
sudo containerlab redeploy [-t acn.clab.yml]

## Show topology
sudo containerlab graph [--topo -t acn.clab.yml]

## Destroy
sudo containerlab destroy [-t acn.clab.yml]
To check if all containers have been destroyed:
docker ps -a
To manually destory containers:
sudo docker rm -f <container-id>