---
layout: post
title:  "Hive Installation And Using"
categories: hive
tags:  bigdata HA cluster hive mapreduce
author: Root Wang
---

* content
{:toc}

## What is the HIVE?

这里简单说明一下，好对大家配置hive有点帮助。`hive是建立在hadoop上的`，当然，你如果只搭建hive也没用什么错。说简单一点，hadoop中的mapreduce调用如果面向DBA的时候，那么问题也就显现了，因为不是每个DBA都能明白mapreduce的工作原理，如果为了管理数据而需要学习一门新的技术，从现实生活中来说，公司又需要花钱请更有技术的人来了。

　　开个玩笑，hadoop是为了存储数据和计算而推广的技术，而和数据挂钩的也就属于数据库的领域了，所以hadoop和DBA挂钩也就是情理之中的事情，在这个基础之上，我们就需要为了DBA创作适合的技术。

　　hive正是实现了这个，hive是要类SQL语句（HiveQL）来实现对hadoop下的数据管理。hive属于数据仓库的范畴，那么，数据库和数据仓库到底有什么区别了，这里简单说明一下：

*.数据库侧重于OLTP（在线事务处理），
*.数据仓库侧重OLAP（在线分析处理）；

也就是说，例如mysql类的数据库更侧重于短时间内的数据处理，反之。


无hive：使用者.....->mapreduce...->hadoop数据（可能需要了解mapreduce）
有hive：使用者...(->HQL（SQL）->hive...->mapreduce)...->hadoop数据（只需要会SQL语句）


## hive安装和配置

### 安装

1.下载hive——地址：http://mirror.bit.edu.cn/apache/hive/
2.hive解压 :

```sh
[root@s100 local]# tar -zxvf apache-hive-2.1.1-bin.tar.gz -C /usr/local/
```


### 配置

1.Environment init:
```sh
[root@s100 local]# vim /etc/profile
 

1 #hive
2 export HIVE_HOME=/usr/local/hive
3 export PATH=$PATH:$HIVE_HOME/bin
```


2.创建hive-site.xml
```sh
[root@s100 conf]# cd ${HIVE_HOME}/conf/
[root@s100 conf]#  mv ${HIVE_HOME}/conf/hive-default.xml.template ${HIVE_HOME}/conf/hive-site.xml
```

3.修改hive-site.xml

```doc
        <!-- 插入一下代码 -->
    <property>
        <name>javax.jdo.option.ConnectionUserName</name>用户名（这4是新添加的，记住删除配置文件原有的哦！）
        <value>root</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionPassword</name>密码
        <value>123456</value>
    </property>
   <property>
        <name>javax.jdo.option.ConnectionURL</name>mysql
        <value>jdbc:mysql://master:3306/hive</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>mysql驱动程序
        <value>com.mysql.jdbc.Driver</value>
    </property>
        <!-- 到此结束代码 -->
```
> Add above content at before hive.exec.script.wrapper section, or may cause default setting will override your setting


Found following issue , need extra setting:
>Failed with exception java.io.IOException:java.lang.IllegalArgumentException: 
>java.net.URISyntaxException: Relative path in absolute URI: '${system:user.name%7D}'


Add following section
```doc
<property>
<name>system:java.io.tmpdir</name>
<value>/${HIVE_HOME}tmp</value>
<description/>
</property>
```

Change following attribution:
```
<property>
    <name>hive.exec.local.scratchdir</name>
    <value>${HIVE_HOME}/tmp/${user.name}</value>
    <description>Local scratch space for Hive jobs</description>
  </property>
```


4.复制mysql的驱动程序到${HIVE_HOME}/lib下面

```sh
[root@s100 lib]# ll mysql-connector-java-5.1.18-bin.jar 
-rw-r--r-- 1 root root 789885 1月   4 01:43 mysql-connector-java-5.1.18-bin.jar
```

5.创建用户，用户权限，DB for HIVE

```sh
Insert user:

MariaDB [hive]> insert into mysql.user(Host,User,Password) values("localhost","hive",password("123456"));

Grant permission to user on localhost & remote:

MariaDB [hive]> grant all privileges on *.* to hive@localhost identified by '123456';
MariaDB [hive]> grant all privileges on *.* to hive@'%' identified by '123456';


Create database for hive:

MariaDB [hive]> create database hive;
```

6.初始化mysql中hive的schema

```sh
1 [root@s100 bin]# pwd
2 /usr/local/hive/bin
3 [root@s100 bin]# schematool -dbType mysql -initSchema
```

7.执行hive

8.查询mysql

```sh
mysql> use hive
15 Reading table information for completion of table and column names
16 You can turn off this feature to get a quicker startup with -A
17 
18 Database changed
19 mysql> show tables;
20 +---------------------------+
21 | Tables_in_hive            |
22 +---------------------------+
23 | AUX_TABLE                 |
24 | BUCKETING_COLS            |
25 | CDS                       |
26 | COLUMNS_V2                |
27 | COMPACTION_QUEUE          |
28 | COMPLETED_COMPACTIONS     |
```


