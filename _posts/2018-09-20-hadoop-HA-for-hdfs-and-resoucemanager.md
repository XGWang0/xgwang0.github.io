---
layout: post
title:  "HDFS AND ResourceManager HA Setting"
categories: hadoop
tags:  bigdata structure hadoop recover
author: Root Wang
---

* content
{:toc}
## Preparation:
**Machines**
  10.67.19.100   Master
  10.67.19.101   hadoop-slave1
  10.67.19.102   hadoop-slave2
 
**Hadoop**
  hadoop-2.9.1

## HDFS HA

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/hdfs_HA.png)


```sh
================ master jps result =================
17728 JournalNode
18577 DFSZKFailoverController
10162 QuorumPeerMain
18005 NameNode
18854 NodeManager
18183 DataNode
18700 ResourceManager
20429 Jps
================ exit from master  =================

================ openqa jps result =================
18192 DFSZKFailoverController
18304 NodeManager
5041 QuorumPeerMain
17975 DataNode
17864 NameNode
23096 Jps
17708 JournalNode
================ exit from openqa  =================

================ hadoop-slave2 jps result =================
24112 ResourceManager
25090 Jps
23509 JournalNode
23849 NodeManager
23658 DataNode
9101 QuorumPeerMain
================ exit from hadoop-slave2  =================
```
>QuorumPeerMain : zookeeper instance
>DFSZKFailoverController : Failover instance for hdfs HA
>NameNode : NN
>DataNode : DN
>ResourceManager : RM
>JournalNode : JN


## Config all setting

### zookeeper

