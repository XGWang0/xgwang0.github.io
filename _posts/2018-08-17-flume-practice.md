---
layout: post
title:  "flume 练习心得"
categories: flume
tags: bigdata structure logcollection
author: Root Wang
---

* content
{:toc}
## 简介
flume （日志收集系统）

Flume是Cloudera提供的一个高可用的，高可靠的，分布式的海量日志采集、聚合和传输的系统，Flume支持在日志系统中定制各类数据发送方，用于收集数据；同时，Flume提供对数据进行简单处理，并写到各种数据接受方（可定制）的能力。
关于写倒计时大家可能都都比较熟悉，使用 setTimeout 或 setInterval 就可以搞定。几秒钟或者几分钟的倒计时这样写没有问题，但是如果是长时间的倒计时，这样写就会不准确。如果用户修改了他的设备时间，这样的倒计时就没有意义了。今天就说说写一个精确的倒计时的方法。

## 优势
1. Flume可以将应用产生的数据存储到任何集中存储器中，比如HDFS,HBase
2. 当收集数据的速度超过将写入数据的时候，也就是当收集信息遇到峰值时，这时候收集的信息非常大，甚至超过了系统的写入数据能力，这时候，Flume会在数据生产者和数据收容器间做出调整，保证其能够在两者之间提供平稳的数据.
3. 提供上下文路由特征
4. Flume的管道是基于事务，保证了数据在传送和接收时的一致性.
5. Flume是可靠的，容错性高的，可升级的，易管理的,并且可定制的。

## 特征
1. Flume可以高效率的将多个网站服务器中收集的日志信息存入HDFS/HBase中
2. 使用Flume，我们可以将从多个服务器中获取的数据迅速的移交给Hadoop中
3. 除了日志信息，Flume同时也可以用来接入收集规模宏大的社交网络节点事件数据，比如facebook,twitter,电商网站如亚马逊，flipkart等
4. 支持各种接入资源数据的类型以及接出数据类型
5. 支持多路径流量，多管道接入流量，多管道接出流量，上下文路由等
6. 可以被水平扩展

## 结构
* `Agent`主要由:`source`,`channel`,`sink`三个组件组成.
- `Source`:
  - 从数据发生器接收数据,并将接收的数据以Flume的event格式传递给一个或者多个通道channal,Flume提供多种数据接收的方式,比如Avro,Thrift,twitter1%等
- `Channel`:
  - `channel`是一种短暂的存储容器,它将从source处接收到的event格式的数据缓存起来,直到它们被sinks消费掉,它在source和sink间起着一共桥梁的作用,channal是一个完整的事务,这一点保证了数据在收发的时候的一致性. 并且它可以和任意数量的source和sink链接. 支持的类型有: JDBC channel , File System channel , Memort channel等.
- `Sink`:
  - `sink`将数据存储到集中存储器比如Hbase和HDFS,它从channals消费数据(events)并将其传递给目标地. 目标地可能是另一个sink,也可能HDFS,HBase.


-------------------------

## 安装

* Download flume bin to local 
* Extract tarball
* Set system variable to /etc/profile
```sh
# flume setting
#
export JAVA_HOME=/usr/lib64/jvm/jre-1.8.0-openjdk
export FLUME_HOME=/syshome/flume/apache-flume-1.8.0-bin
export PATH=$JAVA_HOME/bin:$PATH:$FLUME_HOME/bin
```

## 执行
```sh
# flume-ng  agent --conf ./conf/ -f conf/multi_source_single_changel.conf -Dflume.root.logger=DEBUG,console -n a
```

## flume categories
conf content
----------------------------------------------
### netcat source
```doc
# 指定Agent的组件名称（a），一个进程
a.sources=r1
a.channels=c1
a.sinks=k1

# For netcat source
a.sources.r1.type=netcat
a.sources.r1.bind=10.67.19.84
a.sources.r1.port=4444
a.sources.r1.channels=c1

a.channels.c1.type=memory
a.channels.c1.capacity=1000
a.channels.c1.transactionCapacity=1000

a.sinks.k1.channel=c1
#a.sinks.k1.type=logger
a.sinks.k1.type=file_roll
a.sinks.k1.sink.rollInterval = 0
a.sinks.k1.sink.directory = /var/log/flume
```