## hive 使用与测试

1.Hadoop中的HDFS存了什么？

```sh
hadoop fs -fs hdfs://myhdfs -lsr /tmp/hive
lsr: DEPRECATED: Please use 'ls -R' instead.
drwx------   - root supergroup          0 2018-10-30 14:24 /tmp/hive/root
drwx------   - root supergroup          0 2018-10-30 14:24 /tmp/hive/root/0c359b5e-595f-4e04-b7dd-e569d0a77c88
drwx------   - root supergroup          0 2018-10-30 14:24 /tmp/hive/root/0c359b5e-595f-4e04-b7dd-e569d0a77c88/_tmp_space.db
drwx------   - root supergroup          0 2018-10-30 14:24 /tmp/hive/root/ef4dae45-e750-44dc-be9b-e81298a4ac3d
drwx------   - root supergroup          0 2018-10-30 14:24 /tmp/hive/root/ef4dae45-e750-44dc-be9b-e81298a4ac3d/_tmp_space.db
```

2.进入HIVE， 创建库与表：

```sh
[root@localhost conf]# hive

#创建DB

1 hive> create database hive_1;
2 OK
3 Time taken: 1.432 seconds

# 显示DB
1 hive> show databases;
2 OK
3 default
4 hive_1
5 Time taken: 1.25 seconds, Fetched: 2 row(s)

```


3.查看hdfs 和mysql：

```sh
Master:/opt/apache-hive-3.1.0-bin # hadoop fs -fs hdfs://myhdfs -lsr /user
lsr: DEPRECATED: Please use 'ls -R' instead.
drwxr-xr-x   - root supergroup          0 2018-10-30 14:21 /user/hive
drwxr-xr-x   - root supergroup          0 2018-10-30 14:21 /user/hive/warehouse
drwxr-xr-x   - root supergroup          0 2018-10-30 14:21 /user/hive/warehouse/hive_1.db
drwxr-xr-x   - root supergroup          0 2018-09-27 17:00 /user/root
drwxr-xr-x   - root supergroup          0 2018-10-24 16:31 /user/root/.sparkStaging
```

```sh
MariaDB [hive]> select * from DBS;
+-------+-----------------------+---------------------------------------------+---------+------------+------------+-----------+
| DB_ID | DESC                  | DB_LOCATION_URI                             | NAME    | OWNER_NAME | OWNER_TYPE | CTLG_NAME |
+-------+-----------------------+---------------------------------------------+---------+------------+------------+-----------+
|     1 | Default Hive database | hdfs://myhdfs/user/hive/warehouse           | default | public     | ROLE       | hive      |
|     2 | NULL                  | hdfs://myhdfs/user/hive/warehouse/hive_1.db | hive_1  | root       | USER       | hive      |
+-------+-----------------------+---------------------------------------------+---------+------------+------------+-----------+
```

4.创建表在HIVE

```sh
hive> use hive_1;
OK
Time taken: 0.754 seconds
hive> create table hive_01 (id int,name string);
OK
Time taken: 2.447 seconds
hive> show tables;
OK
hive_01 （表创建成功）
Time taken: 0.31 seconds, Fetched: 2 row(s)
hive> 
```

5.HDFS和mysql出现了那些变化：

```sh
Master:/opt/apache-hive-3.1.0-bin # hadoop fs -fs hdfs://myhdfs -lsr /user
lsr: DEPRECATED: Please use 'ls -R' instead.
drwxr-xr-x   - root supergroup          0 2018-10-30 14:21 /user/hive
drwxr-xr-x   - root supergroup          0 2018-10-30 14:21 /user/hive/warehouse
drwxr-xr-x   - root supergroup          0 2018-10-30 14:27 /user/hive/warehouse/hive_1.db
drwxr-xr-x   - root supergroup          0 2018-10-30 14:27 /user/hive/warehouse/hive_1.db/hive_01
drwxr-xr-x   - root supergroup          0 2018-09-27 17:00 /user/root
drwxr-xr-x   - root supergroup          0 2018-10-24 16:31 /user/root/.sparkStaging
```

```sh
MariaDB [hive]> select * from TBLS\G;
*************************** 1. row ***************************
            TBL_ID: 1
       CREATE_TIME: 1540880824
             DB_ID: 2
  LAST_ACCESS_TIME: 0
             OWNER: root
        OWNER_TYPE: USER
         RETENTION: 0
             SD_ID: 1
          TBL_NAME: hive_01
          TBL_TYPE: MANAGED_TABLE
VIEW_EXPANDED_TEXT: NULL
VIEW_ORIGINAL_TEXT: NULL
IS_REWRITE_ENABLED:  
1 row in set (0.00 sec)
```

---------------------------------------------------------------
版权声明：

本文作者：Root

欢迎对小博主的博文内容批评指点，如果问题，可评论或邮件联系（john.wangxg@gmail.com）

欢迎转载，转载请在文章页面明显位置给出原文链接，谢谢