```doc
tickTime=2000
# The number of ticks that the initial 
# synchronization phase can take
initLimit=10
# The number of ticks that can pass between 
# sending a request and getting an acknowledgement
syncLimit=5
# the directory where the snapshot is stored.
# do not use /tmp for storage, /tmp here is just 
# example sakes.
dataDir=/root/zookeeper
# the port at which the clients will connect
dataLogDir=/opt/zookeeper-3.4.12/logs

clientPort=2181
server.1=0.0.0.0:2878:3878
server.2=hadoop-slave1:2878:3878
server.3=hadoop-slave2:2878:3878
```
> [Get zoo.cfg](https://github.com/XGWang0/xgwang0.github.io/raw/master/_files/zookeeper/zoo.cfg)
> New file myid in folder dataDir and type number of server into myid file, different server need to add different server id init it. take server.1 as example, need add 1 to myid file on server.1

### core-site.xml

```doc
<configuration>
<property>
  <name>hadoop.tmp.dir</name>
  <value>/root/hadoop/tmp</value>
  <description>A base for other temporary directories.</description>
</property>

<property>
  <name>fs.defaultFS</name>
  <value>hdfs://myhdfs</value>
  <description>hdfs cluser unique id(hdfs-site.xml setting it), can use this address as -fs value during hdfs operations </description>
</property>

<property>
  <name>fs.checkpoint.period</name>
  <value>60</value>
  <description>The number of seconds between two periodic checkpoints.
  </description>
</property>

<property>
  <name>fs.checkpoint.size</name>
  <value>67108864</value>
</property>

<property>
   <name>ha.zookeeper.quorum</name>
   <value>master:2181,openqa:2181,hadoop-slave2:2181</value>
  <description>Set zookeeper server and port</description>
</property>

</configuration>
```

> [Get core-site.xml](https://github.com/XGWang0/xgwang0.github.io/raw/master/_files/hdfs/HA/core-site.xml)


### hdfs-site.xml

```doc
<property>
   	<name>dfs.name.dir</name>
   	<value>/root/hadoop/dfs/name</value>
   	<description>Path on the local filesystem where the NameNode stores the namespace and transactions logs persistently.</description>
</property>

<property>
    <name>dfs.data.dir</name>
    <value>/root/hadoop/dfs/data</value>
    <description>Comma separated list of paths on the localfilesystem of a DataNode where it should store its blocks.</description>
</property>

<property>
	<name>dfs.replication</name>
	<value>2</value>
</property>

<property>
<name>dfs.permissions</name>
 	<value>false</value>
    <description>need not permissions</description>
</property>

<property>
    <name>fs.checkpoint.dir</name>
    <value>/root/hadoop/dfs/checkpoint</value>
</property>

<property>
    <name>dfs.datanode.max.transfer.threads</name>
    <value>4096</value>
</property>

<property>
    <name>dfs.webhdfs.enabled</name>
    <value>true</value>
	<description>true means enable for web rest api</description>
</property>

<property>
   	<name>dfs.nameservices</name>
   	<value>myhdfs</value>
	<description>uniform server id for hdfs cluster</description>
</property>

<property>
	<name>dfs.ha.namenodes.myhdfs</name>
	<value>nn1,nn2</value>
	<description>name node list for HA</description>
</property>

<property>
	<name>dfs.namenode.rpc-address.myhdfs.nn1</name>
	<value>master:9000</value>
</property>

<property>
	<name>dfs.namenode.rpc-address.myhdfs.nn2</name>
	<value>openqa:9000</value>
</property>

<property>
	<name>dfs.namenode.servicepc-address.myhdfs.nn1</name>
	<value>master:53310</value>
</property>

<property>
	<name>dfs.namenode.servicepc-address.myhdfs.nn2</name>
	<value>openqa:53310</value>
</property>

<property>
	<name>dfs.namenode.http-address.myhdfs.nn1</name>
	<value>master:50070</value>
</property>

<property>
	<name>dfs.namenode.http-address.myhdfs.nn2</name>
	<value>openqa:50070</value>
</property>

<property>
	<name>dfs.namenode.shared.edits.dir</name>
	<value>qjournal://master:8485;openqa:8485;hadoop-slave2:8485/myhdfs</value>
</property>

<property>
	<name>dfs.journalnode.edits.dir</name>
	<value>/root/hadoop/dfs/jndata</value>
</property>

<property>
	<name>dfs.client.failover.proxy.provider.myhdfs</name>
	<value>org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider</value>
</property>

<property>
	<name>dfs.ha.fencing.methods</name>
	<value>shell(/tmp/check_master.sh)</value>
	<!-- value>sshfence</value-->
</property>

<property>
	<name>dfs.ha.fencing.ssh.private-key-files</name>
	<value>/home/user/.ssh/id_rsa</value>
</property>

<property>
	<name>dfs.namenode.edits.dir</name>
	<value>/root/hadoop/dfs/edits</value>
</property>

<property>
	<name>dfs.ha.automatic-failover.enabled</name>
	<value>true</value>
</property>

```

> [Get hdfs-site.xml](https://github.com/XGWang0/xgwang0.github.io/raw/master/_files/hdfs/HA/hdfs-site.xml)


### Sync files

> Remotely copy all changed to all nodes


## Start up and switch active namenode manually

* Start zookeeper on all nodes

```sh
#> bin/zkServer.sh start
```

* Start up journalnode on all nodes

```sh
hadoop-daemon.sh start journalnode
```

* Format namenode on master node

```sh
#> hadoop-daemon.sh start namenode
```

* Sync data of master namenode to standby

```sh
#> hdfs namenode -bootstrapStandby
```

* Start standby namenode
```sh
#> hadoop-daemon.sh start namenode
```

----------------------------------------------

* Browser web of master/standby namenode

>http://master:50070
>http://standby:50070

* Get namenode status

```sh
#> hdfs haadmin -getServiceState nn1
#> hdfs haadmin -getServiceState nn2
```

* Switch namenode between active and standby

```sh
#> hdfs haadmin -transitionToActive nn1
#> hdfs haadmin -transitionToStandby nn1
```

## Startup and Switch automatiocally

* Format hdfs with `zkfc` (This is a must)

```sh
#> hdfs zkfc -formatZK
```
> You can get some node data in zookeeper by command `zkClient ls /`

* Start all instance

```sh
#> start-all.sh
```

* Verify if the standby name becomes active node after active node down

```sh
#> kill -9 ${active namenode process id}
```

--------------------------------------------------------------------------------------------------


## ResourceManager HA

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/rm-ha-overview.png)


### yarn-site.xml

```doc
<!--是否开启RM ha，默认是开启的-->
<property>
   <name>yarn.resourcemanager.ha.enabled</name>
   <value>true</value>
</property>
<!--声明两台resourcemanager的地址-->
<property>
   <name>yarn.resourcemanager.cluster-id</name>
   <value>myrmcluster</value>
</property>
<property>
   <name>yarn.resourcemanager.ha.rm-ids</name>
   <value>rm1,rm2</value>
</property>
<property>
   <name>yarn.resourcemanager.hostname.rm1</name>
   <value>Master</value>
</property>
<property>
   <name>yarn.resourcemanager.hostname.rm2</name>
   <value>hadoop-slave2</value>
</property>

<!--指定zookeeper集群的地址-->
<property>
   <name>yarn.resourcemanager.zk-address</name>
<value>master:2181,openqa:2181,hadoop-slave2:2181</value>
</property>
<!--启用自动恢复，当任务进行一半，rm坏掉，就要启动自动恢复，默认是false-->
<property>
   <name>yarn.resourcemanager.recovery.enabled</name>
   <value>true</value>
</property>

<!--指定resourcemanager的状态信息存储在zookeeper集群，默认是存放在FileSystem里面。-->
<property>
   <name>yarn.resourcemanager.store.class</name>
   <value>org.apache.hadoop.yarn.server.resourcemanager.recovery.ZKRMStateStore</value>
</property>

<!-- Site specific YARN configuration properties -->

<!-- This is only for rm1 config -->
   <property>
        <description>The address of the applications manager interface in the RM.</description>
        <name>yarn.resourcemanager.address.rm1</name>
        <value>${yarn.resourcemanager.hostname.rm1}:8032</value>
   </property>

   <property>
        <description>The address of the scheduler interface.</description>
        <name>yarn.resourcemanager.scheduler.address.rm1</name>
        <value>${yarn.resourcemanager.hostname.rm1}:8030</value>
   </property>

   <property>
        <description>The http address of the RM web application.</description>
        <name>yarn.resourcemanager.webapp.address.rm1</name>
        <value>${yarn.resourcemanager.hostname.rm1}:8088</value>
   </property>

   <property>
        <description>The https adddress of the RM web application.</description>
        <name>yarn.resourcemanager.webapp.https.address.rm1</name>
        <value>${yarn.resourcemanager.hostname.rm1}:8090</value>
   </property>

   <property>
        <name>yarn.resourcemanager.resource-tracker.address.rm1</name>
        <value>${yarn.resourcemanager.hostname.rm1}:8031</value>
   </property>

   <property>
        <description>The address of the RM admin interface.</description>
        <name>yarn.resourcemanager.admin.address.rm1</name>
        <value>${yarn.resourcemanager.hostname.rm1}:8033</value>
   </property>

<!-- This is only for rm2 config -->
   <property>
        <description>The address of the applications manager interface in the RM.</description>
        <name>yarn.resourcemanager.address.rm2</name>
        <value>${yarn.resourcemanager.hostname.rm2}:8032</value>
   </property>

   <property>
        <description>The address of the scheduler interface.</description>
        <name>yarn.resourcemanager.scheduler.address.rm2</name>
        <value>${yarn.resourcemanager.hostname.rm2}:8030</value>
   </property>

   <property>
        <description>The http address of the RM web application.</description>
        <name>yarn.resourcemanager.webapp.address.rm2</name>
        <value>${yarn.resourcemanager.hostname.rm2}:8088</value>
   </property>

   <property>
        <description>The https adddress of the RM web application.</description>
        <name>yarn.resourcemanager.webapp.https.address.rm2</name>
        <value>${yarn.resourcemanager.hostname.rm2}:8090</value>
   </property>

   <property>
        <name>yarn.resourcemanager.resource-tracker.address.rm2</name>
        <value>${yarn.resourcemanager.hostname.rm2}:8031</value>
   </property>

   <property>
        <description>The address of the RM admin interface.</description>
        <name>yarn.resourcemanager.admin.address.rm2</name>
        <value>${yarn.resourcemanager.hostname.rm2}:8033</value>
   </property>


<!--  Common config -->

   <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
   </property>

   <property>
        <name>yarn.scheduler.maximum-allocation-mb</name>
        <value>2048</value>
        <discription>每个节点可用内存,单位MB,默认8182MB</discription>
   </property>

   <property>
        <name>yarn.nodemanager.vmem-pmem-ratio</name>
        <value>2.1</value>
   </property>

   <property>
        <name>yarn.nodemanager.resource.memory-mb</name>
        <value>2048</value>
</property>

   <property>
        <name>yarn.nodemanager.vmem-check-enabled</name>
        <value>false</value>
</property>

```

> [Get yarn-site.xml](https://github.com/XGWang0/xgwang0.github.io/raw/master/_files/yarn/HA/yarn-site.xml)

### Sync changed file to all nodes **
Need to copy changed files to all servers

### Verify ResourceManager HA

>Broswer http://master:8088
>Browser http://hadoop-slaves2:8088, the access will jump master resourcemanager web page

** Verify status of resourcemanager **

```sh
./yarn rmadmin -getServiceState rm1
```

> When job is running and map just finished, then kill resourcemanager on master, will found the following reduce work will continue run on standby resourcemanager and standby resourcemanager will be active.
