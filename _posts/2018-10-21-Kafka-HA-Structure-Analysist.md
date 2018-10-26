---
layout: post
title:  "Spark Running Flow"
categories: Spark
tags:  bigdata structure mapreduce spark
author: Root Wang
---

* content
{:toc}

## 下面是kafka与其他消息系统之间的区别


![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_ha_strucutre_1.png)

可以看出，kafka支持持久化消息，消息回追等功能，在HA方面kafka使用的是replication策略

在了解replication机制之前必须看下kafka的系统架构的文件存储机制

### kafka的系统架构的文件存储机制

![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_ha_strucutre_2.png)

如图，kafka中的消息是以topic进行分类的，生产者通过topic向kafka broker发送消息，消费者通过topic读取消息。然而topic在物理层面上又能够以partition进行分组，在上一篇已经提到，一个topic可以分为多个partition，那么topic以及partition是怎么存储的呢?partition还可以细分为segment，一个物理上有多个segment组成，那么这些segment又是什么呢?


为了便于说明问题，假设这里只有一个Kafka集群，且这个集群只有一个Kafka broker，即只有一台物理机。在这个Kafka broker中配置($KAFKA_HOME/config/server.properties中)log.dirs=/tmp/kafka-logs，以此来设置Kafka消息文件存储目录，与此同时创建一个topic:topic_vms_test，partition的数量为4.

```sh
($KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --partitions 4 --topic topic_vms_test --replication-factor 4
```
那么我们此时可以在/tmp/kafka-logs(log.dirs option on server.properity)目录中可以看到生成了4个目录:

![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_ha_strucutre_3.png)

在Kafka文件存储中，同一个topic下有多个不同的partition，每个partiton为一个目录，partition的名称规则为:topic名称+有序序号，第一 个序号从0开始计，最大的序号为partition数量减1，partition是实际物理上的概念，而topic是逻辑上的概念。

![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_ha_strucutre_4.png)

“.index”索引文件存储大量的元数据，“.log”数据文件存储大量的消息，索引文件中的元数据指向对应数据文件中message的物理偏移地址。其中以“.index”索引文件中的元数据[3, 348]为例，在“.log”数据文件表示第3个消息，即在全局partition中表示170410+3=170413个消息，该消息的物理偏移地址为348。

如 00000000000000000170410.index 和 log 文件的对应如下:

![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_ha_strucutre_5.png)

那么如何从partition中通过offset查找message呢?

>以上图为例，读取offset=170418的消息，首先查找segment文件，其中 00000000000000000000.index为最开始的文件，第二个文件为00000000000000170410.index(起始偏移为170410+1=170411)，而第 三个文件为00000000000000239430.index(起始偏移为239430+1=239431)，所以这个offset=170418就落到了第二个文件之中。其他 后续文件可以依次类推，以其实偏移量命名并排列这些文件，然后根据二分查找法就可以快速定位到具体文件位置。其次根据 00000000000000170410.index文件中的[8,1325]定位到00000000000000170410.log文件中的1325的位置进行读取。

要是读取offset=170418的消息，从00000000000000170410.log文件中的1325的位置进行读取.

那么怎么知道何时读完本条消息，否则 就读到下一条消息的内容了?

>这个就需要联系到消息的物理结构了，消息都具有固定的物理结构，包括:offset(8 Bytes)、消息体的大 小(4 Bytes)、crc32(4 Bytes)、magic(1 Byte)、attributes(1 Byte)、key length(4 Bytes)、key(K Bytes)、payload(N Bytes)等等字段，可以确定一条消息的大小，即读取到哪里截止。

kafka的高可用就是依赖于上面的文件存储结构的，kafka能保证HA的策略有:

*.data replication
*.leader election。

Kafka中topic的每个partition有一个`预写式的日志文件`，虽然partition可以继续细分为若干个segment文件，但是对于上层应用来说可以将 partition看成最小的存储单元(一个有多个segment文件拼接的“巨型”文件)，每个partition都由一些列有序的、不可变的消息组成，这些消息被连续的追加到partition中。

在kafka0.8版本之后 ，为了提高消息的可靠性，Kafka每个topic的partition有N个副本(replicas)，其中N(大于等于1)是topic的复制因子(replica fator)的个数。

这个时候每个 partition下面就有可能有多个 replicas(_replication机制，相当于是partition的副本但是有可能存储在其他的broker上_),但是这多个replica并不一定分布在一个broker上，而这时候为了*更好的在replica之间复制数据，此时会选出一个leader，这个时候 producer会push消息到这个leader(leader机制)，consumer也会从这个leader pull 消息，其他的 replica只是作为follower从leader复制数据，leader负责所有的读写*;

