---
layout: post
title:  "hbase installation and usage"
categories: hadoop
tags:  bigdata structure hadoop  mapreduce  hbase
author: Root Wang
---

* content
{:toc}
## 简介
HBase安裝模式與Hadoop相同，有Standalone、Pseudo-Distributed與Fully-Distributed，而這些名稱也是根據Hadoop的安裝模式所命名。比較特別的是Standalone與Pseudo-Distributed模式不一定要將資料儲存在HDFS上，但無法擁有Hadoop的容錯機制與分散式等優點，而Fully-Distributed 只能 運行在Hadoop上面。

## 事前準備
與Hadoop相同，HBase原始碼也是由Java撰寫，所以也是需要安裝JDK並且設定JAVA_HOME。
另外，HBase是架設在Hadoop上面的DataBase，如果想擁有Hadoop分散式儲存的功能，一個Hadoop叢集也是必要的。
所以需要作下列的準備：

### 安裝JDK，並設並JAVA_HOME
一個Hadoop叢集（optional）

下載HBase tar file後解壓縮，並設定HBASE_HOME。這邊使用2.0.0-appha4版本當作安裝教學範例。
備註：HBase2.0.x只支援Hadoop 2.6.1+與2.7.1+版本，其他版本目前尚未支援。

```sh
下載已經Build好的Hadoop檔案儲存至/opt，並且解壓縮至/opt/hbase目錄
cd /opt
sudo wget http://apache.stu.edu.tw/hbase/2.0.0-alpha4/hbase-2.0.0-alpha4-bin.tar.gz
#解壓縮
sudo tar -zxvf hbase-2.0.0-alpha4-bin.tar.gz
#移動至/opt/hbase
sudo mv /opt/hbase-2.0.0-alpha4-bin /opt/hbase
設定HBASE_HOME環境變數：
#編輯~/.bashrc
sudo vi ~/.bashrc
#加入下列參數
export HBASE_HOME=/opt/hbase
export PATH=$PATH:$HBASE_HOME/bin
Standalone
與Hadoop相同，Standalone是HBase預設的模式，啟動時會在一個JVM內運行所有HBase全部的daemon，包含Master、RegionServer與ZooKeeper。
```


### 使用local file system安裝模式：

修改_hbase-site.xml_即可。
```doc
<configuration>
  <property>
    <name>hbase.rootdir</name>
    <value>file:///opt/data/hbase</value>
  </property>
  <property>
    <name>hbase.zookeeper.property.dataDir</name>
    <value>/opt/data/zookeeper</value>
    <description>如果沒有設定，預設路徑為/tmp</description>
  </property>
</configuration>
hbase-site.xml 所設定的路徑如果不存在，HBase啟動時會自動建立。
```

啟動HBase：
```sh
cd ${HBASE_HOME}/bin
sudo bash start-hbase.sh
```

如果啟動成功，可以使用jps指令來觀察HBase的daemon，其中會包含：
HMaster
與HDFS的namenode功能類似，紀錄資料位於哪個RegionServer，重要性也與namenode一樣。
HRegionServer
相當於HDFS的datanode，負責儲存資料。
HQuorumPeer
HBase內建的zookeeper。如果安裝HBase時沒有另外指定外部的zookeeper，啟動HBase時會自行啟動。

###使用HDFS安裝模式：

修改_hbase-site.xml_即可，啟動方式與local file system模式相同，只要將hbase.rootdir改為HDFS上的路徑，並將hbase.cluster.distributed設定為false
```doc
<property>
    <name>hbase.rootdir</name>
    <value>hdfs://{hostname}:9000/hbase</value>
</property>
<property>
    <name>hbase.cluster.distributed</name>
    <value>false</value>
</property>
```
*備註：{hostname}為主機名稱，請依照自己的Hadoop Namenode所在的hostname修改.*


### Pseudo-Distributed
與Standalone運作方式類似，差別在於Pseudo-Distributed的daemon是在不同的JVM運作。儲存模式也與Standalone一樣，可以使用local file system或是HDFS，設定方法也與Standalone模式相同，只要修改hbase-site.xml。

設定為Pseudo-Distributed模式：

修改_hbase-site.xml_，加入下列參數設定。
```doc
<property>
  <name>hbase.cluster.distributed</name>
  <value>true</value>
</property>
```doc
*如果已經啟動Standalone模式的HBase，務必請先關閉再重新啟動，可使用下列指令關閉：*
```sh
cd ${HBASE_HOME}/bin
#關閉HBase
sudo bash stop-hbase.sh
或者是使用rolling restart重新啟動HBase，不必完全關閉HBase。

cd ${HBASE_HOME}/bin
#rolling restart HBase
sudo bash rolling-restart.sh
```


###Fully-Distributed
由於Fully-Distributed只支援運作在HDFS，所以必須先準備好Hadoop，Hadoop運作模式一樣可以使用那三種模式。如果是要在production環境運作，無論是Hadoop或是HBase皆強烈建議使用Fully-Distributed。

設定hbase-site.xml：由於Fully-Distributed只支援運作在HDFS上，所以hbase.rootdir必需設定為HDFS路徑，且hbase.cluster.distributed需設定為true。HBase運作時需要zookeeper的協助，在production環境強烈建議需要一組不同於Hadoop與HBase的機器來運作zookeeper。實驗性質則可以使用HBase內建的zookeeper，不需要額外安裝。

