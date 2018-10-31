---
layout: post
title:  "MapReduce structure and workflow"
categories: mapreduce
tags:  bigdata structure hadoop mapreduce
author: Root Wang
---

* content
{:toc}

### Brief

MapReduce讲的就是分而治之的程序处理理念，把一个复杂的任务划分为若干个简单的任务分别来做。另外，就是程序的调度问题，哪些任务给哪些Mapper来处理是一个着重考虑的问题。MapReduce的根本原则是信息处理的本地化，哪台PC持有相应要处理的数据，哪台PC就负责处理该部分的数据，这样做的意义在于可以减少网络通讯负担。

![](https://github.com/XGWang0/wiki/raw/master/_images/mapreduce_strucutre_workflow_1.jpg)

### MapReduce执行流程
1.客户端提交一个作业
2.JobClient与JobTracker通信，JobTracker返回一个JobID
3.JobClient复制作业资源文件

> 将运行作业所需要的资源文件复制到HDFS上，包括MapReduce程序打包的JAR文件、配置文件和客户端计算所得的输入划分信息。这些文件都存放在JobTracker专门为该作业创建的文件夹中。文件夹名为该作业的Job ID。JAR文件默认会有10个副本（mapred.submit.replication属性控制）；输入划分信息告诉了JobTracker应该为这个作业启动多少个map任务等信息。

4.开始提交任务（任务的描述信息：包括jobid，jar存放的位置，配置信息等等）
5.初始化任务。创建作业对象

>JobTracker接收到作业后，将其放在一个作业队列里，等待作业调度器对其进行调度

6.对HDFS上的资源文件进行分片，每一个分片对应一个MapperTask

> 当作业调度器根据自己的调度算法调度到该作业时，会根据输入划分信息为每个划分创建一个map任务，并将map任务分配给TaskTracker执行

7.TaskTracker会向JobTracker返回一个心跳信息（任务的描述信息），根据心跳信息分配任务

> TaskTracker每隔一段时间会给JobTracker发送一个心跳，告诉JobTracker它依然在运行，同时心跳中还携带着很多的信息，比如当前map任务完成的进度等信息。当JobTracker收到作业的最后一个任务完成信息时，便把该作业设置成“成功”。当JobClient查询状态时，它将得知任务已完成，便显示一条消息给用户。

8.TaskTracker从HDFS上获取作业资源文件

> 对于map和reduce任务，TaskTracker根据主机核的数量和内存的大小有固定数量的map槽和reduce槽。这里需要强调的是：map任务不是随随便便地分配给某个TaskTracker的，这里有个概念叫：数据本地化（Data-Local）。意思是：将map任务分配给含有该map处理的数据块的TaskTracker上，同时将程序JAR包复制到该TaskTracker上来运行，这叫“运算移动，数据不移动”。而分配reduce任务时并不考虑数据本地化。

9.登录到子JVM

10.TaskTracker启动一个child进程来执行具体任务

![](https://github.com/XGWang0/wiki/raw/master/_images/mapreduce_strucutre_workflow_2.jpeg)

-----------------------------

### Map Reduce works in details

#### Map端：
1．每个输入分片会让一个map任务来处理，默认情况下，以HDFS的一个块的大小（默认为64M）为一个分片，当然我们也可以设置块的大小。map输出的结果会暂且放在一个环形内存缓冲区中（该缓冲区的大小默认为100M，由io.sort.mb属性控制），当该缓冲区快要溢出时（默认为缓冲区大小的80%，由io.sort.spill.percent属性控制），会在本地文件系统中创建一个溢出文件，将该缓冲区中的数据写入这个文件。

2．在写入磁盘之前，线程首先根据reduce任务的数目将数据划分为相同数目的分区，也就是一个reduce任务对应一个分区的数据。这样做是为了避免有些reduce任务分配到大量数据，而有些reduce任务却分到很少数据，甚至没有分到数据的尴尬局面。其实分区就是对数据进行hash的过程。然后对每个分区中的数据进行排序，如果此时设置了Combiner，将排序后的结果进行Combia操作，这样做的目的是让尽可能少的数据写入到磁盘。

3．当map任务输出最后一个记录时，可能会有很多的溢出文件，这时需要将这些文件合并。合并的过程中会不断地进行排序和combia操作，目的有两个：1.尽量减少每次写入磁盘的数据量；2.尽量减少下一复制阶段网络传输的数据量。最后合并成了一个已分区且已排序的文件。为了减少网络传输的数据量，这里可以将数据压缩，只要将mapred.compress.map.out设置为true就可以了。

4．将分区中的数据拷贝给相对应的reduce任务。有人可能会问：分区中的数据怎么知道它对应的reduce是哪个呢？其实map任务一直和其父TaskTracker保持联系，而TaskTracker又一直和JobTracker保持心跳。所以JobTracker中保存了整个集群中的宏观信息。只要reduce任务向JobTracker获取对应的map输出位置就ok了哦。

#### Reduce端：
1．Reduce会接收到不同map任务传来的数据，并且每个map传来的数据都是有序的。如果reduce端接受的数据量相当小，则直接存储在内存中（缓冲区大小由mapred.job.shuffle.input.buffer.percent属性控制，表示用作此用途的堆空间的百分比），如果数据量超过了该缓冲区大小的一定比例（由mapred.job.shuffle.merge.percent决定），则对数据合并后溢写到磁盘中。

2．随着溢写文件的增多，后台线程会将它们合并成一个更大的有序的文件，这样做是为了给后面的合并节省时间。其实不管在map端还是reduce端，MapReduce都是反复地执行排序，合并操作，现在终于明白了有些人为什么会说：排序是hadoop的灵魂。

3．合并的过程中会产生许多的中间文件（写入磁盘了），但MapReduce会让写入磁盘的数据尽可能地少，并且最后一次合并的结果并没有写入磁盘，而是直接输入到reduce函数


### Sample

从word count这个实例来理解MapReduce。MapReduce大体上分为六个步骤：input, split, map, shuffle, reduce, output。细节描述如下：

1.输入(input)：如给定一个文档，包含如下四行：
Hello Java
Hello C
Hello Java
Hello C++

2. 拆分(split)：将上述文档中每一行的内容转换为key-value对，即：

0 - Hello Java
1 - Hello C
2 – Hello Java
3 - Hello C++

3. 映射(map)：将拆分之后的内容转换成新的key-value对，即：

(Hello , 1)
(Java , 1)
(Hello , 1)
(C , 1)
(Hello , 1)
(Java , 1)
(Hello , 1)
(C++ , 1)

4. 派发(shuffle)：将key相同的扔到一起去，即：

(Hello , 1)
(Hello , 1)
(Hello , 1)
(Hello , 1)
(Java , 1)
(Java , 1)
(C , 1)
(C++ , 1)
注意：这一步需要移动数据，原来的数据可能在不同的datanode上，这一步过后，相同key的数据会被移动到同一台机器上。最终，它会返回一个list包含各种k-value对，即：

{ Hello: 1,1,1,1}
{Java: 1,1}
{C: 1}
{C++: 1}

5. 缩减(reduce)：把同一个key的结果加在一起。如：

(Hello , 4)
(Java , 2)
(C , 1)
(C++,1)

6. 输出(output): 输出缩减之后的所有结果。

