---
layout: post
title:  "hadoop installation"
categories: hadoop
tags:  bigdata structure hadoop 
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

##Setting basic environemnt##
**SSH connection without password**
1. Generate key for ssh on all machines
```sh
ssh-keygen  -t   rsa   -P  1024
```

2. Copy all machines\'s key `~/.ssh/id_dsa.pub` content to authorized_keys, need to create file authorized_keys if it missing

3. Upload authorized_keys file to all machines

4. Set permission for following folder and file
```sh
chmod 700/755 ~/.ssh
chmod 600 authorized_keys
```

5. Verify ssh connection without password

**Set hosts**
Add following conetent to /etc/hosts on all machines
```sh
  10.67.19.100   Master
  10.67.19.101   hadoop-slave1
  10.67.19.102   hadoop-slave2
```

## Jdk and hadoop installation
** jdk installation**
> Need version of jdk shoud be not below 1.7
> Need install jdk-devel packages (not verification)

**hadoop installation**
> Download hadoop bin tarball to /opt folder
> Add environent variable to /etc/profile
```sh
export CLASSPATH=$JAVA_HOME/lib:$JAVA_HOME/jre/lib
export HADOOP_HOME=/opt/hadoop-2.9.1
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
```

**Create folder for hadoop file stroage**
```sh
mkdir  /root/hadoop
mkdir  /root/hadoop/tmp
mkdir  /root/hadoop/var
mkdir  /root/hadoop/dfs
mkdir  /root/hadoop/dfs/name
mkdir  /root/hadoop/dfs/data
```

**hadoop config setting**
> `Following all config file need to sync to all machines`
1. core-site.xml
```sh
<configuration>
 <property>
        <name>hadoop.tmp.dir</name>
        <value>/root/hadoop/tmp</value>
        <description>A base for other temporary directories.</description>
   </property>

   <property>
        <name>fs.default.name</name>
        <value>hdfs://Master:9000</value>
        <description>WebUI for hdfs access.</description>
   </property>
</configuration>
```

2. hadoop-env.sh
> modify variable JAVA_HOME if your java version is differnent with ${JAVA_HOME}
```sh
export JAVA_HOME=${JAVA_HOME}
```

3. hdfs-site.xml
```sh
<configuration>
<property>
   <name>dfs.name.dir</name>
   <value>/root/hadoop/dfs/name</value>
   <description>Path on the local filesystem where the NameNode stores the namespace and transactions logs persistently(fsimage file in here).</description>
</property>

<property>
   <name>dfs.data.dir</name>
   <value>/root/hadoop/dfs/data</value>
   <description>Comma separated list of paths on the local filesystem of a DataNode where it should store its blocks.</description>
</property>

<property>
   <name>dfs.replication</name>
   <value>2</value>
</property>

<property>
      <name>dfs.permissions</name>
      <value>false</value>
      <description>need not permissions</description>
</property>
</configuration>
```

4. mapred-site.xml
> MapReduce setting
```sh
<configuration>
<property>
   <name>mapred.job.tracker</name>
   <value>Master:49001</value>
</property>

<property>
      <name>mapred.local.dir</name>
       <value>/root/hadoop/var</value>
</property>


<property>
       <name>mapreduce.framework.name</name>
       <value>yarn</value>
</property>
</configuration>
```

5. yarn-site.xml
```sh
<configuration>

<!-- Site specific YARN configuration properties -->
   <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>Master</value>
   </property>

   <property>
        <description>The address of the applications manager interface in the RM.</description>
        <name>yarn.resourcemanager.address</name>
        <value>${yarn.resourcemanager.hostname}:8032</value>
   </property>

   <property>
        <description>The address of the scheduler interface.</description>
        <name>yarn.resourcemanager.scheduler.address</name>
        <value>${yarn.resourcemanager.hostname}:8030</value>
   </property>

   <property>
        <description>The http address of the RM web application.</description>
        <name>yarn.resourcemanager.webapp.address</name>
        <value>${yarn.resourcemanager.hostname}:8088</value>
   </property>

   <property>
        <description>The https adddress of the RM web application.</description>
        <name>yarn.resourcemanager.webapp.https.address</name>
        <value>${yarn.resourcemanager.hostname}:8090</value>
   </property>

   <property>
        <name>yarn.resourcemanager.resource-tracker.address</name>
        <value>${yarn.resourcemanager.hostname}:8031</value>
   </property>

   <property>
        <description>The address of the RM admin interface.</description>
        <name>yarn.resourcemanager.admin.address</name>
        <value>${yarn.resourcemanager.hostname}:8033</value>
   </property>

   <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
   </property>

   <property>
        <name>yarn.scheduler.maximum-allocation-mb</name>
        <value>1024</value>
        <discription>每个节点可用内存,单位MB,默认8182MB</discription>
   </property>

   <property>
        <name>yarn.nodemanager.vmem-pmem-ratio</name>
        <value>2.1</value>
   </property>

   <property>
        <name>yarn.nodemanager.resource.memory-mb</name>
        <value>1024</value>
   </property>

   <property>
        <name>yarn.nodemanager.vmem-check-enabled</name>
        <value>false</value>
   </property>
</configuration>

```

6. slaves
```sh
hadoop-slave2
hadoop-slave1
```

## Startup hadoop
**Format hdfs** 
```sh
hadoop  namenode  -format
```

**Start all serices**
```sh
start-all.sh
```

## Verify hadoop status
**hadoop overview**
> access url :  http://{master ip address}:50070/

**Yarn overview**
> access url :  http://${master ip address}:8088/

