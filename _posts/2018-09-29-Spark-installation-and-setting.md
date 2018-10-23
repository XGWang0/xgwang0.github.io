---
layout: post
title:  "(二)Spark installation and setting"
categories: Spark
tags:  bigdata structure mapreduce spark
author: Root Wang
---

* content
{:toc}


## Spark env setting:

### HA Setting

1.创建`spark-env.sh` 并加入以下内容：

```doc
#端口
export SPARK_MASTER_PORT=7077
#指定可用的CPU内核数量(默认:所有可用，实际使用时没有配置最后这两个参数)
export SPARK_WORKER_CORES=2
#作业可使用的内存容量，默认格式为1000m或者2g(默认:所有RAM去掉给操作系统用的1GB)
export SPARK_WORKER_MEMORY=2g

#zookeeper 设置， HA使用
export SPARK_DAEMON_JAVA_OPTS="-Dspark.deploy.recoveryMode=ZOOKEEPER -Dspark.deploy.zookeeper.url=master:2181,openqa:2181,hadoop-slave2:2181 -Dspark.deploy.zookeeper.dir=/spark"

# This seting is for yarn/hadoop env
export HADOOP_CONF_DIR=/opt/hadoop-2.9.1/etc/hadoop

```

2.slave 设置：
将会在slave文件所添加的主机中启动worker

```doc
hadoop-slave2
master
openqa
```

3.同步以上所有文件到HA的其他节点 （本文为zookeeper 的所有节点）


4.开始zookeeper服务在所有节点上

```sh
zkServer.sh start
``

5.开始dfs所有服务

```sh
start-all.sh
```

6.开始spark服务在主节点上

```sh
sbin/start-all.sh
```

7.开始spark master实例在其他节点上

```sh
sbin/start-master.sh
```

8.验证spark HA
访问 http://{node}:8080,
只有主节点为active状态， 其他为standby状态。
kill 主节点master进程， 其他节点将会选举出新的active Spark


### Start on local

```sh
bin/pyspark 
```

### Start on Hadoop

```sh
bin/pyspark --master spark://master:7077
```

### Start on Yarn
```sh
bin/pyspark --master yarn -deploy-mode client
```