### http source
```doc
# 指定Agent的组件名称（a），一个进程
a.sources=r1
a.channels=c1
a.sinks=k1

# For netcat source
#a.sources.r1.type=netcat
#a.sources.r1.bind=10.67.19.84
#a.sources.r1.port=4444
#a.sources.r1.channels=c1

a.sources.r1.type=http
a.sources.r1.bind=10.67.19.84
a.sources.r1.port=5140
a.sources.r1.handler= org.apache.flume.source.http.JSONHandler
a.sources.r1.channels=c1

a.channels.c1.type=memory
a.channels.c1.capacity=1000
a.channels.c1.transactionCapacity=1000

a.sinks.k1.channel=c1
#a.sinks.k1.type=logger
a.sinks.k1.type=file_roll
a.sinks.k1.sink.rollInterval = 0
a.sinks.k1.sink.directory = /var/log/flume
```

_Send data to flume : curl -X POST -d '[{"headers":{"State":"c1","host":"master"},"body":"test for http flume"}]' 10.67.19.84:5140_

### spooling dir source
```
# 指定Agent的组件名称（a），一个进程
a.sources=r1
a.channels=c1
a.sinks=k1

# For netcat source
a.sources.r1.type=spooldir
a.sources.r1.spoolDir=/tmp/flume/
a.sources.r1.fileHeader = true
a.sources.r1.interceptors = i1
a.sources.r1.interceptors.i1.type = timestamp

a.sources.r1.channels=c1

a.channels.c1.type=memory
a.channels.c1.capacity=1000
a.channels.c1.transactionCapacity=1000

a.sinks.k1.channel=c1
a.sinks.k1.type=logger
```

### single source + mutliple channel
```doc
# 指定Agent的组件名称（a），一个进程
a.sources=r1
a.channels=c1 c2 c3
a.sinks=k1

# For netcat source
a.sources.r1.type=netcat
a.sources.r1.bind=10.67.19.84
a.sources.r1.port=4444
#a.sources.r1.handler= org.apache.flume.source.http.JSONHandler
a.sources.r1.channels=c1 c2 c3

# State is the key of header struct, if the value of key State is c1, the source will pass to c1 changel, so one and so forth 
a.sources.r1.selector.type = multiplexing
a.sources.r1.selector.header = State
a.sources.r1.selector.mapping.c1 = c1
a.sources.r1.selector.mapping.c2 = c2
a.sources.r1.selector.mapping.c3 = c3
a.sources.r1.selector.optional.c4 = c1 c2
a.sources.r1.selector.default = c1

# Multiple channels should use different checkpointdir, or cause lock waitting
a.channels.c1.type = file
a.channels.c1.checkpointDir = /tmp/flume/c1_checkpoint
a.channels.c1.dataDirs = /mnt/flume/c1_data

a.channels.c2.type = file
a.channels.c2.checkpointDir = /tmp/flume/c2_checkpoint
a.channels.c2.dataDirs = /mnt/flume/c2_data

a.channels.c3.type = file
a.channels.c3.checkpointDir = /tmp/flume/c3_checkpoint

#a.channels.c1.type=memory
#a.channels.c1.capacity=1000
#a.channels.c1.transactionCapacity=1000

a.sinks.k1.channel=c1
a.sinks.k1.type=logger
#a.sinks.k1.type=file_roll
#a.sinks.k1.sink.rollInterval = 0
#a.sinks.k1.sink.directory = /var/log/flume
```

* one/multiple source[s] VS one/multiple channel[s] *
* one sink VS one channel, not admit one sink VS multiple channels *

### mutliple sources + one channel
```doc
# 指定Agent的组件名称（a），一个进程
a.sources=r1 r2
a.channels=c1
a.sinks=k1

# For netcat source
a.sources.r1.type=netcat
a.sources.r1.bind=10.67.19.84
a.sources.r1.port=4444
a.sources.r1.channels=c1


a.sources.r2.type=netcat
a.sources.r2.bind=10.67.19.84
a.sources.r2.port=4445
a.sources.r2.channels=c1

a.channels.c1.type=memory
a.channels.c1.capacity=1000
a.channels.c1.transactionCapacity=1000

a.sinks.k1.channel=c1
a.sinks.k1.type=logger

```

