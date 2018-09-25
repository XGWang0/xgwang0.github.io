---
layout: post
title:  "Force metadata to second namenode manually"
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

**Secondnamenode**
  set openqa as secondnamenode


## Step one: Save latest HDFS metadata to the fsimage by the NameNode

On the NameNode, save latest metadata to the fsimage as the HDFS super user (e.g. the user that runs the HDFS daemons) by running following commands:

```sh
$ hdfs dfsadmin -safemode enter
$ hdfs dfsadmin -safemode get # to confirm and ensure it is in safemode
$ hdfs dfsadmin -saveNamespace
$ hdfs dfsadmin -safemode leave
```

## Step two: clean the Secondary NameNode old data dir
On the Secondary NameNode as the HDFS super user, stop Secondary NameNode service.

```sh
$ hadoop-daemon.sh stop secondarynamenode
```

Use jps to make sure the secondarynamenode process is indeed stopped.
Find out the value of dfs.namenode.checkpoint.dir for the `Secondary NameNode`:

```sh
$ hdfs getconf -confKey dfs.namenode.checkpoint.dir
An example output is:

file:///home/hadoop/tmp/dfs/namesecondary
```

Then, move/rename the current dir under dfs.namenode.checkpoint.dir so that it can be rebuilt again. For the above example, the command will be

```sh
$ mv /home/hadoop/tmp/dfs/namesecondary /home/hadoop/tmp/dfs/namesecondary.old
```

## Step three: force a HDFS metadata checkpointing by the Secondary NameNode
Run following command on the Secondary NameNode:

```sh
$ hdfs secondarynamenode -checkpoint force
Then start the secondarynamenode back

$ hadoop-daemon.sh start secondarynamenode
```