如果没有一个leader的话，所有的replica都去进行读写 那么NxN(N+1个replica之间复制消息)的互相同步数据就变得很复杂而且数据的一致性和有序性不能够保证。

为了实现更高的可用性，_推荐在部署kafka的时候，能够保证一个topic的partition数量大于broker的数量，而且还需要把replica均匀的分布在所有的broker上，不能够只分布在一个 broker上_，如果只分布在一个broker上，此时如果broker 宕机，会导致所有的replica都不能够提供服务，partition数据丢失或是不能够写入和读取，所以需要均匀的分布replica，即使某个broker宕机，但是可以保证它上面的负载可以被均匀的分配到其他幸存的拥有replica的broker上。

kafka 分配replica的算法是：

1.将所有的broker(假设共有n个broker) 和 partition进行排序
2.将第i个partition分配到第(i mod n)个broker上
3.将第i个partition的第j个replica分配到第((i+j)mod n)个broker上

zookeepe会对partition的leader replica等进行管理

## kafka中的消息同步：

### kafka传播消息

HW:HW俗称高水位，HighWatermark的缩写

kafka在处理传播消息的时候，
1.Producer会发布消息到某个partition上，先通知找到这个partition的leader replica，无论这个partition的 Replica factor是多少，Producer 先把消息发送给replica的leader
2.然后Leader在接受到消息后会写入到Log，这时候这个leader的其余follower都会去leader pull数据，这样可保证follower的replica的数据顺序和leader是一致的.
3.follower在接受到消息之后写入到Log里面(同步)，然后向leader发送ack确认.
4.一旦Leader接收到了所有的ISR(与leader保持同步的Replica列表)中的follower的ack消息，这个消息就被认为是 commit了，然后leader增加HW并且向producer发送ack消息，表示消息已经发送完成。

但是为了提高性能，每个follower在接受到消息之后就会直接返回给leader ack消息，而并非等数据写入到log里面(异步)，所以，可以认为对于已经commit的数据，*只可以保证消息已经存在与所有的replica的内存中，但是不保证已经被持久化到磁盘中，所以进而也就不能保证完全发生异常的时候，该消息能够被consumer消费掉*，如果异常发生，leader 宕机，而且内存数据消失，此时重新选举leader就会出现这样的情况，但是由于考虑这样的情况实属少见，所以这种方式在性能和数据持久化上做了一个相对的平衡，consumer读取消息也是从 leader，并且只有已经commit之后的消息(offset小于HW)才会暴露给consumer。

kafka replication propagate消息的过程:

![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_ha_strucutre_6.png)

如图示: Kafka集群中有4个broker, 某topic有3个partition,且复制因子即副本(replica)个数也为3，Kafka提供了数据复制算法保证，如果leader发生故障或挂掉，一个新leader被选举并被接受客户端的消息成功写入。Kafka确保从同步副本列表中选举一个副本为leader，或者说follower追赶leader数据。leader负责维护和跟踪ISR(In-Sync Replicas的缩写，表示副本同步队列)中所有follower滞后的状态。当producer发送一条消息到broker后，leader写入消息并通知ISR中的所有follower去拉取消息，follower拉取到消息之后返回ack，leader收到所有的follower的确认消息之后，这个消息就会认为提交了。


*消息复制延迟受最慢的follower限制，那么怎么在高性能和高可用之间权衡呢? 关系到下面消息的确认*

### kafka的消息确认

kafka的存活条件包括两个条件：
1.kafka必须维持着与zookeeper的session(这个通过zookeeper的heartbeat机制来实现)
2.follower必须能够及时的将数据从leader复制过去 ，不能够“落后太多”。

leader会跟踪与其保持着同步的replica列表简称ISR，(in-sync replica)，如果一个follower宕机或是落后太多，leader就会把它从ISR中移除掉。这里指的落后太多是说 follower复制的消息落后的超过了预设值，(该值可在$KAFKA_HOME/config/server.properties中通过replica.lag.max.messages配置，其默认值是4000)，或者follower超过一定时间(该值可在$KAFKA_HOME/config/server.properties中通过replica.lag.time.max.ms来配置，其默认值是10000)没有向leader发起fetch请求。

*kafka的消息确认机制跟kafka消息的复制机制有关：*

