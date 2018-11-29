---
layout: post
title:  "Swarm Sample"
categories: docker
tags:  docker swarm docker-machine
author: Root Wang
---

* content
{:toc}

### Docker machine

Docker Machine is a tool that lets you install Docker Engine on virtual hosts, and manage the hosts with docker-machine commands. You can use Machine to create Docker hosts on your local Mac or Windows box, on your company network, in your data center, or on cloud providers like Azure, AWS, or Digital Ocean.

Using docker-machine commands, you can start, inspect, stop, and restart a managed host, upgrade the Docker client and daemon, and configure a Docker client to talk to your host.

Point the Machine CLI at a running, managed host, and you can run docker commands directly on that host. For example, run docker-machine env default to point to a host called default, follow on-screen instructions to complete env setup, and run docker ps, docker run hello-world, and so forth.


#### Install Docker-machine with diriver kvm driver
Download a binary release (make sure it is named docker-machine-driver-kvm), mark it as executable, and place it somewhere in your PATH. 
```sh
zypper in docker-machine-kvm

zypper in docker-machine
```

### Create docker machine by kvm driver

```sh
docker-machine create  -d kvm --kvm-network "default" manager2
```
>Got following errors:
>1.Error creating machine: Error detecting OS: Too many retries waiting for SSH to be available.  Last error: Maximum number of retries (60) exceeded
>2.Unable to determine VM's IP address, did it fail to boot?
>
>I try to login to vm by virt-manager, found the net interface is not right, have the `docker0` and `lo` interface, edit vm config file manually and use public bridge interface of host for vm, which can get `eth0` interface with public addr, but still not be used by docker-machine due to docker-machine needs 2 interface `ech0` and `ech1`, the eth0 is used inside vm, ech1 is used communcation with docker machine. 

NOTE: Will fill the solution after investigation

### Create cluster by swarm

#### docker env
hostA :
	os : opensuse 42.2
	docker : 17.09.1-ce
        Go : go1.8.7
hostB : 
	os : opensuse 42.3
	docker : 18.06.1-ce
        Go : go1.10.5

#### Init cluster
```sh
docker swarm init --advertise-addr ${hostA ip addr}

docker swarm join-token manager                                              │i+ | docker-machine-kvm     | package | 0.8.2-1
To add a manager to this swarm, run the following command:                              │.19                          | x86_64 | virt_co
                                                                                        │ntain
    docker swarm join --token SWMTKN-1-57u2oyym6p2ycrqb0xdd0yvhxar6g6b66j3cutgqkt9a3ctli│i  | docker-runc            | package | 1.0.0rc
h-72asgq1o9pgf1r9eydminei7l 10.67.19.84:2377 

docker swarm join-token worker                                               │i+ | docker-machine-kvm     | package | 0.8.2-1
To add a worker to this swarm, run the following command:                               │.19                          | x86_64 | virt_co
                                                                                        │ntain
    docker swarm join --token SWMTKN-1-57u2oyym6p2ycrqb0xdd0yvhxar6g6b66j3cutgqkt9a3ctli│i  | docker-runc            | package | 1.0.0rc
h-26nnkmtoxclifrrkm28r12bzx 10.67.19.84:2377
```

#### Add hostB as worker to cluster

In hostA machine:
```sh
docker swarm join --token SWMTKN-1-57u2oyym6p2ycrqb0xdd0yvhxar6g6b66j3cutgqkt9a3ctlih-26nnkmtoxclifrrkm28r12bzx 10.67.19.84:2377
```

Check node status, on hostA (master)
```sh
docker node ls
ID                            HOSTNAME            STATUS              AVAILABILITY        MANAGER STATUS
0hps30sl7722ydq06mle1am6f *   hostA              Ready               Active              Leader
nke9bocohhy9nagtqzrcr7bsp     hostB              Ready               Active
```

#### Creat service on hostA
```sh
docker service create --detach=false --replicas 2 -p 8009:80 --name web nginx
note: --detach=false is needed, or the service running in backend.
```

Check service status
```sh
docker service ls
ID                  NAME                MODE                REPLICAS            IMAGE               PORTS
mulbmicg89rb        web                 replicated          2/2                 nginx:latest        *:8009->80/tcp

note: 2/2 indicates all replicas are running
```

Check container status on both hostA and hostB:
```sh
docker container ps
```

#### Scaling up Or Scaling Down

```sh
docker service scale web=3

docker service scale web=2
```


#### Draining a worker

Drain a worker means manager will move all services or tasks from the worker which status is active and AVAILABILITY for ready to others available workers.

```sh

# Get node status
:~ # docker node ls
ID                            HOSTNAME            STATUS              AVAILABILITY        MANAGER STATUS
0hps30sl7722ydq06mle1am6f *   hostA              Ready               Active              Leader
nke9bocohhy9nagtqzrcr7bsp     hostB              Ready               Active              

# Get service status from specific node
hostA:~ # docker node  ps hostB                                                                                                       
ID                  NAME                IMAGE               NODE                DESIRED STATE       CURRENT STATE           ERROR       
        PORTS
eyqfy2abyb5w        web.3               nginx:latest        hostB              Running             Running 8 minutes ago

# Make hostB node drain
hostA:~ # docker node update --availability drain hostB                                                                       [0/1914]
hostB


# Reget service status of hostB
hostA:~ # docker node ps hostB 
ID                  NAME                IMAGE               NODE                DESIRED STATE       CURRENT STATE            ERROR      
         PORTS
eyqfy2abyb5w        web.3               nginx:latest        hostB              Shutdown            Shutdown 5 seconds ago              

         
hostA:~ # docker node ps hostA 
ID                  NAME                IMAGE               NODE                DESIRED STATE       CURRENT STATE            ERROR      
                   PORTS
v2kxl0zp6mwh        web.1               nginx:latest        hostA              Running             Running 3 hours ago                 
                   
uy393pe3ixwq         \_ web.1           nginx:latest        hostA              Shutdown            Failed 3 hours ago       "task: non-
zero exit (137)"   
8ihgf5kyl55b         \_ web.1           nginx:latest        hostA              Shutdown            Failed 4 hours ago       "task: non-
zero exit (137)"   
4wief5zz4owk        web.3               nginx:latest        hostA              Running             Running 15 seconds ago  


# Get service status
hostA:~ # docker service ps web
ID                  NAME                IMAGE               NODE                DESIRED STATE       CURRENT STATE                 ERROR                         PORTS
v2kxl0zp6mwh        web.1               nginx:latest        hostA              Running             Running 4 hours ago                                         
uy393pe3ixwq         \_ web.1           nginx:latest        hostA              Shutdown            Failed 4 hours ago            "task: non-zero exit (137)"   
8ihgf5kyl55b         \_ web.1           nginx:latest        hostA              Shutdown            Failed 4 hours ago            "task: non-zero exit (137)"   
4wief5zz4owk        web.3               nginx:latest        hostA              Running             Running about a minute ago                                  
eyqfy2abyb5w         \_ web.3           nginx:latest        hostB              Shutdown            Shutdown about a minute ago
```

#### Rolling update

```sh
docker service update --image <imagename>:<version> web
```

#### Remove swarm
1.Remove service
```sh
docker service rm .....
```

2.Leave all worker from swarm
Run following cmd on each worker
```sh
docker swarm leave -f
```

3.Close manager of swarm
Run following cmd on manager
```sh
docker swarm leave -f
``
