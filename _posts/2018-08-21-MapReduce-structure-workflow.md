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

