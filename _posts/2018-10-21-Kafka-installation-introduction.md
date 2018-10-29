---
layout: post
title:  "Kafka Installation And Introduction"
categories: Kafka
tags:  bigdata MQ Kafka
author: Root Wang
---

* content
{:toc}

## Kafka简介
讲完实战让我们稍微了解一下Kafka的一些基本入门知识

### 基本术语
*消息* 
先不管其他的，我们使用Kafka这个消息系统肯定是先关注消息这个概念，在Kafka中，每一个消息由键、值和一个时间戳组成


*主题和日志*
然后研究一下Kafka提供的核心概念——主题

Kafka集群存储同一类别的消息流称为主题

主题会有多个订阅者（0个1个或多个），当主题发布消息时，会向订阅者推送记录

针对每一个主题，Kafka集群维护了一个像下面这样的分区日志：

Kafka中的Message是以topic为基本单位组织的，不同的topic之间是相互独立的。每个topic又可以分成几个不同的partition(每个topic有几个partition是在创建topic时指定的)，每个partition存储一部分Message。借用官方的一张图，可以直观地看到topic和partition的关系

![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_log_anatomy.png)

partition是以文件的形式存储在文件系统中，比如，创建了一个名为page_visits的topic，其有5个partition，那么在Kafka的数据目录中(由配置文件中的log.dirs指定的)中就有这样5个目录: page_visits-0， page_visits-1，page_visits-2，page_visits-3，page_visits-4，其命名规则为<topic_name>-<partition_id>，里面存储的分别就是这5个partition的数据。

`这些分区位于不同的服务器上，每一个分区可以看做是一个结构化的提交日志，每写入一条记录都会记录到其中一个分区并且分配一个唯一地标识其位置的数字称为偏移量offset

Kafka集群会将发布的消息保存一段时间，不管是否被消费。例如，如果设置保存天数为2天，那么从消息发布起的两天之内，该消息一直可以被消费，但是超过两天后就会被丢弃以节省空间。其次，Kafka的数据持久化性能很好，所以长时间存储数据不是问题`

如下图所示，生产者每发布一条消息就会向分区log写入一条记录的offset，而消费者就是通过offset来读取对应的消息的，一般来说每读取一条消息，消费者对应要读取的offset就加1，例如最后一条读到offset=12，那么下条offset就为13.由于消费者通过offset来读取消息，所以可以重复读取已经读过的记录，或者跳过某些记录不读



![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_log_consumer.png)


### Partition


### 分区设计
Partition中的每条Message由offset来表示它在这个partition中的偏移量，这个offset不是该Message在partition数据文件中的实际存储位置，而是逻辑上一个值，它唯一确定了partition中的一条Message。因此，可以认为offset是partition中Message的id。partition中的每条Message包含了以下三个属性：
offset
MessageSize
data
其中offset为long型，MessageSize为int32，表示data有多大，data为message的具体内容。它的格式和Kafka通讯协议中介绍的MessageSet格式是一致。

Partition的数据文件则包含了若干条上述格式的Message，按offset由小到大排列在一起。下：

> *.append: 把给定的ByteBufferMessageSet中的Message写入到这个数据文件中。
> *.searchFor: 从指定的startingPosition开始搜索找到第一个Message其offset是大于或者等于指定的offset，并返回其在文件中的位置Position。它的实现方式是从startingPosition开始读取12个字节，分别是当前MessageSet的offset和size。如果当前offset小于指定的offset，那么将position向后移动LogOverHead+MessageSize（其中LogOverHead为offset+messagesize，为12个字节）。
> *.read：准确名字应该是slice，它截取其中一部分返回一个新的FileMessageSet。它不保证截取的位置数据的完整性。
> *.sizeInBytes: 表示这个FileMessageSet占有了多少字节的空间。
> *.truncateTo: 把这个文件截断，这个方法不保证截断位置的Message的完整性。
> *.readInto: 从指定的相对位置开始把文件的内容读取到对应的ByteBuffer中。


Kafka中采用分区的设计有几个目的。一是可以处理更多的消息，不受单台服务器的限制。Topic拥有多个分区意味着它可以不受限的处理更多的数据。第二，分区可以作为并行处理的单元，稍后会谈到这一点

*分布式*
Log的分区被分布到集群中的多个服务器上。每个服务器处理它分到的分区。 根据配置每个分区还可以复制到其它服务器作为备份容错

每个分区有一个leader，零或多个follower。Leader处理此分区的所有的读写请求，而follower被动的复制数据。如果leader宕机，其它的一个follower会被推举为新的leader。 一台服务器可能同时是一个分区的leader，另一个分区的follower。 这样可以平衡负载，避免所有的请求都只让一台或者某几台服务器处理

*生产者*
生产者往某个Topic上发布消息。生产者还可以选择将消息分配到Topic的哪个节点上。最简单的方式是轮询分配到各个分区以平衡负载，也可以根据某种算法依照权重选择分区

*消费者*
Kafka有一个消费者组的概念，生产者把消息发到的是消费者组，在消费者组里面可以有很多个消费者实例，如下图所示：

![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_consumer-groups.png)


Kafka集群有两台服务器，四个分区，此外有两个消费者组A和B，消费者组A具有2个消费者实例C1-2，消费者B具有4个消费者实例C3-6

那么Kafka发送消息的过程是怎样的呢？

