---
layout: post
title:  "hadoop Yarn structure and configuration setting"
categories: hadoop
tags:  bigdata structure hadoop Yarn
author: Root Wang
---

* content
{:toc}
## Yarn简介
  Yarn是Hadoop集群的资源管理系统。Hadoop2.0对MapReduce框架做了彻底的设计重构，我们称Hadoop2.0中的MapReduce为MRv2或者Yarn，它主要包括两部分功能：

1. ResourceManagement 资源管理
2. JobScheduling/JobMonitoring 任务调度监控

到了Hadoop2.x也就是Yarn，它的目标是将这两部分功能分开，也就是分别用两个进程来管理这两个任务：

1. ResourceManger
2. ApplicationMaster

需要注意的是，在Yarn中我们把job的概念换成了application，因为在新的Hadoop2.x中，运行的应用不只是MapReduce了，还有可能是其它应用如一个DAG（有向无环图Directed Acyclic Graph，例如storm应用）。Yarn的另一个目标就是拓展Hadoop，使得它不仅仅可以支持MapReduce计算，还能很方便的管理诸如Hive、Hbase、Pig、Spark/Shark等应用。这种新的架构设计能够使得各种类型的应用运行在Hadoop上面，并通过Yarn从系统层面进行统一的管理，也就是说，有了Yarn，各种应用就可以互不干扰的运行在同一个Hadoop系统中，共享整个集群资源，如下图所示： 


