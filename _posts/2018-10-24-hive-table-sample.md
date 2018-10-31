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

### 普通表 Managed Table (Internal Table):
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








### Partitions
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

### Buckets
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


### Internal Table VS External Table:

#### Apache Hive Internal and External Tables

Hive is an open source data warehouse system used for querying and analyzing large datasets. Data in Apache Hive can be categorized into Table, Partition, and Bucket. The table in Hive is logically made up of the data being stored. Hive has two types of tables which are as follows:

*.Managed Table (Internal Table)
*.External Table

*Hive Managed Tables*

It is also know an internal table. When we create a table in Hive, it by default manages the data. This means that Hive moves the data into its warehouse directory.

*Hive External Tables*

We can also create an external table. It tells Hive to refer to the data that is at an existing location outside the warehouse directory.

#### Featured Difference between Hive Internal Tables vs External Tables

##### LOAD and DROP Semantics
We can see the main difference between the two table type in the LOAD and DROP semantics.

*.Managed Tables – When we load data into a Managed table, then Hive moves data into Hive warehouse directory.
For example:

```sql
CREATE TABLE managed_table (dummy STRING);
LOAD DATA INPATH '/user/tom/data.txt' INTO table managed_table;
```

This moves the file hdfs://user/tom/data.txt into Hive’s warehouse directory for the managed_table table, which is hdfs://user/hive/warehouse/managed_table.

Further, if we drop the table using:
```sql
DROP TABLE managed_table
```

Then this will delete the table metadata including its data. The data no longer exists anywhere. This is what it means for HIVE to manage the data.

External Tables – External table behaves differently. In this, we can control the creation and deletion of the data. The location of the external data is specified at the table creation time:

```sql
CREATE EXTERNAL TABLE external_table(dummy STRING)
LOCATION '/user/tom/external_table';
LOAD DATA INPATH '/user/tom/data.txt' INTO TABLE external_table;
```

Now, with the EXTERNAL keyword, Apache Hive knows that it is not managing the data. So it doesn’t move data to its warehouse directory. It does not even check whether the external location exists at the time it is defined. This very useful feature because it means we create the data lazily after creating the table.

The important thing to notice is that when we drop an external table, Hive will leave the data untouched and only delete the metadata.

##### Security

*.`Managed Tables` – Hive solely controls the Managed table security. Within Hive, security needs to be managed; probably at the schema level (depends on organization).
*.`External Tables` – These tables’ files are accessible to anyone who has access to HDFS file structure. So, it needs to manage security at the HDFS file/folder level.

##### When to use Managed and external table

*Use Managed table when*

*.We want Hive to completely manage the lifecycle of the data and table.
*.Data is temporary


*Use External table when*

*.Data is used outside of Hive. For example, the data files are read and processed by an existing program that does not lock the files.
*.We are not creating a table based on the existing table.
*.We need data to remain in the underlying location even after a DROP TABLE. This may apply if we are pointing multiple schemas at a single data set.
*.The hive shouldn’t own data and control settings, directories etc., we may have another program or process that will do these things.

### Conclusion

In conclusion, Managed tables are like normal database table in which we can store data and query on. On dropping Managed tables, the data stored in them is also deleted and data is lost forever. While dropping External tables will delete metadata but not the data.


### What is Hive Partitioning and Bucketing?

Apache Hive is an open source data warehouse system used for querying and analyzing large datasets. Data in Apache Hive can be categorized into Table, Partition, and Bucket. The table in Hive is logically made up of the data being stored. It is of two type such as internal table and external table. Refer this guide to learn what is Internal table and External Tables and the difference between both. Let us now discuss the Partitioning and Bucketing in Hive in detail-

*.Partitioning – Apache Hive organizes tables into partitions for grouping same type of data together based on a column or partition key. Each table in the hive can have one or more partition keys to identify a particular partition. Using partition we can make it faster to do queries on slices of the data.
*.Bucketing – In Hive Tables or partition are subdivided into buckets based on the hash function of a column in the table to give extra structure to the data that may be used for more efficient queries.

#### Comparison between Hive Partitioning vs Bucketing

