---
layout: post
title:  "hbase rowkey design"
categories: hadoop
tags: bigdata structure hadoop mapreduce hbase
author: Root Wang
---

* content
{:toc}

## 简介
如果想要享受HBase飛快的查詢速度，與避免read/write的hotspot，好的RowKey Design是很重要的。

HBase的資料是儲存於Region Server並且以RowKey當作各Region分區的界線。由於RowKey是使用字典排序，當RowKey為連續字串時會導致資料傾斜，資料過度集中於某個region server。當這狀況發生時，如果有多個使用者同時對這個table發出請求(讀/寫)，這個region server會無法接受過多的請求數量而過於忙碌，這時候(讀/寫)的效能就會下降，嚴重的會導致該region server被認定已經crash，觸發HBase容錯機制而讓整個HBase叢集更為忙碌...

HBase是三维有序存储的，通过rowkey（行键），column key（column family和qualifier）和TimeStamp（时间戳）这个三个维度可以对HBase中的数据进>行快速定位。

HBase中rowkey可以唯一标识一行记录，在HBase查询的时候，有以下几种方式：

通过get方式，指定rowkey获取唯一一条记录
通过scan方式，设置startRow和stopRow参数进行范围匹配
全表扫描，即直接扫描整张表中所有行记录

HBase是三维有序存储的，通过rowkey（行键），column key（column family和qualifier）和TimeStamp（时间戳）这个三个维度可以对HBase中的数据进行快速定位。

## RowKey Scan
假設有個`RowKey`的結構長成這樣：
><userId>-<date>-<messageId>-<attachementId>
前面有介紹過HBase在使用RoeKey當作filter時，使用Scan查詢速度最快可以到毫秒等級。一般使用者會搭配已模糊查詢的方式來查資料，而HBase的RowKey在模糊查詢上就會有個限制，就是只支援後面字串的模糊查詢。以上面的RowKey結構為例，在查詢時就只能使用這四種方式：

>1.<userId>
>2.<userId>-<date>
>3.<userId>-<date>-<messageId>
>4.<userId>-<date>-<messageId>-<attachementId>
Key Design Type

## 四種RowKey設計方法：

* *Sequential/Time-serial key*
* *Salted key*
* *Field swap/promotion*
* *Random key*
* *Sequential/Time-serial ke*


### 如果使用Sequential/Time-serial key當作RowKey，資料會被寫入同一個region，此設計不適用於頻繁寫入的使用情境。

`Sequential key` : 假設使用員工編號當作`RowKey`
|員工編號|簡寫|
|A0001	|0001|
|A0002	|0002|
|A0003	|0003|
|A0004	|0004|

`Time-serial key` : 假設以訂單紀錄當作`RowKey`，格式為：`yyyy-mmdd-hhmmssss-productionId`

|訂單記錄	|代號|
|2010-0101-11562366-prdId1|	prdId1|
|2010-0101-23332187-prdId2|	prdId2|
|2010-0103-14224378-prdId1|	prdId1|
|···	···               |           |
|2010-0301-08262299-prdId5|	prdId5|
|2010-0302-17260101-prdId7|	prdId7|
|···	···               |           |
|2010-0801-11562377-prdId5|	prdId5|
|···	···               |           |

### Salted key
俗稱的灑鹽巴。使用演算法對`RowKey`加工，讓資料平均散佈到各個`Region Server`。

以員工編號為例

|員工編號|	簡寫|
|A0001|	0001|
|A0002|	0002|
|A0003|	0003|
|A0004|	0004|

*使用String rowkey = id.reverse()方法灑完鹽巴後就會成這樣：*

|員工編號|	簡寫|
|1000A|	0001|
|2000A|	0002|
|3000A|	0003|
|4000A|	0004|

### Field swap/promotion key
假設`RowKey`的格式是這樣<date>-<userId>，Swap方式就是把這兩個欄位位置交換：

<<date>-<userId> -> <userId>-<date>
而`Promotion`意指將某個`cf:qualifier`的值（列的值）提升至`RowKey`的位置，與原來的`RowKey`形成一個新的複合`RowKey`：

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/hbase_rowkey_image1.png)

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/hbase_rowkey_image2.png)

### Random key
`Random Key`，顧名思義就是隨機分布的`RowKey`，這種設計可以降低在寫入的情境發生`hotspot`的狀況。

例如可以使用MD5對timestamp加密後產生一組隨機的RowKey:

>byte[] rowkey = MD5(timestamp)

效能
由下面的圖可以了解這幾種RowKey適用的情境與效能：

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/hbase_rowkey_image3.png)


## HBase 查询方式
HBase中rowkey可以唯一标识一行记录，在HBase查询的时候，有以下几种方式：

* 通过get方式，指定rowkey获取唯一一条记录
* 通过scan方式，设置startRow和stopRow参数进行范围匹配
* 全表扫描，即直接扫描整张表中所有行记录

## rowkey长度原则
rowkey是一个二进制码流，可以是任意字符串，最大长度 64kb ，实际应用中一般为10-100bytes，以 byte[] 形式保存，一般设计成定长。

