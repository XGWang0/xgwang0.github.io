---
layout: post
title:  "Capabilitys Of Linux"
categories: Security
tags:  security capability
author: Root Wang
---

* content
{:toc}

## 环境
*. 一台主机，启动两个opensuse；
*. 两台虚拟机的ip为192.168.159.130和192.168.159.132
原理图如下：

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/vxlan_gre_network.jpg)

这里的VTEP就是隧道endpoint，可以是GRE也可以是VXLAN的。
为什么要加namespace，是模拟物理中的虚拟机报文走向，guest的网络和host的网络本身就是两个不同的网络，os都不同.


## GRE模型
在其中一个192.168.159.130虚拟机上，主要执行如下命令：

```sh
ip netns add ns0 //创建一个namespace，用于模拟vm环境
ip link add veth0 type veth peer name veth1 //创建一对veth
ip link set veth0 netns ns0 //把veth0加入到namespace中
ip netns exec ns0 ip addr add 10.1.1.2/24 dev veth0 //在ns0中给veth0配上IP
ovs-vsctl add-br br-int //创建ovs网桥
ovs-vsctl add-port br-int veth1 //把veth1加入到网桥作为internal类型的port
ovs-vsctl add-port br-int gre0 – set interface gre0 type=gre options:remote_ip=192.168.159.132 //给ovs网桥添加gre类型的port，并指定远端ip
```

在另外一个host上，也执行如上命令，但是gre口的remote_ip要填成192.168.159.130，且veth0的ip指定成10.1.1.1/24即可。

*补充*
在namespace中，需要确保路由存在，默认在空间里的veth0是属于down状态的，要执行：

```sh
ip netns exec ns0 ip link set veth0 up
```

拉起来后，这样系统就会自动添加一条路由信息，如：

```sh
10.1.1.0/24 dev veth0  proto kernel  scope link  src 10.1.1.1 
然后，在192.168.159.132的机器上，用ping命令ping对端的10.1.1.2，注意要在namespace下ping，如
ip netns exec ns0 ping 10.1.1.2
```

便会有以下打印：

```sh
root@suse:~# ip netns exec ns0 ping 10.1.1.2
PING 10.1.1.2 (10.1.1.2) 56(84) bytes of data.
64 bytes from 10.1.1.2: icmp_seq=1 ttl=64 time=2.06 ms
64 bytes from 10.1.1.2: icmp_seq=2 ttl=64 time=0.649 ms
64 bytes from 10.1.1.2: icmp_seq=3 ttl=64 time=0.851 ms
64 bytes from 10.1.1.2: icmp_seq=4 ttl=64 time=0.859 ms
64 bytes from 10.1.1.2: icmp_seq=5 ttl=64 time=0.564 ms
```

在192.168.159.130所在网口eth0上抓包，结果为：

```sh
root@suse:~# tcpdump -i eth0 src 192.168.159.132
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes
00:11:08.983087 IP 192.168.159.132 > 192.168.159.130: GREv0, length 102: IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5174, seq 100, length 64
00:11:09.982124 IP 192.168.159.132 > 192.168.159.130: GREv0, length 102: IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5174, seq 101, length 64
00:11:10.984115 IP 192.168.159.132 > 192.168.159.130: GREv0, length 102: IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5174, seq 102, length 64
00:11:11.983123 IP 192.168.159.132 > 192.168.159.130: GREv0, length 102: IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5174, seq 103, length 64
```

再对veth1抓包，结果为：

```sh
root@suse:~# tcpdump -i veth1
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on veth1, link-type EN10MB (Ethernet), capture size 262144 bytes
00:09:45.901800 IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5174, seq 17, length 64
00:09:45.901892 IP 10.1.1.2 > 10.1.1.1: ICMP echo reply, id 5174, seq 17, length 64
00:09:46.902296 IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5174, seq 18, length 64
00:09:46.902458 IP 10.1.1.2 > 10.1.1.1: ICMP echo reply, id 5174, seq 18, length 64
00:09:47.903955 IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5174, seq 19, length 64
```

可以看到，在eth0，走的是GREv0的192.168.159.0网段，经过gre0口剥离后，在veth1上，就变成10.1.1.0网段的报文了。

## VXLAN模型
VXLAN的模型和GRE一样，只不过是用VXLAN类型的端口替换了gre类型的端口。
操作步骤如下：

在上述GRE模型的基础上，删除gre0口：

```sh
ovs-vsctl del-port br-int gre0
```

添加vxlan口，比如：

```sh
ovs-vsctl add-port br-int vxlan0 – set interface vxlan0 type=vxlan options:remote_ip=192.168.159.132
```

在两个节点都这么操作，当然remote_ip需要根据具体单板填写。

执行后，同样对eth0上抓包，结果为：

```sh
root@suse:~# tcpdump -i eth0 src 192.168.159.132
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes
00:34:15.888589 IP 192.168.159.132.45741 > 192.168.159.130.4789: VXLAN, flags [I] (0x08), vni 0
IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5411, seq 397, length 64
00:34:16.890482 IP 192.168.159.132.45741 > 192.168.159.130.4789: VXLAN, flags [I] (0x08), vni 0
IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5411, seq 398, length 64
00:34:17.890829 IP 192.168.159.132.45741 > 192.168.159.130.4789: VXLAN, flags [I] (0x08), vni 0
IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5411, seq 399, length 64
```

在veth1上抓，为：

```sh
root@suse:~# tcpdump -i veth1
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on veth1, link-type EN10MB (Ethernet), capture size 262144 bytes
00:28:00.714422 IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5411, seq 22, length 64
00:28:00.714509 IP 10.1.1.2 > 10.1.1.1: ICMP echo reply, id 5411, seq 22, length 64
00:28:01.714182 IP 10.1.1.1 > 10.1.1.2: ICMP echo request, id 5411, seq 23, length 64
00:28:01.714214 IP 10.1.1.2 > 10.1.1.1: ICMP echo reply, id 5411, seq 23, length 64
```

从结果看，在eth0上，VXLAN类型报文被接收，网段为192.168.159.0，通过解分装，在veth1上就同样是10.1.1.0网段的报文了。

其他
VXLAN和GRE其实在技术细节上是有很大区别的。据说，VXLAN是通过组播的技术，发送组播加入包后，后续的私有网络通信都是通过组播来搞定；而GRE的话，有个硬伤，就是网络节点互相之间必须有私有隧道，即两两间都要有链接，当节点规模大的时候，维护起来成本太高，而VXLAN通过组播解决了这个问题。（听说neutron把VXLAN的组播阉割了，等同于GRE）

另外，观察VXLAN的报文，发现报文一直是被本机的4789端口收，用命令看了下：

```sh
root@suse:~# netstat -a|grep 4789
udp        0      0 *:4789                  *:*
```

删了节点上的vxlan口后，发现这条记录不见了，说明ovs网桥在创建VXLAN类型的port时，都会监听4789端口。而GRE类型的port则不会。
