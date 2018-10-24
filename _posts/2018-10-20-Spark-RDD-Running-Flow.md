---
layout: post
title:  "Spark Running Flow"
categories: Spark
tags:  bigdata structure mapreduce spark
author: Root Wang
---

* content
{:toc}

## Spark运行基本流程参见下面示意图

1.构建Spark Application的运行环境（启动SparkContext），SparkContext向资源管理器（可以是Standalone、Mesos或YARN）注册并申请运行Executor资源； 
2.资源管理器分配Executor资源并启动StandaloneExecutorBackend，Executor运行情况将随着心跳发送到资源管理器上； 
3.SparkContext构建成DAG图，将DAG图分解成Stage，并把Taskset发送给Task Scheduler。Executor向SparkContext申请Task，Task Scheduler将Task发放给Executor运行同时SparkContext将应用程序代码发放给Executor。 
4.Task在Executor上运行，运行完毕释放所有资源。

![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow1.png)

*Spark运行架构特点：*

每个Application获取专属的executor进 程，该进程在Application期间一直驻留，并以多线程方式运行tasks。这种Application隔离机制有其优势的，无论是从调度角度看 （每个Driver调度它自己的任务），还是从运行角度看（来自不同Application的Task运行在不同的JVM中）。当然，这也意味着 Spark Application不能跨应用程序共享数据，除非将数据写入到外部存储系统。
Spark与资源管理器无关，只要能够获取executor进程，并能保持相互通信就可以了。
提 交SparkContext的Client应该靠近Worker节点（运行Executor的节点)，最好是在同一个Rack里，因为Spark Application运行过程中SparkContext和Executor之间有大量的信息交换；如果想在远程集群中运行，最好使用RPC将 SparkContext提交给集群，不要远离Worker运行SparkContext。
Task采用了数据本地性和推测执行的优化机制。

### RDD

*特点*

总体而言，Spark采用RDD以后能够实现高效计算的主要原因如下：
1.高效的容错性。现有的分布式共享内存、键值存储、内存数据库等，为了实现容错，必须在集群节点之间进行数据复制或者记录日志，也就是在节点之间会发生大量的数据传输，这对于数据密集型应用而言会带来很大的开销。在RDD的设计中，数据只读，不可修改，如果需要修改数据，必须从父RDD转换到子RDD，由此在不同RDD之间建立了血缘关系。所以，RDD是一种天生具有容错机制的特殊集合，不需要通过数据冗余的方式（比如检查点）实现容错，而只需通过RDD父子依赖（血缘）关系重新计算得到丢失的分区来实现容错，无需回滚整个系统，这样就避免了数据复制的高开销，而且重算过程可以在不同节点之间并行进行，实现了高效的容错。此外，RDD提供的转换操作都是一些粗粒度的操作（比如map、filter和join），RDD依赖关系只需要记录这种粗粒度的转换操作，而不需要记录具体的数据和各种细粒度操作的日志（比如对哪个数据项进行了修改），这就大大降低了数据密集型应用中的容错开销；
2.中间结果持久化到内存。数据在内存中的多个RDD操作之间进行传递，不需要“落地”到磁盘上，避免了不必要的读写磁盘开销；
3.存放的数据可以是Java对象，避免了不必要的对象序列化和反序列化开销。

*RDD之间的依赖关系*

RDD中不同的操作会使得不同RDD中的分区会产生不同的依赖。RDD中的依赖关系分为窄依赖（Narrow Dependency）与宽依赖（Wide Dependency），图9-10展示了两种依赖之间的区别。
窄依赖表现为一个父RDD的分区对应于一个子RDD的分区，或多个父RDD的分区对应于一个子RDD的分区；比如图9-10(a)中，RDD1是RDD2的父RDD，RDD2是子RDD，RDD1的分区1，对应于RDD2的一个分区（即分区4）；再比如，RDD6和RDD7都是RDD8的父RDD，RDD6中的分区（分区15）和RDD7中的分区（分区18），两者都对应于RDD8中的一个分区（分区21）。
宽依赖则表现为存在一个父RDD的一个分区对应一个子RDD的多个分区。比如图9-10(b)中，RDD9是RDD12的父RDD，RDD9中的分区24对应了RDD12中的两个分区（即分区27和分区28）。
总体而言，如果父RDD的一个分区只被一个子RDD的一个分区所使用就是窄依赖，否则就是宽依赖。窄依赖典型的操作包括map、filter、union等，宽依赖典型的操作包括groupByKey、sortByKey等。对于连接（join）操作，可以分为两种情况。
1. 对输入进行协同划分，属于窄依赖（如图9-10(a)所示）。所谓协同划分（co-partitioned）是指多个父RDD的某一分区的所有“键（key）”，落在子RDD的同一个分区内，不会产生同一个父RDD的某一分区，落在子RDD的两个分区的情况。
2. 对输入做非协同划分，属于宽依赖，如图9-10(b)所示。
对于窄依赖的RDD，可以以流水线的方式计算所有父分区，不会造成网络之间的数据混合。对于宽依赖的RDD，则通常伴随着Shuffle操作，即首先需要计算好所有父分区数据，然后在节点之间进行Shuffle。