建议越短越好，不要超过16个字节，原因如下：

数据的持久化文件HFile中是按照KeyValue存储的，如果rowkey过长，比如超过100字节，1000w行数据，光rowkey就要占用100*1000w=10亿个字节，将近1G数据，这样会极大影响HFile的存储效率；
MemStore将缓存部分数据到内存，如果rowkey字段过长，内存的有效利用率就会降低，系统不能缓存更多的数据，这样会降低检索效率。
目前操作系统都是64位系统，内存8字节对齐，控制在16个字节，8字节的整数倍利用了操作系统的最佳特性。
rowkey散列原则
如果rowkey按照时间戳的方式递增，不要将时间放在二进制码的前面，建议将rowkey的高位作为散列字段，由程序随机生成，低位放时间字段，这样将提高数据均衡分布在每个RegionServer，以实现负载均衡的几率。如果没有散列字段，首字段直接是时间信息，所有的数据都会集中在一个RegionServer上，这样在数据检索的时候负载会集中在个别的RegionServer上，造成热点问题，会降低查询效率。

### rowkey唯一原则
必须在设计上保证其唯一性，rowkey是按照字典顺序排序存储的，因此，设计rowkey的时候，要充分利用这个排序的特点，将经常读取的数据存储到一块，将最近可能会被访问的数据放到一块。

## 什么是热点
HBase中的行是按照rowkey的字典顺序排序的，这种设计优化了scan操作，可以将相关的行以及会被一起读取的行存取在临近位置，便于scan。然而糟糕的rowkey设计是热点的源头。 热点发生在大量的client直接访问集群的一个或极少数个节点（访问可能是读，写或者其他操作）。大量访问会使热点region所在的单个机器超出自身承受能力，引起性能下降甚至region不可用，这也会影响同一个RegionServer上的其他region，由于主机无法服务其他region的请求。 设计良好的数据访问模式以使集群被充分，均衡的利用。

为了避免写热点，设计rowkey使得不同行在同一个region，但是在更多数据情况下，数据应该被写入集群的多个region，而不是一个。

下面是一些常见的避免热点的方法以及它们的优缺点：

### 加盐
这里所说的加盐不是密码学中的加盐，而是在rowkey的前面增加随机数，具体就是给rowkey分配一个随机前缀以使得它和之前的rowkey的开头不同。分配的前缀种类数量应该和你想使用数据分散到不同的region的数量一致。加盐之后的rowkey就会根据随机生成的前缀分散到各个region上，以避免热点。

### 哈希
哈希会使同一行永远用一个前缀加盐。哈希也可以使负载分散到整个集群，但是读却是可以预测的。使用确定的哈希可以让客户端重构完整的rowkey，可以使用get操作准确获取某一个行数据

### 反转
第三种防止热点的方法时反转固定长度或者数字格式的rowkey。这样可以使得rowkey中经常改变的部分（最没有意义的部分）放在前面。这样可以有效的随机rowkey，但是牺牲了rowkey的有序性。

反转rowkey的例子以手机号为rowkey，可以将手机号反转后的字符串作为rowkey，这样的就避免了以手机号那样比较固定开头导致热点问题

### 时间戳反转
一个常见的数据处理问题是快速获取数据的最近版本，使用反转的时间戳作为rowkey的一部分对这个问题十分有用，可以用 Long.Max_Value - timestamp 追加到key的末尾，例如 [key][reverse_timestamp] , [key] 的最新值可以通过scan [key]获得[key]的第一条记录，因为HBase中rowkey是有序的，第一条记录是最后录入的数据。

比如需要保存一个用户的操作记录，按照操作时间倒序排序，在设计rowkey的时候，可以这样设计

[userId反转][Long.Max_Value - timestamp]，在查询用户的所有操作记录数据的时候，直接指定反转后的userId，startRow是[userId反转][000000000000],stopRow是[userId反转][Long.Max_Value - timestamp]

如果需要查询某段时间的操作记录，startRow是[user反转][Long.Max_Value - 起始时间]，stopRow是[userId反转][Long.Max_Value - 结束时间]

## 其他一些建议

尽量减少行和列的大小在HBase中，value永远和它的key一起传输的。当具体的值在系统间传输时，它的rowkey，列名，时间戳也会一起传输。如果你的rowkey和列名很大，甚至可以和具体的值相比较，那么你将会遇到一些有趣的问题。HBase storefiles中的索引（有助于随机访问）最终占据了HBase分配的大量内存，因为具体的值和它的key很大。可以增加block大小使得storefiles索引再更大的时间间隔增加，或者修改表的模式以减小rowkey和列名的大小。压缩也有助于更大的索引。

列族尽可能越短越好，最好是一个字符

冗长的属性名虽然可读性好，但是更短的属性名存储在HBase中会更好

## 总结：
任何一種的RowKey設計沒有絕對好或是不好的分別，要看使用情境再決定要挑選哪種設定方式。
介紹完了RowKey設計後，接下來要來介紹HBase hello world api
