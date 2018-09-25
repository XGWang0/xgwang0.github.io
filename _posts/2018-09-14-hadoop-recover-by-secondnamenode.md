---
layout: post
title:  "hadoop recover by sencondnamenode"
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


## Simulate metadata losing

**Remove metadata**

```sh
Master:~/hadoop/dfs/name # ls
current  in_use.lock

Master:~rm -rf .*
```

**Stop hadoop**

```sh
Master:~stop-all.sh

This script is Deprecated. Instead use stop-dfs.sh and stop-yarn.sh
Stopping namenodes on [Master]
Master: stopping namenode
hadoop-slave2: no datanode to stop
openqa: no datanode to stop
Stopping secondary namenodes [openqa]
openqa: stopping secondarynamenode
stopping yarn daemons
stopping resourcemanager
openqa: stopping nodemanager
hadoop-slave2: stopping nodemanager
openqa: nodemanager did not stop gracefully after 5 seconds: killing with kill -9
hadoop-slave2: nodemanager did not stop gracefully after 5 seconds: killing with kill -9
no proxyserver to stop
```

**Start hadoop**
```sh
Master:~start-all.sh
```
>This step should be failed, browres log file to get details info

**Access hdfs files**
```sh
>hadoop fs -ls /tmp

>failed to connect hdfs

```

**Stop hadoop**

```sh
>stop-all.sh
```


## Recover name node (Method 1)

**Format name node**

```sh
hadoop namenode -format
```

**Acquire original namespaceID and replace the new one**

Original namespaceID
```sh
openqa node> cat /root/hadoop/dfs/data/current/BP-1076104578-10.67.19.84-1535442595827/current/VERSION 

#Thu Sep 13 23:04:14 EDT 2018
namespaceID=2114780969
cTime=1535442595827
blockpoolID=BP-1076104578-10.67.19.84-1535442595827
layoutVersion=-57

-----------------------------------------------------------------------

master node> cat /root/hadoop/dfs/name/current/VERSION 

#Fri Sep 14 14:30:47 GMT+08:00 2018
namespaceID=1782396194
clusterID=CID-97ad8f65-a6f6-4641-8f16-4375896fb373
cTime=1534924162029
storageType=NAME_NODE
blockpoolID=BP-1619706035-10.67.19.84-1534924162029
layoutVersion=-63

```
> Replace value of namespaceID in file Master node with value of namespaceID in openqa node


**Remove fsimage**

```sh
master node> rm -rf fsimage*
```

**Copy secondname fsimages to Master node**

```sh
Master node> scp openqa:/root/hadoop/dfs/secondnamenode/current/fsimage* /root/hadoop/dfs/name/current/
```

**Restart hadoop**

```sh
master node> start-all.sh
```

**Verify data**

```sh
master node> hadoop fs -ls /
```

## Recover name node (Method 2)

**Remove all metadata files on master node**

**Copy namesecondary folder from second namenode to Master node**

```sh
master node > scp -r openqa:/root/hadoop/dfs/namesecondary /roo/hadoop/dfs/
```

**Import checkpoint**

```sh
hadoop namenode -importCheckpoint
```

```sh
output:
        Any changes to the file system meta-data may be lost.
        Recommended actions:
                - shutdown and restart NameNode with configured "dfs.namenode.edits.dir.required" in hdfs-site.xml;
                - use Backup Node as a persistent and up-to-date storage of the file system meta-data.
18/09/14 14:42:06 INFO namenode.LeaseManager: Number of blocks under construction: 0
18/09/14 14:42:06 INFO blockmanagement.BlockManager: initializing replication queues
18/09/14 14:42:06 INFO hdfs.StateChange: STATE* Leaving safe mode after 0 secs
18/09/14 14:42:06 INFO hdfs.StateChange: STATE* Network topology has 0 racks and 0 datanodes
18/09/14 14:42:06 INFO hdfs.StateChange: STATE* UnderReplicatedBlocks has 0 blocks
18/09/14 14:42:06 INFO blockmanagement.BlockManager: Total number of blocks            = 0
18/09/14 14:42:06 INFO blockmanagement.BlockManager: Number of invalid blocks          = 0
18/09/14 14:42:06 INFO blockmanagement.BlockManager: Number of under-replicated blocks = 0
18/09/14 14:42:06 INFO blockmanagement.BlockManager: Number of  over-replicated blocks = 0
18/09/14 14:42:06 INFO blockmanagement.BlockManager: Number of blocks being written    = 0
18/09/14 14:42:06 INFO hdfs.StateChange: STATE* Replication Queue initialization scan for invalid, over- and under-replicated blocks completed in 1 msec
18/09/14 14:42:06 INFO ipc.Server: IPC Server Responder: starting
18/09/14 14:42:06 INFO ipc.Server: IPC Server listener on 9000: starting
18/09/14 14:42:06 INFO namenode.NameNode: NameNode RPC up at: Master/10.67.19.84:9000
18/09/14 14:42:06 INFO namenode.FSNamesystem: Starting services required for active state
18/09/14 14:42:06 INFO namenode.FSDirectory: Initializing quota with 4 thread(s)
18/09/14 14:42:06 INFO namenode.FSDirectory: Quota initialization completed in 1 milliseconds
name space=1
storage space=0
storage types=RAM_DISK=0, SSD=0, DISK=0, ARCHIVE=0
18/09/14 14:42:06 INFO blockmanagement.CacheReplicationMonitor: Starting CacheReplicationMonitor with interval 30000 milliseconds
```

>NOTICE: This method is invalid in my test for hadoop 2.9

