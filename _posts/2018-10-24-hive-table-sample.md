---
layout: post
title:  "Hive Installation And Using"
categories: hive
tags:  bigdata HA cluster hive mapreduce
author: Root Wang
---

* content
{:toc}

## The table in HIVE

Hive的表，与普通关系型数据库，如mysql在表上有很大的区别，所有hive的表都是一个文件，它是基于Hadoop的文件系统来做的。

hive总体来说可以总结为三种不同类型的表:

### 普通表:
```sql
CREATE [EXTERNAL] TABLE [IF NOT EXISTS] table_name   
  [(col_name data_type [COMMENT col_comment], ...)]   
  [COMMENT table_comment]   
  [PARTITIONED BY (col_name data_type   
    [COMMENT col_comment], ...)]   
  [CLUSTERED BY (col_name, col_name, ...)   
  [SORTED BY (col_name [ASC|DESC], ...)]   
  INTO num_buckets BUCKETS]   
  [ROW FORMAT row_format]   
  [STORED AS file_format]   
  [LOCATION hdfs_path]  

```

sample :
```sh
hive> create table hive_01 (name String, id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY ' ' LINES TERMINATED BY '\n';

#Data content:

hive>!cat /tmp/hello.txt
jee 15
sony 20
ruby 19
kaen 24

# Load data to table
hive> load data local inpath '/tmp/hello.txt' into table hive_01;

hive> select * from hive_01;
```

*table and data file in hdfs:*
```sh
drwxr-xr-x   - root supergroup          0 2018-10-30 15:50 /user/hive/warehouse/hive_1.db/hive_02   # Table name as folder
-rw-r--r--   2 root supergroup         31 2018-10-30 15:50 /user/hive/warehouse/hive_1.db/hive_02/hello.txt  # Data file`
```

>普通表在進行刪除資料表時會發生一個情形，就是連同在HDFS上的原始檔案會一並被刪除，如果想保存原始檔案，可以使用下面的語法進行新增table。

### 外部表
EXTERNAL 关键字可以让用户创建一个外部表，在建表的同时指定一个指向实际数据的路径（LOCATION），Hive 创建内部表时，会将数据移动到数据仓库指向的路径；若创建外部表，仅记录数据所在的路径，不对数据的位置做任何改变。在删除表的时候，内部表的元数据和数据会被一起删除，而外部表只删除元数据，不删除数据。具体sql如下：

```sql
create EXTERNAL table hive_01 (name String, id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY ' ' LINES TERMINATED BY '\n' LOCATION '/user/hive_01';
```
>NOTE: the path for LOCATION should not contain subfolder, or will cause some exception during select operation 

*table and data file in hdfs:*
```sh
drwxr-xr-x   - root supergroup          0 2018-10-30 16:09 /user/hive_01
-rw-r--r--   2 root supergroup         31 2018-10-30 16:09 /user/hive_01/hello.txt
```

### Partition table:

#### What is Partitions?
Hive Partitions is a way to organizes tables into partitions by dividing tables into different parts based on partition keys.

Partition is helpful when the table has one or more Partition keys. Partition keys are basic elements for determining how the data is stored in the table.

For Example: -

Client having Some E –commerce data which belongs to India operations in which each state (38 states) operations mentioned in as a whole. If we take state column as partition key and perform partitions on that India data as a whole, we can able to get Number of partitions (38 partitions) which is equal to number of states (38) present in India. Such that each state data can be viewed separately in partitions tables.

Sample Code Snippet for partitions

1.Creation of Table all states
```sql
# Create table
hive> create  table hive_01 (name String, id int, state String) ROW FORMAT DELIMITED FIELDS TERMINATED BY ' ' LINES TERMINATED BY '\n';

# Data content
hive>! cat /tmp/hello.txt
jee 15 p1
sony 20 p2
ruby 19 p3
kaen 24 p4

```
>NOTE: The space between cloumns shoule be one, or the load operation will input unexpected data to table

2.Loading data into created table all states
```sql
hive> load data local inpath '/tmp/hello.txt' into table hive_01;
```

3.Creation of partition table
```sql
# Create
hive> create table hive_03 (name String, id int) PARTITIONED BY(state string);

# Insert data from hive_01 to it
insert overwrite table hive_03  partition(state) select name,id,state from hive_03;

```
>NOTE: the column order for select clause should be match the order of column in hive_03


4.Actual processing and formation of partition tables based on state as partition key
5.There are going to be 38 partition outputs in HDFS storage with the file name as state name. We will check this in this step

```sh
drwxr-xr-x   - root supergroup          0 2018-10-30 17:24 /user/hive/warehouse/hive_03
drwxr-xr-x   - root supergroup          0 2018-10-30 17:24 /user/hive/warehouse/hive_03/state=p1
-rw-r--r--   2 root supergroup          7 2018-10-30 17:24 /user/hive/warehouse/hive_03/state=p1/000000_0
drwxr-xr-x   - root supergroup          0 2018-10-30 17:24 /user/hive/warehouse/hive_03/state=p2
-rw-r--r--   2 root supergroup          8 2018-10-30 17:24 /user/hive/warehouse/hive_03/state=p2/000000_0
drwxr-xr-x   - root supergroup          0 2018-10-30 17:24 /user/hive/warehouse/hive_03/state=p3
-rw-r--r--   2 root supergroup          8 2018-10-30 17:24 /user/hive/warehouse/hive_03/state=p3/000000_0
drwxr-xr-x   - root supergroup          0 2018-10-30 17:24 /user/hive/warehouse/hive_03/state=p4
-rw-r--r--   2 root supergroup          8 2018-10-30 17:24 /user/hive/warehouse/hive_03/state=p4/000000_0
```

#### What is Buckets?
Buckets in hive is used in segregating of hive table-data into multiple files or directories. it is used for efficient querying.

The data i.e. present in that partitions can be divided further into Buckets
The division is performed based on Hash of particular columns that we selected in the table.
Buckets use some form of Hashing algorithm at back end to read each record and place it into buckets
In Hive, we have to enable buckets by using the set.hive.enforce.bucketing=true;

1.Creating Bucket as shown below.

![](https://github.com/XGWang0/wiki/raw/master/_images/hive_bucket_1.png)

From the above screen shot

We are creating sample_bucket with column names such as first_name, job_id, department, salary and country
We are creating 4 buckets overhere.
Once the data get loaded it automatically, place the data into 4 buckets

2. Loading Data into table sample bucket

Assuming that"Employees table" already created in Hive system. In this step, we will see the loading of Data from employees table into table sample bucket.

Before we start moving employees data into buckets, make sure that it consist of column names such as first_name, job_id, department, salary and country.

Here we are loading data into sample bucket from employees table.

![](https://github.com/XGWang0/wiki/raw/master/_images/hive_bucket_2.png)

3.Displaying 4 buckets that created in Step 1

![](https://github.com/XGWang0/wiki/raw/master/_images/hive_bucket_3.png)

From the above screenshot, we can see that the data from the employees table is transferred into 4 buckets created in step 1.


### ISSUE Solution

1.How to get detail structure of table
```sql
desc FORMATTED hive_01;

show create table hive_01;
```

2.No support to delete or update table
```sql
hive> SET hive.support.concurrency = true;
hive> SET hive.enforce.bucketing = true;
hive> SET hive.exec.dynamic.partition.mode = nonstrict;
hive> SET hive.txn.manager =org.apache.hadoop.hive.ql.lockmgr.DbTxnManager;
hive> SET hive.compactor.initiator.on = true;
hive> SET hive.compactor.worker.threads = 1;
```
