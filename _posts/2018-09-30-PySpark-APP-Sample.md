---
layout: post
title:  "PySpark APP Sample"
categories: Spark
tags:  bigdata structure mapreduce spark
author: Root Wang
---

* content
{:toc}


## RDD sample:

```python
import os
import sys
#配置环境变量并导入pyspark
os.environ['SPARK_HOME'] = r'/opt/spark-2.3.2-bin-hadoop2.7'
sys.path.append("/opt/spark-2.3.2-bin-hadoop2.7/python")
sys.path.append("/opt/spark-2.3.2-bin-hadoop2.7/python/py4j-0.10.7-src.zip")
from pyspark import SparkContext, SparkConf

appName ="spark_1" #应用程序名称
master= "spark://master:7077"#hadoop01为主节点hostname，请换成自己的主节点主机名称
conf = SparkConf().setAppName(appName).setMaster(master)

# Following config settings are not necessary
#conf.set("spark.executor.memory", "128M") 
conf.set("spark.shuffle.service.enabled", "false")

conf.set("spark.dynamicAllocation.enabled", "false")

conf.set("spark.io.compression.codec", "snappy")

conf.set("spark.rdd.compress", "true")
sc = SparkContext(conf=conf)

data = xrange(900000000)
distData = sc.parallelize(data,6)
res = distData.reduce(lambda a, b: a + b)
print("===========================================")
print (res)
print("===========================================")

```


## DataFrame Sample:

```python
# -*- coding:utf-8 -*-

from pyspark.sql import SparkSession
from pyspark.sql import Row

import os
import sys
#配置环境变量并导入pyspark
os.environ['SPARK_HOME'] = r'/opt/spark-2.3.2-bin-hadoop2.7'
sys.path.append("/opt/spark-2.3.2-bin-hadoop2.7/python")
sys.path.append("/opt/spark-2.3.2-bin-hadoop2.7/python/py4j-0.10.7-src.zip")
from pyspark import SparkContext, SparkConf

appName ="spark_1" #应用程序名称
master= "spark://master:7077"#hadoop01为主节点hostname，请换成自己的主节点主机名称
conf = SparkConf().setAppName(appName).setMaster(master)
#conf.set("spark.executor.memory", "128M") 
conf.set("spark.shuffle.service.enabled", "false")

conf.set("spark.dynamicAllocation.enabled", "false")

conf.set("spark.io.compression.codec", "snappy")

conf.set("spark.rdd.compress", "true")

# 常见 session 通过sparkconf
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 还是需要使用sparkcontent 去具体操作数据
sc = spark.sparkContext

# 创建RDD
rdd = sc.textFile("hdfs://myhdfs/test/hello.txt")

rddmap = rdd.map(lambda x: x.split())

userinfo = rddmap.map(lambda m: Row(name=m[0], age=int(m[1])))

# 创建dataframe 使用RDD
user_df = spark.createDataFrame(userinfo)

user_df.createOrReplaceTempView("USER")

# 使用sql instructor
res_sql = spark.sql("SELECT * FROM USER").collect()

res_filter = user_df.filter(user_df.age > 20)

# 保存到hadoop
res_filter.write.format("json").mode("overwrite").save("/tmp/spark.save")


# 转换dataframe成RDD
rdda = res_filter.rdd.map(lambda df: "name :%s, age :%d" %(df.name, df.age))
rdda.saveAsTextFile("/tmp/text")

#user_df.show()

print("="*100)
print(res_sql)
print(res_filter)
print(rdda.collect())
print("="*100)
```


## Run

```sh
spark-submit ${APP}
```