![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow2.jpg)

图9-10 窄依赖与宽依赖的区别

Spark的这种依赖关系设计，使其具有了天生的容错性，大大加快了Spark的执行速度。因为，RDD数据集通过“血缘关系”记住了它是如何从其它RDD中演变过来的，血缘关系记录的是粗颗粒度的转换操作行为，当这个RDD的部分分区数据丢失时，它可以通过血缘关系获取足够的信息来重新运算和恢复丢失的数据分区，由此带来了性能的提升。相对而言，在两种依赖关系中，窄依赖的失败恢复更为高效，它只需要根据父RDD分区重新计算丢失的分区即可（不需要重新计算所有分区），而且可以并行地在不同节点进行重新计算。而对于宽依赖而言，单个节点失效通常意味着重新计算过程会涉及多个父RDD分区，开销较大。此外，Spark还提供了数据检查点和记录日志，用于持久化中间RDD，从而使得在进行失败恢复时不需要追溯到最开始的阶段。在进行故障恢复时，Spark会对数据检查点开销和重新计算RDD分区的开销进行比较，从而自动选择最优的恢复策略。

*阶段的划分*

Spark通过分析各个RDD的依赖关系生成了DAG，再通过分析各个RDD中的分区之间的依赖关系来决定如何划分阶段，具体划分方法是：在DAG中进行反向解析，遇到宽依赖就断开，遇到窄依赖就把当前的RDD加入到当前的阶段中；将窄依赖尽量划分在同一个阶段中，可以实现流水线计算（具体的阶段划分算法请参见AMP实验室发表的论文《Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing》）。例如，如图9-11所示，假设从HDFS中读入数据生成3个不同的RDD（即A、C和E），通过一系列转换操作后再将计算结果保存回HDFS。对DAG进行解析时，在依赖图中进行反向解析，由于从RDD A到RDD B的转换以及从RDD B和F到RDD G的转换，都属于宽依赖，因此，在宽依赖处断开后可以得到三个阶段，即阶段1、阶段2和阶段3。可以看出，在阶段2中，从map到union都是窄依赖，这两步操作可以形成一个流水线操作，比如，分区7通过map操作生成的分区9，可以不用等待分区8到分区9这个转换操作的计算结束，而是继续进行union操作，转换得到分区13，这样流水线执行大大提高了计算的效率。


![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow3.jpg)

图9-11根据RDD分区的依赖关系划分阶段

由上述论述可知，把一个DAG图划分成多个“阶段”以后，每个阶段都代表了一组关联的、相互之间没有Shuffle依赖关系的任务组成的任务集合。每个任务集合会被提交给任务调度器（TaskScheduler）进行处理，由任务调度器将任务分发给Executor运行。

### RDD running
通过上述对RDD概念、依赖关系和阶段划分的介绍，结合之前介绍的Spark运行基本流程，这里再总结一下RDD在Spark架构中的运行过程（如图9-12所示）：
（1）创建RDD对象；
（2）SparkContext负责计算RDD之间的依赖关系，构建DAG；
（3）DAGScheduler负责把DAG图分解成多个阶段，每个阶段中包含了多个任务，每个任务会被任务调度器分发给各个工作节点（Worker Node）上的Executor去执行。

![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow6.jpg)

### DAG

*DAGScheduler*

DAGScheduler 把一个Spark作业转换成Stage的DAG（Directed Acyclic Graph有向无环图），根据RDD和Stage之间的关系找出开销最小的调度方法，然后把Stage以TaskSet的形式提交给 TaskScheduler，下图展示了DAGScheduler的作用：

![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow4.png)

*TaskScheduler*

DAGScheduler 决定了运行Task的理想位置，并把这些信息传递给下层的TaskScheduler。此外，DAGScheduler还处理由于Shuffle数据丢失 导致的失败，这有可能需要重新提交运行之前的Stage（非Shuffle数据丢失导致的Task失败由TaskScheduler处理）。 
TaskScheduler维护所有TaskSet，当Executor向Driver发送心跳时，TaskScheduler会根据其资源剩余情况分配 相应的Task。另外TaskScheduler还维护着所有Task的运行状态，重试失败的Task。下图展示了TaskScheduler的作用：

