---
layout: post
title:  "Hive Installation And Using"
categories: hive
tags:  bigdata HA cluster hive mapreduce
author: Root Wang
---

* content
{:toc}


### Setting 

#### ENV

Host1 : opensuse
  - Docker : 17.09

Host2 : opensuse
  - Docker : 17.09

Host3: opensuse
  - Docker : 17.09

-------------------------------

#### Install & start consul on Host1

* Instllation *
```sh
docker run -d -p 8500:8500 -h consul --name consul progrium/consul -server -bootstrap

```

* Get ip addr for consul *

```sh
docker container inspect -f '{{ .NetworkSettings.IPAddress }}' consul

172.17.0.3
```

#### Setting for others hosts except host1

* Setting on host2 and host3 *

1.Get docker.service config file

```sh
   systemctl cat docker.service
```

2.Get env file for step 1 result

Sample:
```doc
[Service]
#EnvironmentFile=/etc/sysconfig/docker
`EnvironmentFile=/etc/default/docker`

# While Docker has support for socket activation (-H fd://), this is not
# enabled by default because enabling socket activation means that on boot your
# containers won't start until someone tries to administer the Docker daemon.
Type=notify
ExecStart=/usr/bin/dockerd --containerd /run/containerd/containerd.sock --add-runtime oci=/usr/sbin/docker-runc $DOCKER_NETWORK_OPTIONS 
ExecReload=/bin/kill -s HUP $MAINPID

# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity

# Uncomment TasksMax if your systemd version supports it.
# Only systemd 226 and above support this property.
TasksMax=infinity

# Set delegate yes so that systemd does not reset the cgroups of docker containers
# Only systemd 218 and above support this property.
Delegate=yes

# This is not necessary because of how we set up containerd.
#KillMode=process

```

3. Add following content to step2
```sh
# Add following info to /etc/default/docker or /etc/sysconfig/docker which defined by variable EnvironmentFile in device.server
DOCKER_OPTS="-H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock --cluster-advertise {Docker Host[2,3] network interface/ip addr}:2375 --cluster-store consul://{Docker Host 1 IP Address}:8500"

Sample :
DOCKER_OPTS="-H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock --cluster-advertise eth0:2375 --cluster-store consul://10.67.19.84:8500 "

```

4. Check cluster related option 

```sh
docker info

Sample:
Cluster Store: consul://10.67.19.84:8500
Cluster Advertise: 10.67.132.90:2375
```

5. Restart docker deamon


#### Create overlay network and using

1. Create overlay network on any hosts except host1

```sh
docker network create -d overlay --subnet=192.168.3.0/24 my-overlay
```

2. Check network info 

```sh
docker network ls
```

3. Start container via overlay network on host2

```sh
docker run -itd --name container1 --net my-overlay busybox
``

4. Start container via overlay network on host3

```sh
docker run -itd --name container2 --net my-overlay busybox
``

5. Inpect overlay network

```sh
$ docker network inspect my-overlay

Sample:
        "Containers": {
            "9cb9b55aa18cf4058ae82827fe63a6bb70519f9b51d3957f4754e7fbce40ede3": {
                "Name": "container_slave2",
                "EndpointID": "46ca5d385f926f582811c451af8cd413c61cea8ca83db9575cf55ea6742ec18c",
                "MacAddress": "02:42:c0:a8:03:04",
                "IPv4Address": "192.168.3.4/24",
                "IPv6Address": ""
            },
            "ep-fc803d036f5d3313ee536f68a9953d168376e9fe1d83db66c35da2969c0bc9dd": {
                "Name": "container_xgwang",
                "EndpointID": "fc803d036f5d3313ee536f68a9953d168376e9fe1d83db66c35da2969c0bc9dd",
                "MacAddress": "02:42:c0:a8:03:02",
                "IPv4Address": "192.168.3.2/24",
                "IPv6Address": ""
            }
        },


``

6. Ping 

```sh
$ docker exec container1 ping -w 5 container2
```

7. In addition 

Can also put a existing container to overlay network by :

```sh
$ docker network connect my-overlay container3
```