例如此时我们创建了一个主题test，有两个分区，分别是Server1的P0和Server2的P1，假设此时我们通过test发布了一条消息，那么这条消息是发到P0还是P1呢，或者是都发呢？答案是只会发到P0或P1其中之一，也就是消息只会发给其中的一个分区

分区接收到消息后会记录在分区日志中，记录的方式我们讲过了，就是通过offset，正因为有这个偏移量的存在，所以一个分区内的消息是有先后顺序的，即offset大的消息比offset小的消息后到。但是注意，由于消息随机发往主题的任意一个分区，因此虽然同一个分区的消息有先后顺序，但是不同分区之间的消息就没有先后顺序了，那么如果我们要求消费者顺序消费主题发的消息那该怎么办呢，此时只要在创建主题的时候只提供一个分区即可

讲完了主题发消息，接下来就该消费者消费消息了，假设上面test的消息发给了分区P0，此时从图中可以看到，有两个消费者组，那么P0将会把消息发到哪个消费者组呢？从图中可以看到，P0把消息既发给了消费者组A也发给了B，但是A中消息仅被C1消费，B中消息仅被C3消费。这就是我们要讲的，主题发出的消息会发往所有的消费者组，而每一个消费者组下面可以有很多消费者实例，这条消息只会被他们中的一个消费掉


### partiiton 如何解决效率问题

*我们来思考一下，如果一个partition只有一个数据文件会怎么样？*

1.新数据是添加在文件末尾（调用FileMessageSet的append方法），不论文件数据文件有多大，这个操作永远都是O(1)的。
2.查找某个offset的Message（调用FileMessageSet的searchFor方法）是顺序查找的。因此，如果数据文件很大的话，查找的效率就低。

那Kafka是如何解决查找效率的的问题呢？有两大法宝：

1.分段 
2.索引

#### 数据文件的分段
Kafka解决查询效率的手段之一是将数据文件分段，比如有100条Message，它们的offset是从0到99。假设将数据文件分成5段，第一段为0-19，第二段为20-39，以此类推，每段放在一个单独的数据文件里面，数据文件以该段中最小的offset命名。这样在查找指定offset的Message的时候，用二分查找就可以定位到该Message在哪个段中。

#### 为数据文件建索引
数据文件分段使得可以在一个较小的数据文件中查找对应offset的Message了，但是这依然需要顺序扫描才能找到对应offset的Message。为了进一步提高查找的效率，Kafka为每个分段后的数据文件建立了索引文件，文件名与数据文件的名字是一样的，只是文件扩展名为.index。
索引文件中包含若干个索引条目，每个条目表示数据文件中一条Message的索引。索引包含两个部分（均为4个字节的数字），分别为相对offset和position。

相对offset：因为数据文件分段以后，每个数据文件的起始offset不为0，相对offset表示这条Message相对于其所属数据文件中最小的offset的大小。举例，分段后的一个数据文件的offset是从20开始，那么offset为25的Message在index文件中的相对offset就是25-20 = 5。存储相对offset可以减小索引文件占用的空间。
position，表示该条Message在数据文件中的绝对位置。只要打开文件并移动文件指针到这个position就可以读取对应的Message了。
index文件中并没有为数据文件中的每条Message建立索引，而是采用了稀疏存储的方式，每隔一定字节的数据建立一条索引。这样避免了索引文件占用过多的空间，从而可以将索引文件保留在内存中。但缺点是没有建立索引的Message也不能一次定位到其在数据文件的位置，从而需要做一次顺序扫描，但是这次顺序扫描的范围就很小了。


---------------------------------

## Kafka installation

### Download and extract tarball

下载地址：http://kafka.apache.org/downloads.
```sh
wget http://apache.fayea.com/kafka/0.10.1.0/kafka_2.11-0.10.1.0.tgz
tar -xvf kafka_2.11-0.10.1.0.tgz
cd kafka_2.11-0.10.1.0

```

### Config 
首先把Kafka解压后的目录复制到集群的各台服务器

然后修改各个服务器的配置文件：进入Kafka的config目录，修改server.properties

```doc
# brokerid就是指各台服务器对应的id，所以各台服务器值不同
broker.id=0
# 端口号，无需改变
port=9092
# 当前服务器的IP，各台服务器值不同
host.name=192.168.0.10
# Zookeeper集群的ip和端口号
zookeeper.connect=192.168.0.10:2181,192.168.0.11:2181,192.168.0.12:2181
# 日志目录
log.dirs=/home/www/kafka-logs
```


### Start Kafka

```sh
bin/kafka-server-start.sh config/server.properties &
```

### Kafka常用命令

1.新建一个主题

```sh
bin/kafka-topics.sh --create --zookeeper hxf:2181,cfg:2181,jqs:2181,jxf:2181,sxtb:2181 --replication-factor 2 --partitions 2 --topic test
```

2.查看新建的主题

```sh
bin/kafka-topics.sh --describe --zookeeper hxf:2181,cfg:2181,jqs:2181,jxf:2181,sxtb:2181 --topic test
```

3.查看Kafka所有的主题

```sh
bin/kafka-topics.sh --list --zookeeper hxf:2181,cfg:2181,jqs:2181,jxf:2181,sxtb:2181
```

4.在终端发送消息

```sh
bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test
```

5.在终端接收（消费）消息

```sh
bin/kafka-console-consumer.sh --zookeeper hxf:2181,cfg:2181,jqs:2181,jxf:2181,sxtb:2181 --bootstrap-server localhost:9092 --topic test --from-beginning
```
