---
layout: post
title:  "hadoop sencondnamenode setting"
categories: hadoop
tags:  bigdata structure hadoop 
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

## Config xml file
**New masters for secondnamenode**

```sh
echo openqa > masters
```

**Edit hdfs-site.xml**

Add following info to hdfs-site.xml

```doc
<property>
<name>dfs.namenode.secondary.http-address</name>
<value>openqa:50090</value>
</property>
```
>Notice: the node name "openqa" should be idential with content of masters


**Upload changed files to all nodes**

```sh
scp hdfs-site.xml masters openqa@/${hadoop etc path}
```

**Notice**

```doc
<property>
<name>dfs.namenode.secondary.http-address</name>
<value>openqa:50090</value>
</property>
```
>If do not add above info to hdfs-site.xml, the namenode will start-up a secondnamenode, additionally, the content of masters file will decide is another secondnamenode will be up. In this case, will start up *2 secondnamenodes*, one is default in *name node*, another one is in *openqa* node

------------------------------------------

## Config for backup node
> The backup node should not be existent with `secondnamenode` or `checkpoint node`

All config files should be same on non-backup server, only backup server setting need to follow below content:
```doc
<property>
 <name>dfs.namenode.backup.http-address</name>
 <value>hadoop-slave2:50090</value>
</property>


<property>
        <name>dfs.backup.address</name>
        <value>hadoop-slave2:9000</value>
</property>

<property>
 <name>dfs.namenode.http-address</name>
 <value>master:50070</value>
</property>

<property>
    <name>fs.checkpoint.dir</name>
 <value>/root/hadoop/dfs/checkpoint</value>
</property>
```

> The item fs.checkpoint.dir will use default setting if not set

## Start up backup node

run cmd on master host, do not user start-all.sh to startup all instances
```sh
start-dfs.sh
start-yarn.sh
```

run cmd on backup node server

```sh
#> hdfs namenode -backup
#> jps
namenode
datanode

```

## How to recover namenode by backup node
>The current backup node is not hot standby, so need manually recover

*.Stop namenode of master
*.Clean all files in dfs.name.dir of master node
*.Copy all fsimage files from dfs.name.dir of backup node to master node
*.run
```sh
hdfs namenode -importCheckPoint
```
*.Start master node
