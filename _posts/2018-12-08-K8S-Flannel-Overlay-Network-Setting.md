---
layout: post
title:  "K8S Flannel Overlay Network Setting"
categories: k8s
tags:  docker k8s
author: Root Wang
---

* content
{:toc}


### Host env
hostA : 
	ip : 11.11.18.8
	os : opensuse 42.3
	docker : 18.06.1-ce
        Go : go1.10.5
	flannel : 0.7.1-1.2
	etcd : 3.1.0-3.2
	etcdctl : 3.1.0-3.2

hostB : 
	ip : 11.11.19.191
	os : opensuse 42.3
	docker : 18.06.1-ce
        Go : go1.10.5
	etcd : 3.1.0-3.2
	etcdctl : 3.1.0-3.2

### Setting Server Config

#### Etcd Setting

1.Modify file /etc/sysconfig/etcd following below content:

```doc
# 2.0版本之前此端口是4001，为了兼容以往程序此端口还在使用中。以后版本可能会被丢弃

ETCD_LISTEN_CLIENT_URLS="http://10.67.18.8:2379,http://10.67.18.8:4001"

ETCD_ADVERTISE_CLIENT_URLS="http://10.67.18.8:2379,http://10.67.18.8:4001"

```

2.Restart


#### Flannel Setting on each Nodes

1.Modify file /etc/sysconfig/flannel following below content:

```doc

# etcd url location.  Point this to the server where etcd runs
FLANNEL_ETCD_ENDPOINTS="http://10.67.18.8:2379"

# network recode location on etcd             
FLANNEL_ETCD_KEY="/coreos.com/network"
```

2.Add network setting record for flannel on etcd server.
```sh
HostB #:etcdctl --endpoint="http://10.67.18.8:2379" set /coreos.com/network/config '{ "Network": "172.17.0.0/16"}'
HostB #:etcdctl --endpoint="http://10.67.18.8:2379" get /coreos.com/network/config
-----------
{ "Network": "172.17.0.0/16"}
```

3.Restart docker server

4.Restart flannel server

#### Setting docker network

1.Modify network of docker
```sh
HostB #: cp /usr/lib/mk-docker-opts.sh /usr/bin/
HOstB #: /usr/lib/mk-docker-opts.sh -i
HOstB #: cat /run/flannel/subnet.env 
FLANNEL_NETWORK=172.17.0.0/16
FLANNEL_SUBNET=172.17.60.1/24
FLANNEL_MTU=1472
FLANNEL_IPMASQ=false

HOstB #: source /run/flannel/subnet.env
HOstB #: ifconfig docker0 ${FLANNEL_SUBNET}
```

2.Restart docker server

#### Verification

Setting all nodes following above content, you will get:
```sh
HostB #: etcdctl --endpoint="http://10.67.18.8:2379" ls /coreos.com/network/subnets
/coreos.com/network/subnets/172.17.60.0-24
/coreos.com/network/subnets/172.17.14.0-24
```

```sh
HostB #: route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         gateway.office. 0.0.0.0         UG    0      0        0 br0
10.67.16.0      *               255.255.248.0   U     0      0        0 br0
`172.17.0.0      *               255.255.0.0     U     0      0        0 flannel0`
`172.17.60.0     *               255.255.255.0   U     0      0        0 docker0`
172.18.0.0      *               255.255.0.0     U     0      0        0 docker_gwbridge


HostA #: route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         gateway.office. 0.0.0.0         UG    0      0        0 br0
10.67.16.0      *               255.255.248.0   U     0      0        0 br0
`172.17.0.0      *               255.255.0.0     U     0      0        0 flannel0`
`172.17.14.0     *               255.255.255.0   U     0      0        0 docker0`
172.18.0.0      *               255.255.0.0     U     0      0        0 docker_gwbridge


```

```sh
HostB #: etcdctl --endpoint="http://10.67.18.8:2379" get /coreos.com/network/subnets/172.17.60.0-24
{"PublicIP":"11.11.18.8"}
HostB #: etcdctl --endpoint="http://10.67.18.8:2379" get /coreos.com/network/subnets/172.17.14.0-24
{"PublicIP":"11.11.19.191"}
```

```sh
HostA #: ping 172.17.60.1
PING 172.17.60.1 (172.17.60.1) 56(84) bytes of data.
64 bytes from 172.17.60.1: icmp_seq=1 ttl=62 time=0.535 ms 
64 bytes from 172.17.60.1: icmp_seq=2 ttl=62 time=0.564 m
```