_kafka的复制机制既不是完全的同步复制，也不是单纯的异步复制_，
同步的话需要所有的ISR中的follower都复制完成之后才能确认这个消息已经commit了，这个复制方式严重了影响了kafka的吞吐量。
但是在异步复制的情况下，follower异步的从leader拉取数据，消息被leader 写入Log后就被认为是已经commit了，如果此时 follower没有从leader复制完，并且leader宕机，此时consumer就会接收不到消息，导致数据的丢失.
所以 kafka这种ISR的机制可以更好的平衡吞吐量和确保数据不丢失，Follower可以批量的从leader复制数据，这样极大的提高了性能(批量写磁盘)，极大减少follower和leader的差距。

kafka只解决fail 和recover，一条消息只有被ISR里的所有Follower都从Leader复制过去才会被认为已提交。这样就避免了部分数据被写进了Leader，还没来得及被任何Follower复制就宕机了，而造成数据丢失(Consumer无法消费这些数据)。而对于Producer而言，它可以选择是否等待消息commit，这可以通过request.required.acks来设置。这种机制确保了只要ISR有一个或以上的Follower，一条被commit的消息就不会丢失。

### kafka 中的leader选举：

上文说明了Kafka是如何做Replication的，另外一个很重要的问题是当Leader宕机了，怎样在Follower中选举出新的Leader。因为Follower可能落后许多或者crash了，所以必须确保选择“最新”的Follower作为新的Leader。
一个基本的原则就是，如果Leader不在了，新的Leader必须拥有原来的Leader commit过的所有消息。这就需要作一个折衷，如果Leader在标明一条消息被commit前等待更多的Follower确认，那在它宕机之后就有更多的Follower可以作为新的Leader，但这也会造成吞吐率的下降。

#### Majority Vote
一种非常常用的Leader Election的方式是“Majority Vote”(“少数服从多数”)，但Kafka并未采用这种方式。这种模式下，如果我们有2f+1个Replica(包含Leader和Follower)，那在commit之前必须保证有f+1个Replica复制完消息，为了保证正确选出新的Leader，fail的Replica不能超过f个。因为在剩下的任意f+1个Replica里，至少有一个Replica包含有最新的所有消息。
这种方式有个很大的优势，系统的latency(等待时间)只取决于最快的几个Broker，而非最慢那个。
Majority Vote也有一些劣势，为了保证Leader Election的正常进行，它所能容忍的fail的follower个数比较少。如果要容忍1个follower挂掉，必须要有3个以上的Replica，如果要容忍2个Follower挂掉，必须要有5个以上的Replica。也就是说，在生产环境下为了保证较高的容错程度，必须要有大量的Replica，而大量的Replica又会在大数据量下导致性能的急剧下降。这就是这种算法更多用在Zookeeper这种共享集群配置的系统中而很少在需要存储大量数据的系统中使用的原因。例如HDFS的HA Feature是基于majority-vote-based journal，但是它的数据存储并没有使用这种方式。

实际上，Leader Election算法非常多，比如Zookeeper的Zab,Raft和Viewstamped Replication。而Kafka所使用的Leader Election算法更像微软的PacificA算法。

#### 而Kafka所使用的Leader Election

Kafka在Zookeeper中动态维护了一个ISR(in-sync replicas)，这个ISR里的所有Replica都跟上了leader，只有ISR里的成员才有被选为Leader的可能。在这种模式下，对于f+1个Replica，一个Partition能在保证不丢失已经commit的消息的前提下容忍f个Replica的失败。在大多数使用场景中，这种模式是非常有利的。事实上，为了容忍f个Replica的失败，Majority Vote和ISR在commit前需要等待的Replica数量是一样的，但是ISR需要的总的Replica的个数几乎是Majority Vote的一半。

虽然Majority Vote与ISR相比有不需等待最慢的Broker这一优势，但是Kafka作者认为Kafka可以通过Producer选择是否被commit阻塞来改善这一问题，并且节省下来的Replica和磁盘使得ISR模式仍然值得。

*那么如何选取出leader?：*

最简单最直观的方案是(谁写进去谁就是leader)，所有Follower都在Zookeeper上设置一个Watch，一旦Leader宕机，其对应的ephemeral znode会自动删除，此时所有Follower都尝试创建该节点，而创建成功者(Zookeeper保证只有一个能创建成功)即是新的Leader，其它Replica即为Follower。

但是该方法会有3个问题：

1.split-brain 这是由Zookeeper的特性引起的，虽然Zookeeper能保证所有Watch按顺序触发，但并不能保证同一时刻所有Replica“看”到的状态是一样的，这就可能造成不同Replica的响应不一致
2.herd effect 如果宕机的那个Broker上的Partition比较多，会造成多个Watch被触发，造成集群内大量的调整
3.Zookeeper负载过重 每个Replica都要为此在Zookeeper上注册一个Watch，当集群规模增加到几千个Partition时Zookeeper负载会过重。