![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow5.png)

在不同运行模式中任务调度器具体为：
Spark on Standalone模式为TaskScheduler；
YARN-Client模式为YarnClientClusterScheduler
YARN-Cluster模式为YarnClusterScheduler


## Spark在不同集群中的运行架构

Spark 注重建立良好的生态系统，它不仅支持多种外部文件存储系统，提供了多种多样的集群运行模式。部署在单台机器上时，既可以用本地（Local）模式运行，也 可以使用伪分布式模式来运行；当以分布式集群部署的时候，可以根据自己集群的实际情况选择Standalone模式（Spark自带的模式）、YARN- Client模式或者YARN-Cluster模式。Spark的各种运行模式虽然在启动方式、运行位置、调度策略上各有不同，但它们的目的基本都是一致 的，就是在合适的位置安全可靠的根据用户的配置和Job的需要运行和管理Task。

### Spark on Standalone运行过程

Standalone 模式是Spark实现的资源调度框架，其主要的节点有Client节点、Master节点和Worker节点。其中Driver既可以运行在Master 节点上中，也可以运行在本地Client端。当用spark-shell交互式工具提交Spark的Job时，Driver在Master节点上运行；当 使用spark-submit工具提交Job或者在Eclips、IDEA等开发平台上使用”new SparkConf.setManager(“spark://master:7077”)”方式运行Spark任务时，Driver是运行在本地 Client端上的。
其运行过程如下：

1.SparkContext连接到Master，向Master注册并申请资源（CPU Core 和Memory）； 
2.Master根据SparkContext的资源申请要求和Worker心跳周期内报告的信息决定在哪个Worker上分配资源，然后在该Worker上获取资源，然后启动StandaloneExecutorBackend； 
3.StandaloneExecutorBackend向SparkContext注册； 
4.SparkContext将Applicaiton代码发送给StandaloneExecutorBackend；并且SparkContext解 析Applicaiton代码，构建DAG图，并提交给DAG Scheduler分解成Stage（当碰到Action操作时，就会催生Job；每个Job中含有1个或多个Stage，Stage一般在获取外部数据 和shuffle之前产生），然后以Stage（或者称为TaskSet）提交给Task Scheduler，Task Scheduler负责将Task分配到相应的Worker，最后提交给StandaloneExecutorBackend执行； 
5.StandaloneExecutorBackend会建立Executor线程池，开始执行Task，并向SparkContext报告，直至Task完成。 
6.所有Task完成后，SparkContext向Master注销，释放资源。

![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow7.png)


### Spark on YARN运行过程

YARN 是一种统一资源管理机制，在其上面可以运行多套计算框架。目前的大数据技术世界，大多数公司除了使用Spark来进行数据计算，由于历史原因或者单方面业 务处理的性能考虑而使用着其他的计算框架，比如MapReduce、Storm等计算框架。Spark基于此种情况开发了Spark on YARN的运行模式，由于借助了YARN良好的弹性资源管理机制，不仅部署Application更加方便，而且用户在YARN集群中运行的服务和 Application的资源也完全隔离，更具实践应用价值的是YARN可以通过队列的方式，管理同时运行在集群中的多个服务。 
Spark on YARN模式根据Driver在集群中的位置分为两种模式：一种是YARN-Client模式，另一种是YARN-Cluster（或称为YARN-Standalone模式）。

*YARN框架流程*
任何框架与YARN的结合，都必须遵循YARN的开发模式。在分析Spark on YARN的实现细节之前，有必要先分析一下YARN框架的一些基本原理。 
Yarn框架的基本运行流程图为：


![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow8.png)

其中，ResourceManager负责将集群的资源分配给各个应用使用，而资源分配和调度的基本单位是 Container，其中封装了机器资源，如内存、CPU、磁盘和网络等，每个任务会被分配一个Container，该任务只能在该Container中 执行，并使用该Container封装的资源。NodeManager是一个个的计算节点，主要负责启动Application所需的 Container，监控资源（内存、CPU、磁盘和网络等）的使用情况并将之汇报给ResourceManager。ResourceManager与 NodeManagers共同组成整个数据计算框架，ApplicationMaster与具体的Application相关，主要负责同 ResourceManager协商以获取合适的Container，并跟踪这些Container的状态和监控其进度。


#### YARN-Client

Yarn-Client模式中，Driver在客户端本地运行，这种模式可以使得Spark Application和客户端进行交互，因为Driver在客户端，所以可以通过webUI访问Driver的状态，默认是http://hadoop1:8080访问，而YARN通过http:// hadoop1:8088访问。 

YARN-client的工作流程分为以下几个步骤：


![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow9.png)

1.Spark Yarn Client向YARN的ResourceManager申请启动Application Master。同时在SparkContent初始化中将创建DAGScheduler和TASKScheduler等，由于我们选择的是Yarn- Client模式，程序会选择YarnClientClusterScheduler和YarnClientSchedulerBackend； 
2.ResourceManager收到请求后，在集群中选择一个NodeManager，为该应用程序分配第一个Container，要求它在这个 Container中启动应用程序的ApplicationMaster，与YARN-Cluster区别的是在该ApplicationMaster不 运行SparkContext，只与SparkContext进行联系进行资源的分派； 
3.Client中的SparkContext初始化完毕后，与ApplicationMaster建立通讯，向ResourceManager注册，根据任务信息向ResourceManager申请资源（Container）； 
4.一旦ApplicationMaster申请到资源（也就是Container）后，便与对应的NodeManager通信，要求它在获得的 Container中启动启动CoarseGrainedExecutorBackend，CoarseGrainedExecutorBackend启 动后会向Client中的SparkContext注册并申请Task； 
5.Client中的SparkContext分配Task给CoarseGrainedExecutorBackend执 行，CoarseGrainedExecutorBackend运行Task并向Driver汇报运行的状态和进度，以让Client随时掌握各个任务的 运行状态，从而可以在任务失败时重新启动任务； 
6.应用程序运行完成后，Client的SparkContext向ResourceManager申请注销并关闭自己。

#### YARN-Cluster

在 YARN-Cluster模式中，当用户向YARN中提交一个应用程序后，YARN将分两个阶段运行该应用程序：第一个阶段是把Spark的Driver 作为一个ApplicationMaster在YARN集群中先启动；第二个阶段是由ApplicationMaster创建应用程序，然后为它向 ResourceManager申请资源，并启动Executor来运行Task，同时监控它的整个运行过程，直到运行完成。 

YARN-cluster的工作流程分为以下几个步骤：


![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow10.png)


1.Spark Yarn Client向YARN中提交应用程序，包括ApplicationMaster程序、启动ApplicationMaster的命令、需要在Executor中运行的程序等； 
2.ResourceManager收到请求后，在集群中选择一个NodeManager，为该应用程序分配第一个Container，要求它在这个 Container中启动应用程序的ApplicationMaster，其中ApplicationMaster进行SparkContext等的初始 化； 
3.ApplicationMaster向ResourceManager注册，这样用户可以直接通过ResourceManage查看应用程序的运行状态，然后它将采用轮询的方式通过RPC协议为各个任务申请资源，并监控它们的运行状态直到运行结束； 
4.一旦ApplicationMaster申请到资源（也就是Container）后，便与对应的NodeManager通信，要求它在获得的 Container中启动启动CoarseGrainedExecutorBackend，CoarseGrainedExecutorBackend启 动后会向ApplicationMaster中的SparkContext注册并申请Task。这一点和Standalone模式一样，只不过 SparkContext在Spark Application中初始化时，使用CoarseGrainedSchedulerBackend配合YarnClusterScheduler进行 任务的调度，其中YarnClusterScheduler只是对TaskSchedulerImpl的一个简单包装，增加了对Executor的等待逻 辑等； 
5.ApplicationMaster中的SparkContext分配Task给CoarseGrainedExecutorBackend执 行，CoarseGrainedExecutorBackend运行Task并向ApplicationMaster汇报运行的状态和进度，以让 ApplicationMaster随时掌握各个任务的运行状态，从而可以在任务失败时重新启动任务； 
6.应用程序运行完成后，ApplicationMaster向ResourceManager申请注销并关闭自己。


### YARN-Client 与 YARN-Cluster 区别

理 解YARN-Client和YARN-Cluster深层次的区别之前先清楚一个概念：Application Master。在YARN中，每个Application实例都有一个ApplicationMaster进程，它是Application启动的第一个 容器。它负责和ResourceManager打交道并请求资源，获取资源之后告诉NodeManager为其启动Container。从深层次的含义讲 YARN-Cluster和YARN-Client模式的区别其实就是ApplicationMaster进程的区别。

*.YARN- Cluster模式下，Driver运行在AM(Application Master)中，它负责向YARN申请资源，并监督作业的运行状况。当用户提交了作业之后，就可以关掉Client，作业会继续在YARN上运行，因而 YARN-Cluster模式不适合运行交互类型的作业；

![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow11.png)

*.YARN-Client模式下，Application Master仅仅向YARN请求Executor，Client会和请求的Container通信来调度他们工作，也就是说Client不能离开。

![](https://github.com/XGWang0/wiki/raw/master/_images/rdd_running_flow12.png)