![](https://github.com/XGWang0/wiki/raw/master/_images/yarn_strucutre-chart1.png)

## Yarn的组件及架构
Yarn主要由以下几个组件组成：

1. ResourceManager：Global（全局）的进程 
2. NodeManager：运行在每个节点上的进程
3. ApplicationMaster：Application-specific（应用级别）的进程
   *Scheduler：是ResourceManager的一个组件*
   *Container：节点上一组CPU和内存资源*

Container是Yarn对计算机计算资源的抽象，它其实就是一组CPU和内存资源，所有的应用都会运行在Container中。ApplicationMaster是对运行在Yarn中某个应用的抽象，它其实就是某个类型应用的实例，ApplicationMaster是应用级别的，它的主要功能就是向ResourceManager（全局的）申请计算资源（Containers）并且和NodeManager交互来执行和监控具体的task。Scheduler是ResourceManager专门进行资源管理的一个组件，负责分配NodeManager上的Container资源，NodeManager也会不断发送自己Container使用情况给ResourceManager。

ResourceManager和NodeManager两个进程主要负责系统管理方面的任务。ResourceManager有一个Scheduler，负责各个集群中应用的资源分配。对于每种类型的每个应用，都会对应一个ApplicationMaster实例，ApplicationMaster通过和ResourceManager沟通获得Container资源来运行具体的job，并跟踪这个job的运行状态、监控运行进度。

下面我们看一下整个Yarn的架构图： 

![](https://github.com/XGWang0/wiki/raw/master/_images/yarn_strucutre-chart2.png)


## Yarn的组件详解
**Container**
  Container是Yarn框架的计算单元，是具体执行应用task（如map task、reduce task）的基本单位。Container和集群节点的关系是：一个节点会运行多个Container，但一个Container不会跨节点。

一个Container就是一组分配的系统资源，现阶段只包含两种系统资源（之后可能会增加磁盘、网络等资源）：
* CPU core
* Memory in MB

既然一个Container指的是具体节点上的计算资源，这就意味着Container中必定含有计算资源的位置信息：计算资源位于哪个机架的哪台机器上。所以我们在请求某个Container时，其实是向某台机器发起的请求，请求的是这台机器上的CPU和内存资源。

任何**一个job或application必须运行在一个或多个Container中**，在Yarn框架中，ResourceManager只负责告诉ApplicationMaster哪些Containers可以用，ApplicationMaster还需要去找NodeManager请求分配具体的Container。

**Node Manager**
  NodeManager进程运行在集群中的节点上，每个节点都会有自己的NodeManager。NodeManager是一个slave服务：它负责接收ResourceManager的资源分配请求，分配具体的Container给应用。同时，它还负责监控并报告Container使用信息给ResourceManager。通过和ResourceManager配合，NodeManager负责整个Hadoop集群中的资源分配工作。ResourceManager是一个全局的进程，而NodeManager只是每个节点上的进程，管理这个节点上的资源分配和监控运行节点的健康状态。下面是NodeManager的具体任务列表：

- 接收ResourceManager的请求，分配Container给应用的某个任务
- 和ResourceManager交换信息以确保整个集群平稳运行。ResourceManager就是通过收集每个NodeManager的报告信息来追踪整个集群健康状态的，而NodeManager负责监控自身的健康状态。
- 管理每个Container的生命周期
- 管理每个节点上的日志
- 执行Yarn上面应用的一些额外的服务，比如MapReduce的shuffle过程

当一个节点启动时，它会向ResourceManager进行注册并告知ResourceManager自己有多少资源可用。在运行期，通过NodeManager和ResourceManager协同工作，这些信息会不断被更新并保障整个集群发挥出最佳状态。

NodeManager只负责管理自身的Container，它并不知道运行在它上面应用的信息。负责管理应用信息的组件是ApplicationMaster，在后面会讲到。

**Resource Manager**
ResourceManager主要有两个组件：Scheduler和ApplicationManager。

Scheduler是一个资源调度器，它主要负责协调集群中各个应用的资源分配，保障整个集群的运行效率。Scheduler的角色是一个纯调度器，它只负责调度Containers，不会关心应用程序监控及其运行状态等信息。同样，它也不能重启因应用失败或者硬件错误而运行失败的任务

Scheduler是一个可插拔的插件，它可以调度集群中的各种队列、应用等。在Hadoop的MapReduce框架中主要有两种Scheduler：Capacity Scheduler和Fair Scheduler，关于这两个调度器后面会详细介绍。

另一个组件ApplicationManager主要负责接收job的提交请求，为应用分配第一个Container来运行ApplicationMaster，还有就是负责监控ApplicationMaster，在遇到失败时重启ApplicationMaster运行的Container。

**Application Master**
ApplicationMaster的主要作用是向ResourceManager申请资源并和NodeManager协同工作来运行应用的各个任务然后跟踪它们状态及监控各个任务的执行，遇到失败的任务还负责重启它。

在MR1中，JobTracker即负责job的监控，又负责系统资源的分配。而在MR2中，资源的调度分配由ResourceManager专门进行管理，而每个job或应用的管理、监控交由相应的分布在集群中的ApplicationMaster，如果某个ApplicationMaster失败，ResourceManager还可以重启它，这大大提高了集群的拓展性。

在MR1中，Hadoop架构只支持MapReduce类型的job，所以它不是一个通用的框架，因为Hadoop的JobTracker和TaskTracker组件都是专门针对MapReduce开发的，它们之间是深度耦合的。Yarn的出现解决了这个问题，关于Job或应用的管理都是由ApplicationMaster进程负责的，Yarn允许我们自己开发ApplicationMaster，我们可以为自己的应用开发自己的ApplicationMaster。这样每一个类型的应用都会对应一个ApplicationMaster，一个ApplicationMaster其实就是一个类库。这里要区分ApplicationMaster*类库和ApplicationMaster实例*，一个ApplicationMaster类库何以对应多个实例，就行java语言中的类和类的实例关系一样。总结来说就是，每种类型的应用都会对应着一个ApplicationMaster，每个类型的应用都可以启动多个ApplicationMaster实例。所以，在yarn中，是每个job都会对应一个ApplicationMaster而不是每类。

Yarn 框架相对于老的 MapReduce 框架什么优势呢？

- 这个设计大大减小了 ResourceManager 的资源消耗，并且让监测每一个 Job 子任务 (tasks) 状态的程序分布式化了，更安全、更优美。
- 在新的 Yarn 中，ApplicationMaster 是一个可变更的部分，用户可以对不同的编程模型写自己的 AppMst，让更多类型的编程模型能够跑在 Hadoop 集群中，可以参考 hadoop Yarn 官方配置模板中的 ``mapred-site.xml`` 配置。
- 对于资源的表示以内存为单位 ( 在目前版本的 Yarn 中，没有考虑 cpu 的占用 )，比之前以剩余 slot 数目更合理。
- 老的框架中，JobTracker 一个很大的负担就是监控 job 下的 tasks 的运行状况，现在，这个部分就扔给 ApplicationMaster 做了，而 ResourceManager 中有一个模块叫做 ApplicationsManager，它是监测 ApplicationMaster 的运行状况，如果出问题，会将其在其他机器上重启。
- Container 是 Yarn 为了将来作资源隔离而提出的一个框架。这一点应该借鉴了 Mesos 的工作，目前是一个框架，仅仅提供 java 虚拟机内存的隔离 ,hadoop 团队的设计思路应该后续能支持更多的资源调度和控制 , 既然资源表示成内存量，那就没有了之前的 map slot/reduce slot 分开造成集群资源闲置的尴尬情况。

## Yarn request分析
**应用提交过程分析**
了解了上面介绍的这些概念，我们有必要看一下Application在Yarn中的执行过程，整个执行过程可以总结为三步：

1. 应用程序提交
2. 启动应用的ApplicationMaster实例
3. ApplicationMaster实例管理应用程序的执行
下面这幅图展示了应用程序的整个执行过程：

![](https://github.com/XGWang0/wiki/raw/master/_images/yarn_strucutre-chart3.png)

1. 客户端程序向ResourceManager提交应用并请求一个ApplicationMaster实例

2. ResourceManager找到可以运行一个Container的NodeManager，并在这个Container中启动ApplicationMaster实例

3. ApplicationMaster向ResourceManager进行注册，注册之后客户端就可以查询ResourceManager获得自己ApplicationMaster的详细信息，以后就可以和自己的ApplicationMaster直接交互了

4. 在平常的操作过程中，ApplicationMaster根据resource-request协议向ResourceManager发送resource-request请求

5. 当Container被成功分配之后，ApplicationMaster通过向NodeManager发送container-launch-specification信息来启动Container， container-launch-specification信息包含了能够让Container和ApplicationMaster交流所需要的资料

6. 应用程序的代码在启动的Container中运行，并把运行的进度、状态等信息通过application-specific协议发送给ApplicationMaster

7. 在应用程序运行期间，提交应用的客户端主动和ApplicationMaster交流获得应用的运行状态、进度更新等信息，交流的协议也是application-specific协议

8. 一但应用程序执行完成并且所有相关工作也已经完成，ApplicationMaster向ResourceManager取消注册然后关闭，用到所有的Container也归还给系统

**Resource Request和Container**
  Yarn的设计目标就是允许我们的各种应用以共享、安全、多租户的形式使用整个集群。并且，为了保证集群资源调度和数据访问的高效性，Yarn还必须能够感知整个集群拓扑结构。为了实现这些目标，ResourceManager的调度器Scheduler为应用程序的资源请求定义了一些灵活的协议，通过它就可以对运行在集群中的各个应用做更好的调度，因此，这就诞生了Resource Request和Container。

  具体来讲，一个应用先向ApplicationMaster发送一个满足自己需求的资源请求，然后ApplicationMaster把这个资源请求以resource-request的形式发送给ResourceManager的Scheduler，Scheduler再在这个原始的resource-request中返回分配到的资源描述Container。每个ResourceRequest可看做一个可序列化Java对象，包含的字段信息如下：

<resource-name, priority, resource-requirement, number-of-containers>
* resource-name：资源名称，现阶段指的是资源所在的host和rack，后期可能还会支持虚拟机或者更复杂的网络结构

* priority：资源的优先级

* resource-requirement：资源的具体需求，现阶段指内存和cpu需求的数量

* number-of-containers：满足需求的Container的集合

**number-of-containers中的Containers就是ResourceManager给ApplicationMaster分配资源的结果。Container就是授权给应用程序可以使用某个节点机器上CPU和内存的数量。**

ApplicationMaster在得到这些Containers后，还需要与分配Container所在机器上的NodeManager交互来启动Container并运行相关任务。当然Container的分配是需要认证的，以防止ApplicationMaster自己去请求集群资源。

## 参数配置
### Related configuration overview
关于Yarn内存分配与管理，主要涉及到了`ResourceManage`、`ApplicationMatser`、`NodeManager`这几个概念，相关的优化也要紧紧围绕着这几方面来开展。这里还有一个`Container`的概念，现在可以先把它理解为运行map/reduce task的容器，后面有详细介绍。


### ResouceManage 内存资源配置 (配置的是资源调度相关)
>RM1：yarn.scheduler.minimum-allocation-mb 分配给AM单个容器可申请的最小内存 
>RM2：yarn.scheduler.maximum-allocation-mb 分配给AM单个容器可申请的最大内存 
>> 最小值可以计算一个节点最大Container数量
>> 一旦设置，不可动态改变

### NodeManage的内存资源配置 (配置的是硬件资源相关)
>NM1：yarn.nodemanager.resource.memory-mb 节点最大可用内存 
>NM2：yarn.nodemanager.vmem-pmem-ratio 虚拟内存率，默认2.1 
>注：
>> RM1、RM2的值均不能大于NM1的值
>> NM1可以计算节点最大最大Container数量，max(Container)=NM1/RM1
>> 一旦设置，不可动态改变

### ApplicationManage内存配置相关参数 (配置的是任务相关)
>AM1：mapreduce.map.memory.mb 分配给map Container的内存大小 
>AM2：mapreduce.reduce.memory.mb 分配给reduce Container的内存大小
>注：
>>这两个值应该在RM1和RM2这两个值之间
>>AM2的值最好为AM1的两倍
>>这两个值可以在启动时改变


>AM3：mapreduce.map.java.opts 运行map任务的jvm参数，如-Xmx，-Xms等选项 
>AM4：mapreduce.reduce.java.opts 运行reduce任务的jvm参数，如-Xmx，-Xms等选项 
>注：
>>这两个值应该在AM1和AM2之间

### 任务提交
**流程**
1. 用户将应用程序提交到ResourceManager上；
2. ResourceManager为应用程序ApplicationMaster申请资源，并与某个NodeManager通信，以启动ApplicationMaster；
3. ApplicationMaster与ResourceManager通信，为内部要执行的任务申请资源，一旦得到资源后，将于NodeManager通信，以启动对应的任务。
4. 所有任务运行完成后，ApplicationMaster向ResourceManager注销，整个应用程序运行结束。

![](https://github.com/XGWang0/wiki/raw/master/_images/yarn_instance_struct.png)

**Container**
1. Container是YARN中资源的抽象，它封装了某个节点上一定量的资源（CPU和内存两类资源）。它跟Linux Container没有任何关系，仅仅是YARN提出的一个概念（从实现上看，可看做一个可序列化/反序列化的Java类）。 
2. Container由ApplicationMaster向ResourceManager申请的，由ResouceManager中的资源调度器异步分配给ApplicationMaster； 
3. Container的运行是由ApplicationMaster向资源所在的NodeManager发起的，Container运行时需提供内部执行的任务命令（可以使任何命令，比如java、Python、C++进程启动命令均可）以及该命令执行所需的环境变量和外部资源（比如词典文件、可执行文件、jar包等）。 

另外，一个应用程序所需的Container分为两大类，如下： 
* 运行ApplicationMaster的Container：这是由ResourceManager（向内部的资源调度器）申请和启动的，用户提交应用程序时，可指定唯一的ApplicationMaster所需的资源； 
* 运行各类任务的Container：这是由ApplicationMaster向ResourceManager申请的，并由ApplicationMaster与NodeManager通信以启动之。 
以上两类Container可能在任意节点上，它们的位置通常而言是随机的，即ApplicationMaster可能与它管理的任务运行在一个节点上。 
Container是YARN中最重要的概念之一，懂得该概念对于理解YARN的资源模型至关重要，望大家好好理解。 

注意：map/reduce task是运行在Container之中的，所以上面提到的mapreduce.map(reduce).memory.mb大小都大于mapreduce.map(reduce).java.opts值的大小。



## 概念理解
![](https://github.com/XGWang0/wiki/raw/master/_images/yarn_parm_understanding.jpeg)

如上图所示，先看最下面褐色部分， 
AM参数mapreduce.map.memory.mb=1536MB，表示AM要为map Container申请1536MB资源，但RM实际分配的内存却是2048MB，因为yarn.scheduler.mininum-allocation-mb=1024MB，这定义了RM最小要分配1024MB，1536MB超过了这个值，所以实际分配给AM的值为2048MB(这涉及到了规整化因子，关于规整化因子，在本文最后有介绍)。 
AM参数mapreduce.map.java.opts=-Xmx 1024m，表示运行map任务的jvm内存为1024MB,因为map任务要运行在Container里面，所以这个参数的值略微小于mapreduce.map.memory.mb=1536MB这个值。 
NM参数yarn.nodemanager.vmem-pmem-radio=2.1,这表示NodeManager可以分配给map/reduce Container 2.1倍的虚拟内存，安照上面的配置，实际分配给map Container容器的虚拟内存大小为2048*2.1=3225.6MB，若实际用到的内存超过这个值，NM就会kill掉这个map Container,任务执行过程就会出现异常。 
AM参数mapreduce.reduce.memory.mb=3072MB，表示分配给reduce Container的容器大小为3072MB,而map Container的大小分配的是1536MB，从这也看出，reduce Container容器的大小最好是map Container大小的两倍。 
NM参数yarn.nodemanager.resource.mem.mb=24576MB,这个值表示节点分配给NodeManager的可用内存，也就是节点用来执行yarn任务的内存大小。这个值要根据实际服务器内存大小来配置，比如我们hadoop集群机器内存是128GB，我们可以分配其中的80%给yarn，也就是102GB。 
上图中RM的两个参数分别1024MB和8192MB，分别表示分配给AM map/reduce Container的最大值和最小值。





## HDP平台参数调优建议
* 内存分配
>Reserved Memory = Reserved for stack memory + Reserved for HBase Memory (If HBase is on the same node) 
>系统总内存126GB，预留给操作系统24GB，如果有Hbase再预留给Hbase24GB。 
>下面的计算假设Datanode节点部署了Hbase。

* containers 计算：
>MIN_CONTAINER_SIZE = 2048 MB
>containers = min (2*CORES, 1.8*DISKS, (Total available RAM) / MIN_CONTAINER_SIZE)
>containers = min (2*12, 1.8*12, (78 * 1024) / 2048)
>containers = min (24,21.6,39)
>containers = 22

* container 内存计算：
>RAM-per-container = max(MIN_CONTAINER_SIZE, (Total Available RAM) / containers))
>RAM-per-container = max(2048, (78 * 1024) / 22))
>RAM-per-container = 3630 MB

* Yarn 和 Mapreduce 参数配置：
>yarn.nodemanager.resource.memory-mb = containers * RAM-per-container
>yarn.scheduler.minimum-allocation-mb  = RAM-per-container
>yarn.scheduler.maximum-allocation-mb  = containers * RAM-per-container
>mapreduce.map.memory.mb          = RAM-per-container
>mapreduce.reduce.memory.mb      = 2 * RAM-per-container
>mapreduce.map.java.opts          = 0.8 * RAM-per-container
>mapreduce.reduce.java.opts          = 0.8 * 2 * RAM-per-container
>yarn.nodemanager.resource.memory-mb = 22 * 3630 MB
>yarn.scheduler.minimum-allocation-mb     = 3630 MB
>yarn.scheduler.maximum-allocation-mb    = 22 * 3630 MB
>mapreduce.map.memory.mb             = 3630 MB
>mapreduce.reduce.memory.mb         = 22 * 3630 MB
>mapreduce.map.java.opts             = 0.8 * 3630 MB
>mapreduce.reduce.java.opts             = 0.8 * 2 * 3630 MB

附：规整化因子介绍

为了易于管理资源和调度资源，Hadoop YARN内置了资源规整化算法，它规定了最小可申请资源量、最大可申请资源量和资源规整化因子，如果应用程序申请的资源量小于最小可申请资源量，则YARN会将其大小改为最小可申请量，也就是说，应用程序获得资源不会小于自己申请的资源，但也不一定相等；如果应用程序申请的资源量大于最大可申请资源量，则会抛出异常，无法申请成功；规整化因子是用来规整化应用程序资源的，应用程序申请的资源如果不是该因子的整数倍，则将被修改为最小的整数倍对应的值，公式为ceil(a/b)*b，其中a是应用程序申请的资源，b为规整化因子。 
比如，在yarn-site.xml中设置，相关参数如下：

yarn.scheduler.minimum-allocation-mb：最小可申请内存量，默认是1024
yarn.scheduler.minimum-allocation-vcores：最小可申请CPU数，默认是1
yarn.scheduler.maximum-allocation-mb：最大可申请内存量，默认是8096
yarn.scheduler.maximum-allocation-vcores：最大可申请CPU数，默认是4

对于规整化因子，不同调度器不同，具体如下： 
FIFO和Capacity Scheduler，规整化因子等于最小可申请资源量，不可单独配置。 
Fair Scheduler：规整化因子通过参数yarn.scheduler.increment-allocation-mb和yarn.scheduler.increment-allocation-vcores设置，默认是1024和1。 
通过以上介绍可知，应用程序申请到资源量可能大于资源申请的资源量，比如YARN的最小可申请资源内存量为1024，规整因子是1024，如果一个应用程序申请1500内存，则会得到2048内存，如果规整因子是512，则得到1536内存。