hbase-site.xml setting
```doc
  <property>
    <name>hbase.rootdir</name>
    <value>hdfs://10.67.19.84:9000/hbase</value>
  </property>

  <property>
    <name>hbase.cluster.distributed</name>
    <value>true</value>
    <description>The mode the clusterwill be in. Possible values are
      false: standalone and pseudo-distributedsetups with managed Zookeeper
      true: fully-distributed with unmanagedZookeeper Quorum (see hbase-env.sh)
    </description>
  </property>

  <property>
    <name>hbase.zookeeper.quorum</name>
    <value>Master,openqa,hadoop-slave2</value>
    <description>Comma separated listof servers in the ZooKeeper Quorum.
    For example,"host1.mydomain.com,host2.mydomain.com,host3.mydomain.com".
    By default this is set to localhost forlocal and pseudo-distributed modes
    of operation. For a fully-distributedsetup, this should be set to a full
    list of ZooKeeper quorum servers. IfHBASE_MANAGES_ZK is set in hbase-env.sh
    this is the list of servers which we willstart/stop ZooKeeper on.
    </description>
  </property>

  <property>
    <name>hbase.zookeeper.property.dataDir</name>
    <value>/opt/data/hazookeeper</value>
  </property>
```

設定regionservers：與Pseudo-Distributed最大不同點在於，Fully-Distributed會有多台機器運作，故需要設定此檔案讓HMaster知道HBase的成員有哪些。
```sh
編輯regionservers
sudo vi ${HBASE_HOME}/conf/regionservers
#加入機器的hostname，如果有三台機器，請依序加入如下所示
server-a1
server-a2
server-a3
設定完成就可以啟動HBase了！
```

最後
安裝完成後，可以透過 http://{HBASE_MASTER_HOST_NAME_OR_IP}:16010 web ui 來查看HBase叢集的狀況。{HBASE_MASTER_HOST_NAME_OR_IP}為HBase Master所在的機器。

無論是`Standalone`、`Pseudo-Distributed`或是`Fully-Distributed`，需挑選適用的安裝模式才能發揮HBase最好的效益，也能減少使用上的困擾。

如果想要快速體驗Fully-Distributed模式的HBase cluster，可以使用作者所撰寫的hbase on docekr，內有使用說明與教學，也歡迎fork並開PR。





-----------------------------------------------------------
## HBase shell commands:

### hbase shell
是的！你沒看過，HBase Shell的進入指令就是hbase shell。接下來會透過一個使用情境來介紹基本的HBase shell指令。

HBase Shell 使用情境
一開始使用一個新的DataBase時，會需要先新增Table。成功建立好Table後，會需要新增資料。爾後會有編輯舊資料的需求。最後，查詢資料。

### 建立資料表

** Usage **
create 'table_name', 'column_family_name'
#說明
  table_name:    欲建立的table名稱。
  column_family: Column Family名稱。Column Family是用來將欄位分群，被分群的欄位名稱會以Column Family
                 為前綴詞(prefix)，冒號(:)為分隔符號，再加上qualifier(column name)的組合呈現。
                 例如：在某個table內會有欄位`tag:name`與`tag:id`，其中`tag`代表column family，
                 `name`與`id`為qualifier。
接下來我們就來建立一個firstTable的資料表，column family名稱為first_cf：
```sh
create 'firstTable', 'first_cf'
```

** 查詢資料表清單 **
資料表建立成功後，可用下列指令來查看資料表清單：

```sh
hbase>list
TABLE
firstTable
1 row(s)
Took 0.5339 seconds
```

** 新增資料 **
接下來要新增資料：

put 'table_name', 'row_key', 'column_name', 'value'
#說明
  table_name:     table名稱。
  row_key:        row_key，即HBase的Index，也是唯一的主鍵(pk)。
  column_name:    欄位名稱，請以column_family:qualifier格式輸入。
  value:          欄位值。
接下來可以使用下面語法來新增筆資料：

```sh
put 'firstTable', 'rk_1', 'first_cf:value', '65535'
put 'firstTable', 'rk_2', 'first_cf:value', '111'
put 'firstTable', 'rk_3', 'first_cf:value', '9487'
put 'firstTable', 'rk_3', 'first_cf:id', 'John'
```

** 查詢資料 **
新增一筆資料後，接著就要查詢剛剛新增的資料是否正確：


scan 'table_name'
#說明
  table_name:     table名稱。
接下來可以使用下面語法來查詢table資料：

```sh
scan 'firstTable'

結果
ROW                   COLUMN+CELL
 rk_1                 column=first_cf:value, timestamp=1513237353219, value=65535
 rk_2                 column=first_cf:value, timestamp=1513238888458, value=111
 rk_3                 column=first_cf:id, timestamp=1513238938372, value=John
 rk_3                 column=first_cf:value, timestamp=1513238904507, value=9487
3 row(s)
Took 0.0189 seconds
由於前面有提到HBase是以key-value方式儲存資料，所以在這裡可以看到呈現方式也是以key-value方式呈現。
想像成table方式會變成這樣：

rowkey \column	id	value
rk_1		65535
rk_2		111
rk_3	John	9487
這就是前面所提到的稀疏矩陣（Sparse matrix），每個row有資料的欄位數並不一定會相等。使用scan會將該table內所有資料全部以key-value方式顯示在銀幕，使用時務必搭配LIMIT參數控制顯示的資料數量。
```

** 只回傳一筆資料 **
```sh
scan 'firstTable', {LIMIT => 1}
更新資料
HBase沒有update的指令，要更新資料只能再對同一個欄位進行一次put：

put 'firstTable', 'rk_1', 'first_cf:value', '123456'
使用filter取出剛剛put的資料:

scan 'firstTable', {ROWPREFIXFILTER => 'rk_1', COLUMNS => ['first_cf:value']}

#結果
ROW                   COLUMN+CELL
 rk_1                 column=first_cf:value, timestamp=1513241216522, value=123456
1 row(s)
Took 0.0365 seconds
```

* [Hbase shell commands](https://learnhbase.wordpress.com/2013/03/02/hbase-shell-commands/)

* [Hbase doc](http://hbase.apache.org/book.html)