*Kafka 的解决方案是在所有broker中选出一个controller，所有Partition的Leader选举都由这个controller决定*(这个在后面的FailOver中会具体说明)。controller会将Leader的改变直接通过RPC的方式(比Zookeeper Queue的方式更高效)通知需为此作出响应的Broker。同时controller也负责增删Topic以及Replica的重新分配。

最后详细介绍下ISR：

上面我们涉及到`ISR (In-Sync Replicas)`，这个是指副本同步队列。副本数对Kafka的吞吐率是有一定的影响，但极大的增强了可用性。默 认情况下Kafka的replica数量为1，即每个partition都有一个唯一的leader，为了确保消息的可靠性，通常应用中将其值(由broker的参数 offsets.topic.replication.factor指定)大小设置为大于1，比如3。 所有的副本(replicas)统称为`Assigned Replicas，即AR`。

ISR是AR中的一个子集，由leader维护ISR列表，follower从leader同步数据有一些延迟(包括延迟时间replica.lag.time.max.ms和延迟条数replica.lag.max.messages两个维度, 当前最新的版本0.10.x中只支持replica.lag.time.max.ms这个维度)，任意一个超过阈值都会把 follower剔除出ISR, 存入`OSR(Outof-Sync Replicas)`列表，新加入的follower也会先存放在OSR中。`AR=ISR+OSR`。

Kafka 0.10.x版本后移除了replica.lag.max.messages参数，只保留了replica.lag.time.max.ms作为ISR中副本管理的参数。为什么这样做 呢?replica.lag.max.messages表示当前某个副本落后leaeder的消息数量超过了这个参数的值，那么leader就会把follower从ISR中删除。 假设设置replica.lag.max.messages=4，那么如果producer一次传送至broker的消息数量都小于4条时，因为在leader接受到producer发送 的消息之后而follower副本开始拉取这些消息之前，follower落后leader的消息数不会超过4条消息，故此没有follower移出ISR，所以这时 候replica.lag.max.message的设置似乎是合理的。

但是producer发起瞬时高峰流量，producer一次发送的消息超过4条时，也就是超过replica.lag.max.messages，此时follower都会被认为 是与leader副本不同步了，从而被踢出了ISR。但实际上这些follower都是存活状态的且没有性能问题。那么在之后追上leader,并被重新加 入了ISR。于是就会出现它们不断地剔出ISR然后重新回归ISR，这无疑增加了无谓的性能损耗。而且这个参数是broker全局的。设置太大 了，影响真正“落后”follower的移除;设置的太小了，导致follower的频繁进出。无法给定一个合适的replica.lag.max.messages的值，故此，新版本的Kafka移除了这个参数。

*注:ISR中包括:leader和follower。*

HW:HW俗称高水位，HighWatermark的缩写，取一个partition对应的ISR中最小的LEO作为HW，consumer最多只能消费到HW所在的位置。另外每个replica都有HW,leader和follower各自负责更新自己的HW的状态。对于leader新写入的消息，consumer不能立刻消费， leader会等待该消息被所有ISR中的replicas同步后更新HW，此时消息才能被consumer消费。这样就保证了如果leader所在的broker失效，该消息仍然可以从新选举的leader中获取。对于来自内部broker的读取请求，没有HW的限制。

producer生产消息至broker后，ISR以及HW和LEO的流转过程图如下:

![](https://github.com/XGWang0/wiki/raw/master/_images/kafka_ha_strucutre_7.png)

Kafka的这种使用ISR的方式则很好的均衡了确保数据不丢失以及吞吐率,就像上面说的既不是同步也不是异步。

Kafka的ISR的管理最终都会反馈并且保存到Zookeeper节点上。具体位置为:/brokers/topics/[topic]/partitions/[partition]/state。目前有两个地方会 对这个Zookeeper的节点进行维护:

1. Controller来维护:Kafka集群中的其中一个Broker会被选举为Controller，主要负责Partition管理和副本状态管理，也会执行类似于创建删除topic，重分配partition之类的管理任务。在符合某些特定条件下，Controller下的LeaderSelector会选举新的leader，ISR和新的 leader_epoch及controller_epoch写入Zookeeper的相关节点中。同时发起LeaderAndIsrRequest通知所有的replicas并且修改这个节点。

2. leader来维护:leader有单独的线程定期检测ISR中follower是否脱离ISR, 如果发现ISR变化，则会将新的ISR的信息返回到 Zookeeper的相关节点中。