We have taken a brief look at what is Hive Partitioning and what is Hive Bucketing. You can refer our previous blog on Hive Data Models for the detailed study of Bucketing and Partitioning in Apache Hive.

In this section, we will discuss the difference between Hive Partitioning and Bucketing on the basis of different features in detail-

##### Partitioning and Bucketing Commands in Hive

*.Partitioning

The Hive command for Partitioning is:
```sql
CREATE TABLE table_name (column1 data_type, column2 data_type) PARTITIONED BY (partition1 data_type, partition2 data_type,….);
```

*.Bucketing
The Hive command for Bucketing is:

```sql
CREATE TABLE table_name PARTITIONED BY (partition1 data_type, partition2 data_type,….) CLUSTERED BY (column_name1, column_name2, …) SORTED BY (column_name [ASC|DESC], …)] INTO num_buckets BUCKETS;
```

##### Apache Hive Partitioning and Bucketing Example

*.Hive Partitioning Example

For example, we have a table employee_details containing the employee information of some company like employee_id, name, department, year, etc. Now, if we want to perform partitioning on the basis of department column. Then the information of all the employees belonging to a particular department will be stored together in that very partition. Physically, a partition in Hive is nothing but just a sub-directory in the table directory.

For example, we have data for three departments in our employee_details table – Technical, Marketing and Sales. Thus we will have three partitions in total for each of the departments as we can see clearly in diagram below. For each department we will have all the data regarding that very department residing in a separate sub – directory under the table directory.






So for example, all the employee data regarding Technical departments will be stored in user/hive/warehouse/employee_details/dept.=Technical. So, the queries regarding Technical employee would only have to look through the data present in the Technical partition.

Therefore from above example, we can conclude that partitioning is very useful. It reduces the query latency by scanning only relevant partitioned data instead of the whole data set.

*.Hive Bucketing Example

Hence, from the above diagram, we can see that how each partition is bucketed into 2 buckets. Therefore each partition, says Technical, will have two files where each of them will be storing the Technical employee’s data

##### Advantages and Disadvantages of Hive Partitioning & Bucketing

Let us now discuss the pros and cons of Hive partitioning and Bucketing one by one-

*.`Pros and Cons of Hive Partitioning`

*Pros:*

1.It distributes execution load horizontally.
2.In partition faster execution of queries with the low volume of data takes place. For example, search population from Vatican City returns very fast instead of searching entire world population.

*Cons:*

1.There is the possibility of too many small partition creations- too many directories.
2.Partition is effective for low volume data. But there some queries like group by on high volume of data take a long time to execute. For example, grouping population of China will take a long time as compared to a grouping of the population in Vatican City.
3.There is no need for searching entire table column for a single record.

*.`Pros and Cons of Hive Bucketing`

*Pros:*

1.It provides faster query response like portioning.
2.In bucketing due to equal volumes of data in each partition, joins at Map side will be quicker.

*Cons:*

1.We can define a number of buckets during table creation. But loading of an equal volume of data has to be done manually by programmers.

#### column chosen for partititon VS bucket
*.Partitioning:

When choosing a partition column in a table, `partitioning column should not have high cardinality (no.of possible values in column).`

For example, a table contains employee_id, emp_timestamp and country. if we select emp_timestamp as partitioning column, then we will end up creating billions of folders in HDFS.

This will increase overhead on Name Node and decrease overall performance. In this case, we can choose country as partitioning column, because it will create maximum 196 partitions ( as total number of counties in world are 196).

*.Bucketing:

Bucketing decomposes data in each partition into `equal number of parts` as we specify in DDL.

In this example, we can declare employee_id as bucketing column, and no.of buckets as 4.

If we have 10000 records in USA partition, then each bucket file will have 2500 records inside USA partition.

Further if we apply _sorted by_ clause on employee_id , then joining of two tables with same bucketed and sorted column will be very quick.


>Bucketing works well when the field has high cardinality and data is evenly distributed among buckets.
>Partitioning works best when the cardinality of the partitioning field is not too high.

#### Conclusion
In conclusion to Hive Partitioning vs Bucketing, we can say that both partition and bucket distributes a subset of the table’s data to a subdirectory. Hence, Hive organizes tables into partitions. And it subdivides partition into buckets. 