### sink group with failover
`master server`
```doc
# Name the components on this agent
a1.sources = r1
a1.sinks = k1 k2
a1.channels = c1

# Describe/configure the source
a1.sources.r1.type = exec
a1.sources.r1.channels=c1
a1.sources.r1.command=tail -F /root/flume/sink_group

#define sinkgroups
a1.sinkgroups=g1
a1.sinkgroups.g1.sinks=k1 k2
a1.sinkgroups.g1.processor.type=failover
a1.sinkgroups.g1.processor.priority.k1=20
a1.sinkgroups.g1.processor.priority.k2=10
a1.sinkgroups.g1.processor.maxpenalty=10000

#define the sink 1
a1.sinks.k1.type=avro
a1.sinks.k1.hostname=10.67.19.191
a1.sinks.k1.port=9876

#define the sink 2
a1.sinks.k2.type=logger


# Use a channel which buffers events in memory
a1.channels.c1.type = memory
a1.channels.c1.capacity = 1000
a1.channels.c1.transactionCapacity = 100

# Bind the source and sink to the channel
a1.sources.r1.channels = c1
a1.sinks.k1.channel = c1
a1.sinks.k2.channel=c1
```

`slave server`
```doc
# Name the components on this agent
a1.sources = r1
a1.sinks = k1
a1.channels = c1

# Describe/configure the source
a1.sources.r1.type=avro
#any address to listen
a1.sources.r1.bind=0.0.0.0
a1.sources.r1.port=9876
a1.sources.r1.channels=c1

# Describe the sink
a1.sinks.k1.type = file_roll
a1.sinks.k1.sink.directory=/tmp/flumeout/file
a1.sinks.k1.sink.rollInterval=3600


# Use a channel which buffers events in memory
a1.channels.c1.type = memory
a1.channels.c1.capacity = 1000
a1.channels.c1.transactionCapacity = 100

# Bind the source and sink to the channel
a1.sources.r1.channels = c1
a1.sinks.k1.channel = c1
```
_ When the sink k1 is power down or crash, the channel will send event to k2. Additionally, the priority value of a1.sinkgroups.g1.processor.priority.k1 is bigger, more chance the sink will be used prioritily _

### sink to hdfs

```doc
a.sources=r1
a.channels=c1
a.sinks=k1

# For netcat source
a.sources.r1.type=spooldir
a.sources.r1.spoolDir=/tmp/flume/
a.sources.r1.fileHeader = true
a.sources.r1.interceptors = i1
a.sources.r1.interceptors.i1.type = timestamp

a.sources.r1.channels=c1

a.channels.c1.type=memory
a.channels.c1.capacity=1000
a.channels.c1.transactionCapacity=1000


a.sinks.k1.channel=c1
a.sinks.k1.type=hdfs
a.sinks.k1.hdfs.path=hdfs://myhdfs/flume
a.sinks.k1.hdfs.filePrefix=flume_test
#间隔30s flume生成新文件在hdfs
a.sinks.k1.hdfs.rollInterval=30
#文件大于1024byte，flume创建新文件为hdfs
a.sinks.k1.hdfs.rollSize=1024
#Event大于5时，flume创建新文件为hdfs
a.sinks.k1.hdfs.rollCount=5
a.sinks.k1.hdfs.idleTimeout=2
#数据流保证文件内容统一
a.sinks.k1.hdfs.fileType=DataStream
a.sinks.k1.hdfs.useLocalTimeStamp=true

```

Verify result on hdfs:
```sh
#> hadoop fs -fs hdfs://myhdfs/ -s /flume/
output:
-rw-r--r--   2 root supergroup        106 2018-09-21 05:04 /flume/flume_test.1537520696164
-rw-r--r--   2 root supergroup        216 2018-09-21 05:04 /flume/flume_test.1537520696165
-rw-r--r--   2 root supergroup         87 2018-09-21 05:04 /flume/flume_test.1537520696166
-rw-r--r--   2 root supergroup        146 2018-09-21 05:04 /flume/flume_test.1537520696167
-rw-r--r--   2 root supergroup         39 2018-09-21 05:05 /flume/flume_test.1537520696168
```
>hdfs://myhdfs/ 为集群的server name

