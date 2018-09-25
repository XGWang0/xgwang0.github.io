---
layout: post
title:  "using python to control hbase"
categories: hadoop
tags:  bigdata structure hadoop  mapreduce hbase python 
author: Root Wang
---

* content
{:toc}
## introduce
The Apache Thrift software framework, for scalable cross-language services development, combines a software stack with a code generation engine to build services that work efficiently and seamlessly between C++, Java, Python, PHP, Ruby, Erlang, Perl, Haskell, C#, Cocoa, JavaScript, Node.js, Smalltalk, OCaml and Delphi and other languages.

## Install thrift

### Dependence

* boost
```sh
  wget http://sourceforge.net/projects/boost/files/boost/1.60.0/boost_1_60_0.tar.gz
  tar xvf boost_1_60_0.tar.gz
  cd boost_1_60_0
  /bootstrap.sh
  sudo ./b2 install
```
* libevent

### Download and setup

![thrift download](https://dist.apache.org/repos/dist/release/thrift/)

```sh
tar zxvf thrift-0.9.0.tar.gz 
cd  thrift-0.9.0
./configure --prefix=/usr/local/thrift-0.9.0
make
make install
```

### Verification
```sh
$# ./thrift -version
Thrift version 0.11.0
```

## Libirary installation for python

### Generate python library for hbase
```sh
./thrift --gen py /home/xgwang/Downloads/hbase-2.1.0/hbase-thrift/src/main/resources/org/apache/hadoop/hbase/
thrift/Hbase.thrift
```
>Q: 
>>Got warning : [WARNING:/home/xgwang/Downloads/hbase-2.1.0/hbase-thrift/src/main/resources/org/apache/hadoop/hbase/thrift/Hbase.thrift:89] The "byte" type is a compatibility alias for "i8". Use "i8" to emphasize the signedness of this type.
>A:
>>You can get the hbase.thrift form thrift src, but i did not find it there, just ignore this warnning


```sh
$tree gen-py/  
gen-py/
|-- __init__.py
`-- hbase
    |-- Hbase-remote
    |-- Hbase.py
    |-- __init__.py
    |-- constants.py
    `-- ttypes.py
```

### Copy library file to installation path of python
```sh
cp -r ${gen_path}/gen-py /usr/local/python-3.4/lib/python3.4.6/site-packages/
```

### Install thrift package for python
```sh
pip install thrift
```

## Start up hbase and thrift server

### Start hbase
```sh
$ ./start-hbase.sh
```

### Start thrift server
```sh
$ hbase thrift -p 9090 start

2018-09-07 16:57:22,968 INFO  [main] thrift.ThriftServer: ***** STARTING service 'ThriftServer' *****
2018-09-07 16:57:22,970 INFO  [main] util.VersionInfo: HBase 2.1.0
2018-09-07 16:57:22,970 INFO  [main] util.VersionInfo: Source code repository git://zhangduo-Gen8/home/zhangduo/hbase/code revision=e167
3bb0bbfea21d6e5dba73e013b09b8b49b89b
2018-09-07 16:57:22,970 INFO  [main] util.VersionInfo: Compiled by zhangduo on Tue Jul 10 17:26:48 CST 2018
2018-09-07 16:57:22,970 INFO  [main] util.VersionInfo: From source with checksum c8fb98abf2988c0490954e15806337d7
2018-09-07 16:57:23,211 INFO  [main] thrift.ThriftServerRunner: Using default thrift server type
2018-09-07 16:57:23,211 INFO  [main] thrift.ThriftServerRunner: Using thrift server type threadpool
2018-09-07 16:57:23,239 WARN  [main] util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-jav$ classes where applicable
2018-09-07 16:57:23,599 INFO  [main] metrics.MetricRegistries: Loaded MetricRegistries class org.apache.hadoop.hbase.metrics.impl.Metri$RegistriesImpl
2018-09-07 16:57:23,685 INFO  [main] util.log: Logging initialized @909ms
2018-09-07 16:57:23,758 INFO  [main] http.HttpRequestLog: Http request log for http.requests.thrift is not defined
2018-09-07 16:57:23,769 INFO  [main] http.HttpServer: Added global filter 'safety' (class=org.apache.hadoop.hbase.http.HttpServer$Quoti$gInputFilter)
2018-09-07 16:57:23,769 INFO  [main] http.HttpServer: Added global filter 'clickjackingprevention' (class=org.apache.hadoop.hbase.http.$lickjackingPreventionFilter)
gInputFilter)
2018-09-07 16:57:23,769 INFO  [main] http.HttpServer: Added global filter 'clickjackingprevention' (class=org.apache.hadoop.hbase.http.$
lickjackingPreventionFilter)
2018-09-07 16:57:23,772 INFO  [main] http.HttpServer: Added filter static_user_filter (class=org.apache.hadoop.hbase.http.lib.StaticUser
WebFilter$StaticUserFilter) to context thrift
2018-09-07 16:57:23,773 INFO  [main] http.HttpServer: Added filter static_user_filter (class=org.apache.hadoop.hbase.http.lib.StaticUser
WebFilter$StaticUserFilter) to context static
2018-09-07 16:57:23,773 INFO  [main] http.HttpServer: Added filter static_user_filter (class=org.apache.hadoop.hbase.http.lib.StaticUser
WebFilter$StaticUserFilter) to context logs
2018-09-07 16:57:23,802 INFO  [main] http.HttpServer: Jetty bound to port 9095
2018-09-07 16:57:23,803 INFO  [main] server.Server: jetty-9.3.19.v20170502
2018-09-07 16:57:23,841 INFO  [main] handler.ContextHandler: Started o.e.j.s.ServletContextHandler@66498326{/logs,file:///opt/hbase-2.1.
0/logs/,AVAILABLE}
2018-09-07 16:57:23,842 INFO  [main] handler.ContextHandler: Started o.e.j.s.ServletContextHandler@1e6454ec{/static,file:///opt/hbase-2.
1.0/hbase-webapps/static/,AVAILABLE}
2018-09-07 16:57:23,929 INFO  [main] handler.ContextHandler: Started o.e.j.w.WebAppContext@451001e5{/,file:///opt/hbase-2.1.0/hbase-weba
pps/thrift/,AVAILABLE}{file:/opt/hbase-2.1.0/hbase-webapps/thrift}
2018-09-07 16:57:23,935 INFO  [main] server.AbstractConnector: Started ServerConnector@303cf2ba{HTTP/1.1,[http/1.1]}{0.0.0.0:9095}
2018-09-07 16:57:23,935 INFO  [main] server.Server: Started @1161ms
2018-09-07 16:57:23,958 INFO  [main] thrift.ThriftServerRunner: starting TBoundedThreadPoolServer on /0.0.0.0:9090 with readTimeout 6000
0ms; min worker threads=16, max worker threads=1000, max queued requests=1000


```

## Python to operate hbase

### Create a table in hbase
```sh
hbase(main):001:0> list
TABLE                                                                                                                                   
firstTable                                                                                                                              
1 row(s)
Took 0.3766 seconds                                                                                                                     
=> ["firstTable"]

``

Python to connect hbase and get table name

```python
#! /usr/bin/python3
#coding=utf-8
import sys

#from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from hbase import Hbase
from hbase.ttypes import *

transport = TSocket.TSocket('127.0.0.1', 9090)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = Hbase.Client(protocol)
transport.open()
print(client.getTableNames())
```
output:
```sh
[b'firstTable']
``

-----------------------
## thrift api for python
连接与操作代码如下：
```python
from thrift.transport import TSocket,TTransport
from thrift.protocol import TBinaryProtocol
from hbase import Hbase

# thrift默认端口是9090
socket = TSocket.TSocket('192.168.0.156',9090)
socket.setTimeout(5000)

transport = TTransport.TBufferedTransport(socket)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = Hbase.Client(protocol)
socket.open()

print client.getTableNames()
print client.get('test','row1','cf:a')
```

### 常用方法说明
*createTable(tbaleName,columnFamilies)：创建表，无返回值 
**tableName：表名
**columnFamilies：列族信息，为一个ColumnDescriptor列表
```python
from hbase.ttypes import ColumnDescriptor

# 定义列族
column = ColumnDescriptor(name='cf')
# 创建表
client.createTable('test4',[column])
```

*enabledTable(tbaleName)：启用表，无返回值 
**tableName：表名
```python
# 启用表，若表之前未被禁用将会引发IOError错误
client.enabledTable('test')
```

*disableTable(tbaleName)：禁用表，无返回值 
**tableName：表名
```python
# 禁用表，若表之前未被启用将会引发IOError错误
client.disableTable('test')
```

*isTableEnabled(tbaleName)：验证表是否被启用，返回一个bool值 
**tableName：表名
```python
client.isTableEnabled('test')
```

*getTableNames(tbaleName)：获取表名列表，返回一个str列表 
**tableName：表名
```python
client.getTableNames()
```

*getColumnDescriptors(tbaleName)：获取所有列族信息，返回一个字典 
**tableName：表名

```python
client.getColumnDescriptors('test')
```

*getTableRegions(tbaleName)：获取所有与表关联的regions，返回一个TRegionInfo对象列表 
**tableName：表名

```python
client.getTableRegions('test')

```

*deleteTable(tbaleName)：删除表，无返回值 
**tableName：表名
# 表不存在将会引发IOError(message='java.io.IOException: table does not exist...)错误
# 表未被禁用将会引发IOError(message='org.apache.hadoop.hbase.TableNotDisabledException:...)错误

```python
client.deleteTable('test5')
```

*get(tableName,row,column)：获取数据列表，返回一个hbase.ttypes.TCell对象列表 
**tableName：表名
**row：行
**column：列

```python
result = client.get('test','row1','cf:a')       # 为一个列表，其中只有一个hbase.ttypes.TCell对象的数据
print result[0].timestamp
print result[0].value
```

*getVer(tableName,row,column,numVersions)：获取数据列表，返回一个hbase.ttypes.TCell对象列表 
**tableName：表名
**row：行
**column：列
**numVersions：要检索的版本数量

```python
result = client.get('test','row1','cf:a',2)       # 为一个列表，其中只有一个hbase.ttypes.TCell对象的数据
print result[0].timestamp
print result[0].value
```

*getVerTs(tableName,row,column,timestamp,numVersions)：获取小于当前时间戳的数据列表(似乎只获取前一个)，返回一个hbase.ttypes.TCell对象列表 
**tableName：表名
**row：行
**column：列
**timestamp：时间戳
**numVersions：要检索的版本数量

```python
result = client.get('test','row1','cf:a',2)       # 为一个列表，其中只有一个hbase.ttypes.TCell对象的数据
print result[0].timestamp
print result[0].value

```

*getRow(tableName,row)：获取表中指定行在最新时间戳上的数据。返回一个hbase.ttypes.TRowResult对象列表，如果行号不存在返回一个空列表 
**tableName：表名
**row：行

```python
# 行
row = 'row1'
# 列
column = 'cf:a'
# 查询结果
result = client.getRow('test',row)      # result为一个列表
for item in result:                     # item为hbase.ttypes.TRowResult对象
    print item.row
    print item.columns.get('cf:a').value        # 获取值。item.columns.get('cf:a')为一个hbase.ttypes.TCell对象
    print item.columns.get('cf:a').timestamp    # 获取时间戳。item.columns.get('cf:a')为一个hbase.ttypes.TCell对象
```

*getRowWithColumns(tableName,row,columns)：获取表中指定行与指定列在最新时间戳上的数据。返回一个hbase.ttypes.TRowResult对象列表，如果行号不存在返回一个空列表 
**tableName：表名
**row：行
**columns：列，list

```python
result = client.getRowWithColumns('test','row1',['cf:a','df:a'])
for item in result:
    print item.row
    print item.columns.get('cf:a').value
    print item.columns.get('cf:a').timestamp

    print item.columns.get('df:a').value
    print item.columns.get('df:a').timestamp
```

*getRowTs(tableName,row,timestamp)：获取表中指定行并且小于这个时间戳的所有数据。返回一个hbase.ttypes.TRowResult对象列表，如果行号不存在返回一个空列表 
**tableName：表名
**row：行
**timestamp：时间戳

```python
result = client.getRowTs('test','row1',1513069831512)
```

*getRowWithColumnsTs(tableName,row,columns,timestamp)：获取指定行与指定列，并且小于这个时间戳的所有数据。返回一个hbase.ttypes.TRowResult对象列表，如果行号不存在返回一个空列表 
**tableName：表名
**row：行
**columns：列，list
**timestamp：时间戳

```python
result = client.getRowWithColumnsTs('test','row1',['cf:a','cf:b','df:a'],1513069831512)
```

*mutateRow(tableName,row,mutations)：在表中指定行执行一系列的变化操作。如果抛出异常，则事务被中止。使用默认的当前时间戳，所有条目将具有相同的时间戳。无返回值 
**tableName：表名
**row：行
**mutations：变化,list

```python
from hbase.ttypes import Mutation

mutation = Mutation(name='cf:a',value='1')

# 插入数据。如果在test表中row行cf:a列存在，将覆盖
client.mutateRow('test','row1',[mutation])
```

*mutateRowTs(tableName,row,mutations,timestamp)：在表中指定行执行一系列的变化操作。如果抛出异常，则事务被中止。使用指定的时间戳，所有条目将具有相同的时间戳。如果是更新操作时，如果指定时间戳小于原来数据的时间戳，将被忽略。无返回值 
**tableName：表名
**row：行
**mutations：变化,list
**timestamp：时间戳

```python
from hbase.ttypes import Mutation
# value必须为字符串格式，否则将报错
mutation = Mutation(column='cf:a',value='2')
client.mutateRowTs('test','row1',[mutation],1513070735669)
```

*mutateRows(tableName,rowBatches)：在表中执行一系列批次(单个行上的一系列突变)。如果抛出异常，则事务被中止。使用默认的当前时间戳，所有条目将具有相同的时间戳。无返回值 
**tableName：表名
**rowBatches：一系列批次

```python
from hbase.ttypes import Mutation,BatchMutation
mutation = Mutation(column='cf:a',value='2')
batchMutation = BatchMutation('row1',[mutation])
client.mutateRows('test',[batchMutation])
```

*mutateRowsTs(tableName,rowBatches,timestamp)：在表中执行一系列批次(单个行上的一系列突变)。如果抛出异常，则事务被中止。使用指定的时间戳，所有条目将具有相同的时间戳。如果是更新操作时，如果指定时间戳小于原来数据的时间戳，将被忽略。无返回值 
**tableName：表名
**rowBatches：一系列批次，list
**timestamp：时间戳

```python
mutation = Mutation(column='cf:a',value='2')
batchMutation = BatchMutation('row1',[mutation])
client.mutateRowsTs('cx',[batchMutation],timestamp=1513135651874)
```

*atomicIncrement(tableName,row,column,value)：原子递增的列。返回当前列的值 
**tableName：表名
**row：行
**column：列
**value：原子递增的值


```python
result = client.atomicIncrement('cx','row1','cf:b',1)
print result    # 如果之前的值为2，此时值为3
```

*deleteAll(tableName,row,column)：删除指定表指定行与指定列的所有数据，无返回值 
**tableName：表名
**row：行
**column：列

```python
client.deleteAll('cx','row1','cf:a')
```

*deleteAllTs(tableName,row,column,timestamp)：删除指定表指定行与指定列中，小于等于指定时间戳的所有数据，无返回值 
**tableName：表名
**row：行
**column：列
**timestamp：时间戳

```python
client.deleteAllTs('cx','row1','cf:a',timestamp=1513569725685)
```

*deleteAllRow(tableName,row)：删除整行数据，无返回值 
**tableName：表名
**row：行
```python
client.deleteAllRow('cx','row1')
```

*deleteAllRowTs(tableName,row,timestamp)：删除指定表指定行中，小于等于此时间戳的所有数据，无返回值 
**tableName：表名
**row：行
**timestamp：时间戳

```python
client.deleteAllRowTs('cx','row1',timestamp=1513568619326)
```

*scannerOpen(tableName,startRow,columns)：在指定表中，从指定行开始扫描，到表中最后一行结束，扫描指定列的数据。返回一个ScannerID，int类型 
**tableName：表名
**startRow：起始行
**columns：列名列表,list类型

```python
scannerId = client.scannerOpen('cx','row2',["cf:b","cf:c"])
```

*scannerOpenTs(tableName,startRow,columns,timestamp)：在指定表中，从指定行开始扫描，获取所有小于指定时间戳的所有数据，扫描指定列的数据。返回一个ScannerID，int类型 
**tableName：表名
**startRow：起始行
**columns：列名列表,list类型
**timestamp：时间戳

```python
scannerId = client.scannerOpenTs('cx','row1',["cf:a","cf:b","cf:c"],timestamp=1513579065365)
```

*scannerOpenWithStop(tableName,startRow,stopRow,columns)：在指定表中，从指定行开始扫描，扫描到结束行结束(并不获取指定行的数据)，扫描指定列的数据。返回一个ScannerID，int类型 
**tableName：表名
**startRow：起始行
**stopRow：结束行
**columns：列名列表,list类型

```python
scannerId = client.scannerOpenWithStop('cx','row1','row2',["cf:b","cf:c"])
```

*scannerOpenWithStopTs(tableName,startRow,stopRow,columns,timestamp)：在指定表中，从指定行开始扫描，扫描到结束行结束(并不获取指定行的数据)，获取所有小于指定时间戳的所有数据，扫描指定列的数据。返回一个ScannerID，int类型 
**tableName：表名
**startRow：起始行
**stopRow：结束行
**columns：列名列表,list类型
**timestamp：时间戳


```python
scannerId = client.scannerOpenWithStopTs('cx','row1','row2',["cf:a","cf:b","cf:c"],timestamp=1513579065365)

scannerOpenWithPrefix(tableName,startAndPrefix,columns)：在指定表中，扫描具有指定前缀的行，扫描指定列的数据。返回一个ScannerID，int类型 
tableName：表名
startAndPrefix：行前缀
columns：列名列表,list类型
scannerId = client.scannerOpenWithPrefix('cx','row',["cf:b","cf:c"])
```

*scannerGet(id)：根据ScannerID来获取结果，返回一个hbase.ttypes.TRowResult对象列表 
**id：ScannerID

```python
scannerId = client.scannerOpen('cx','row1',["cf:b","cf:c"])
while True:
    result = client.scannerGet(scannerId)
    if not result:
        break
    print result

```
*scannerGetList(id,nbRows)：根据ScannerID来获取指定数量的结果，返回一个hbase.ttypes.TRowResult对象列表 
**id：ScannerID
**nbRows：指定行数
**scannerId = client.scannerOpen('cx','row1',["cf:b","cf:c"])
**result = client.scannerGetList(scannerId,2)


*scannerClose(id)：关闭扫描器，无返回值 
**id：ScannerID

```python
client.scannerClose(scannerId)
```
