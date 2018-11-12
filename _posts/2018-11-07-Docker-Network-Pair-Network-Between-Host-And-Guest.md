---
layout: post
title:  "Find The Pair Network On Between Host And Container"
categories: hive
tags:  bigdata HA cluster hive mapreduce
author: Root Wang
---

* content
{:toc}

### ENV

Host1 : opensuse
  - Docker : 17.09

#### Step 1 : Get network namespace for host side veth

```sh
# ip a
.....
15: eth1@if16: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:ac:12:00:02 brd ff:ff:ff:ff:ff:ff * link-netnsid 1 *
    inet 172.18.0.2/16 scope global eth1
       valid_lft forever preferred_lft forever
```

From above output, we can found the veth `eth1@if16` 's namespace id is 1

#### Step 2 : Get container pid

```sh
# docker inspect -f "{{ .State.Pid }}" ${docker name/ id}
......
6378
```

#### Step 3 : Check namespace created by container

```sh
# lsns -t net
.....
4026532447 net       1 6378 root  sh
```

#### Step 4 : Get namespace id from container

```sh
nsenter -t 27327 -n ip a
....
15: eth1@if16: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:ac:12:00:02 brd ff:ff:ff:ff:ff:ff * link-netnsid 1 *
    inet 172.18.0.2/16 scope global eth1
       valid_lft forever preferred_lft forever
```

We found the network namespace id is same as in host side, so the veth in container `eth1@if16` and veth in host `eth1@if16` is one pair.
