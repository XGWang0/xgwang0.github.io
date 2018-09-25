---
layout: post
title:  "hadoop setting"
categories: hadoop
tags:  bigdata structure hadoop 
author: Root Wang
---

* content
{:toc}
## How to set `rack-aware`:
1. Modify core-site.xml with following content:
```xml
<property>
                <name>topology.script.file.name</name>
                <value>/usr/software/hadoop-2.7.3/sh/topology.sh</value>
</property>
```

2. topology.sh content:
```sh
#!/bin/bash
HADOOP_CONF=/usr/software/hadoop-2.7.3/etc/hadoop
while [ $# -gt 0 ] ; do
  # Actual node ip address will be passed to script
  nodeArg=$1
  exec<${HADOOP_CONF}/topology.data
  result=""
  while read line ; do
    ar=( $line )
    if [ "${ar[0]}" = "$nodeArg" ]||[ "${ar[1]}" = "$nodeArg" ]; then
      result="${ar[2]}"
    fi
  done
  shift
  if [ -z "$result" ] ; then
    echo -n "/default-rack"
  else
    echo -n "$result"
  fi
  done

```

topology.data content:
> 在Namenode上，该文件中的节点必须使用IP，使用主机名无效，而Jobtracker上，该文件中的节点必须使用主机名，使用IP无效,所以，最好ip和主机名都配上。Add a node data to topology.data, the node will be automatically added to cluster.
```doc
10.67.19.110 Master /master/rack1
10.67.19.111 hadoop-slave1 /dd/rack1
10.67.19.112 hadoop-slave2  /dd/rack2
```

3. Verify setting
> Restart hadoop
> Input command to verify topology
```sh
hdfs dfsadmin -printTopology
```
> Result:
```sh
Rack:/dd/rack1
	10.67.19.111:50010 (hadoop-slave1)
Rack:/dd/rack1
        10.67.19.112:50010 (hadoop-slave2)
```

### Add datanode and not restart nodedata
> Modify topology.data and add datanode data into it
> Restart datanode : sbin/hadoop-daemons.sh start datanode
> Verify datanode : bin/hadoop dfsadmin -printTopology

`note:If you do not add datanode data to topology.data and restart datanode, will cause datanode start error in datanode log`

