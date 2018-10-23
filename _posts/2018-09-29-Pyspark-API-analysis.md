---
layout: post
title:  "Pyspark API Analysis"
categories: Spark
tags:  bigdata structure mapreduce spark
author: Root Wang
---

* content
{:toc}

### RDD

* Introduction: *

*. `RDD`是一个抽象的分布式数据集合，它提供了一系列转化操作（例如基本的map()、flatMap()、filter()，类集合操作union()、intersection()、subtract()）和行动操作（例如collect()、count()、take()、top()、reduce()、foreach()）。可以说，RDD是非常灵活的数据集合，其中可以存放类型相同或者互异的数据，同时可以指定任何自己期望的函数对其中的数据进行处理。 
创建一个RDD：

```python
# 从list中创建
rdd = sc.parallelize([1, '2', (3, 4), ['5', '6']])
# 从文件中读取
rdd = sc.textFile('\path\to\file')
```

*. 还有一类RDD是key-value `Pair RDD`，即规定RDD每个元素都是一个二元组，其中第一个值是key，第二个值为value，key一般选取RDD中每个元素的一个字段。 
创建一个Pair RDD：

```python
# 创建一个普通RDD
rdd = sc.parallelize([('a', 1, 2), ('b', 3, 4), ('c', 5, 6)])
# 提取每个元素的第一个元素作为key剩余元素作为value创建Pair RDD
pair_rdd = rdd.map(lambda x: (x[0], x[1:]))
```

可以看到Pair RDD实质上仍然是一个普通的RDD，那为什么它要单独拿出来讲呢？ 
这是因为，Pair RDD由于有key的存在，与普通的RDD相比更加格式化，这种特性就会给Pair RDD赋予一些特殊的操作，例如groupByKey()可以将具有相同key进行分组，其结果仍然得到Pair RDD，然后利用mapValues()对相同key的value进行函数计算；reduceByKey()、countByKey()和sortByKey()等一系列“ByKey()”操作同理。 
另外，两个Pair RDD具有像SQL一样的连接操作，例如两个Pair RDD进行join()后，具有相同key的元素的value会被放在一个元组里，key不相同的元素会被舍弃。leftOuterJoin()、rightOuterJoin()、fullOuterJoin()等操作同理。


### Spark SQL中的DataFrame

Pair RDD已经被一定程度的格式化了，它的每个元素会具有key，但是value仍然具有很大的灵活性。`DataFrame`是一种完全格式化的数据集合，和数据库中的表的概念比较接近，它每列数据必须具有相同的数据类型。也正是由于DataFrame知道数据集合所有的类型信息，DataFrame可以进*行列处理优化*而获得比RDD*更优的性能*。 

在内部实现上，DataFrame是由Row对象为元素组成的集合，每个Row对象存储DataFrame的一行，Row对象中记录每个域=>值的映射，因而Row可以被看做是一个结构体类型。可以通过创建多个tuple/list、dict、Row然后构建DataFrame。 
注：用dict构建DataFrame已经废弃了，推荐用Row。

```python
# 创建list的list
lists = [['a', 1], ['b', 2]]
# 构建具有默认生成的列_1、_2的DataFrame
dataframe = spark.createDataFrame(lists)

# 创建dict的list
dicts = [{'col1':'a', 'col2':1}, {'col1':'b', 'col2':2}]
# 构建具有列col1、col2的DataFrame
dataframe = spark.createDataFrame(dicts)

# 创建Row的list
rows = [Row(col1='a', col2=1), Row(col1='b', col2=2)]
# 构建具有列col1、col2的DataFrame
dataframe = spark.createDataFrame(rows)
```

虽然DataFrame被完全格式化了，但是其中每列可以存储的类型仍然是非常丰富的，包括基本的数据类型、list、tuple、dict和Row，这也就意味着所有的复杂数据类型都可以相互嵌套，从而解除了完全格式化的限制。例如，你可以在一列中存储list类型，而每行list按需存储不定长的数据。 

那么，RDD和DataFrame还有哪些使用上的区别呢？

> RDD：没有列名称，只能使用数字来索引；具有map()、reduce()等方法并可指定任意函数进行计算;
> DataFrame：一定有列名称（即使是默认生成的），可以通过.col_name或者['col_name']来索引列；具有表的相关操作（例如select()、filter()、where()、join），但是没有map()、reduce()等方法。

### RDD 转换为 DataFrame

什么样的RDD可以转换为DataFrame？ 
RDD灵活性很大，并不是所有RDD都能转换为DataFrame，而那些每个元素具有一定相似格式的时候才可以。

为什么RDD需要转换为DataFrame？ 
当RDD进行类似表的相应操作时，都需要指定相应的函数，转换为DataFrame书写更简单，并且执行效率高。

怎么样将RDD转换为DataFrame？ 
就像之前的例子一样，可以利用

```PYTHON
dataframe = spark.createDataFrame(rdd, schema=None, samplingRatio=None)
```

来将RDD转换为DataFrame，其中的参数设置需要注意： 
schema：DataFrame各列类型信息，在提前知道RDD所有类型信息时设定。例如

```python
schema = StructType([StructField('col1', StringType()),
         StructField('col2', IntegerType())])
```

samplingRatio：推测各列类型信息的采样比例，在未知RDD所有类型信息时，spark需要根据一定的数据量进行类型推测；默认情况下，spark会抽取前100的RDD进行推测，之后在真正将RDD转换为DataFrame时如果遇到类型信息不符会报错 Some of types cannot be determined by the first 100 rows, please try again with sampling 。同理采样比例较低，推测类型信息也可能错误。

### DataFrame转换为RDD
有时候DataFrame的表相关操作不能处理一些问题，例如需要对一些数据利用指定的函数进行计算时，就需要将DataFrame转换为RDD。DataFrame可以直接利用.rdd获取对应的RDD对象，此RDD对象的每个元素使用Row对象来表示，每列值会成为Row对象的一个域=>值映射。例如

```python
dataframe = spark.createDataFrame([Row(col1='a', col2=1), Row(col1='b', col2=2)])
>>> 
+----+----+
|col1|col2|
+----+----+
|   a|   1|
|   b|   2|
+----+----+

rdd = dataframe.rdd
>>> [Row(col1=u'a', col2=1), Row(col1=u'b', col2=2)]
```

DataFrame转化后的RDD如果需要和一般形式的RDD进行操作（例如join），还需要做索引将数值从Row中取出，比如转化为Pair RDD可以这样操作
```python
rdd = rdd.map(lambda x: [x[0], x[1:]])
>>> [[u'a', (1,)], [u'b', (2,)]]
```
注意：DataFrame转化的RDD可能包含Row(col1='a')，它和'a'是不同的对象，所以如果与一般的RDD进行join，还需要索引Row取出数值。


### aggregate for RDD:

* Public doc for `aggregate` : *

> aggregate(zeroValue, seqOp, combOp)[source]
> Aggregate the elements of each partition, and then the results for all the partitions, using a given combine functions and a neutral “zero value.”
>The functions op(t1, t2) is allowed to modify t1 and return it as its result value to avoid object allocation; however, it should not modify t2.
>
>The first function (seqOp) can return a different result type, U, than the type of this RDD. Thus, we need one operation for merging a T into an U and one operation for merging two U


Doc for scala language for `aggregate`:
>Aggregate the elements of each partition, and then the results for all the partitions, using given combine functions and a neutral "zero value". This function can return a different result type, U, than the type of this
> RDD, T. Thus, we need one operation for merging a T into an U and one operation for merging two U's, as in scala.TraversableOnce. Both of these functions are allowed to modify and return their first argument instead of creating a new U to avoid memory allocation.  


> seqOp操作会`聚合各分区中`的元素，然后combOp操作把`所有分区的聚合结果` `再次聚合`，两个操作的初始值都是zeroValue.
> seqOp的操作是遍历`分区中的所有元素(T)`，第一个T跟zeroValue做操作，*结果再作为与第二个T做操作的zeroValue*，直到遍历完整个分区。
> combOp操作是把各分区聚合的结果，再聚合。`aggregate`函数返回一个跟RDD不同类型的值。因此，需要一个操作seqOp来把分区中的元素T合并成一个U，另外一个操作combOp把所有U聚合。

>zeroValue:
>the initial value for the accumulated result of each partition for the seqOp operator,
> and also the initial value for the combine results from different partitions for the combOp operator
> - this will typically be the neutral element (e.g. Nil for list concatenation or 0 for
> summation)
>seqOp
>an operator used to accumulate results within a partition
>combOp
>an associative operator used to combine results from different partitions

* Sample *

```py
S1:
>>> seqOp = (lambda x, y: (x[0] + y, x[1] + 1))
>>> combOp = (lambda x, y: (x[0] + y[0], x[1] + y[1]))
>>> sc.parallelize([1, 2, 3, 4]，4).aggregate((0, 0), seqOp, combOp)
(10, 4)

S2:
>>> sc.parallelize([1, 2, 3, 4，5]，3).aggregate((1,1), seqOp, combOp)
(19,9）
```

* Explanation *

S1:
|分区 | 元素|
|0    | 1   |
|1    | 2   |
|2    | 3   |
|3    | 4   |

区内聚合：
zerovalue = (0,0), 
seqOp = (lambda x, y: (x[0] + y, x[1] + 1)), progress as following:

|分区 | 元素 | zerovalue 前 | zerovalue 后  | 区结果  |  
| 0   | 1    | (0,0)        | (0 + 1, 0 + 1)| (1,1)   |
| 1   | 2    | (0,0)        | (0 + 2, 0 + 1)| (2,1)   |
| 2   | 3    | (0,0)        | (0 + 3, 0 + 1)| (3,1)   |
| 3   | 4    | (0,0)        | (0 + 4, 0 + 1)| (4,1)   |


区间聚合：
combOp = (lambda x, y: (x[0] + y[0], x[1] + y[1]))

|分区  | 区结果  |   zerovalue 前 | zerovalue 后   | 区间结果       |
| 0    | (1,1)   |   (0,0)        | (0 + 1, 0 + 1) | (1, 1)         |
| 1    | (2,1)   |   (1,1)        | (1 + 2, 1 + 1) | (3, 2)         |
| 2    | (3,1)   |   (3,2)        | (3 + 3, 2 + 1) | (6, 3)         |
| 3    | (4,1)   |   (6,3)        | (6 + 4, 3 + 1) | (10,4) 最终结果|

S2:
|分区 | 元素  |
|0    | 1,2   |
|1    | 3,4   |
|2    | 5     |

区内聚合：
zerovalue = (1,1), 
seqOp = (lambda x, y: (x[0] + y, x[1] + 1)), progress as following:

|分区 | 元素  | zerovalue 前 | zerovalue 后  | 区结果  |  
| 0   | *1,2   | (1,1)       | (1 + 1, 1 + 1)|        |
| 0   | 1,*2   | (2,2)       | (2 + 2, 2 + 1)| (4,3)  |
| 1   | *3,4   | (1,1)       | (1 + 3, 1 + 1)|    |
| 1   | 3,*4   | (4,2)       | (4 + 4, 2 + 1)| (8,3)  |
| 2   | 5     | (1,1)        | (1 + 5, 1 + 1)| (6,2)   |


区间聚合：
combOp = (lambda x, y: (x[0] + y[0], x[1] + y[1]))

|分区 | 区结果 |zerovalue 前 | zerovalue 后  | 区间结果  |  
| 0   | (4,3)  |  (1,1)       | (4 + 1, 3 + 1)| (5,4)  |
| 1   | (8,3)  |  (5,4)       | (5 + 8, 4 + 3)| (13,7)  |
| 2   | (6,2)  | (13,7)       | (13 + 6, 7 + 2)| (19,9)   |



### Actions for pyspark

```python
1.collect() #collect()的作用是输出经过转化操作的RDD的所有元素，前边也一直在用，不做举例。
2.count() #计算出RDD中元素的个数
    rdd = sc.parallelize([1,2,3])
    print(rdd.count()) #输出结果3
3.countByValue() #统计每个元素在RDD中出现的次数，以键值对的形式返回
    rdd = sc.parallelize([1,2,3,3])
    print(rdd.countByValue()) #输出结果{[1,1],[2,1],[3,2]}，表示1出现了一次，2出现了一次，3出现了两次
4.take(num) #返回RDD中前num个元素
    rdd = sc.parallelize([1,2,3,2,1])
    print(rdd.take(2)) #输出结果[1,2]
5.top(num) #返回RDD中最大的num个元素
    rdd = sc.parallelize([1,2,3,2,1])
    print(rdd.top(2)) #输出结果[3,2]，他所谓的大在纯数字的时候好理解，如果换成字符串，它内部应该是对字符串有编码的，应该是按照UTF-8
                      #具体使用的时候还是要测试一下，这个使用需谨慎。
6.takeOrdered(num) #返回RDD按照提供的顺序的前num个元素（其实应该就是按照从小到大的先后顺序）（RDD读取数据的顺序应该是按照从小到大的先后顺序）
    rdd = sc.parallelize([1,2,3,2,1])
    print(rdd.takeOrdered(2)) #输出结果[1,1]
7.takeSample(True/False,num,[seed]) #对数据进行抽样，True表示有放回的抽样，False表示无放回的抽样，
                                    #其实就是随机返回RDD中随机num个元素，[seed]可选，就是一个计算种子，当seed确定之后，返回的数据将确定
    rdd = sc.parallelize([1,2,3,2,1])
    print(rdd.takeSample(False,2)) #输出结果不确定
    #对有放回和无放回的讲解
    rdd = sc.parallelize([1,1,1]) #为了讲明白True和False的区别，我们将seed固定，因为数据都是1，所以无论seed是多少，输出结果都是一样的
    print(rdd.takeSample(True,4,1)) #有放回，输出结果为[1,1,1,1],因为有放回，所以需要抽4个样本是可以抽取的
    print(rdd.takeSample(False,4,1)) #无放回，输出结果为[1,1,1],因为无放回，所以需要抽取4个样本却只能抽取到3个
8.reduce() #累计运算，接收一个需要两个参数的方法，将RDD中的元素分别作用于这个方法，并进行累计运算，累计运算的意思就是：将第一个和第二个元素运算的结果再和第三个元素运算，以此类推。
    rdd = sc.parallelize([1,2,3,4,5])
    sum = rdd.reduce(lambda x,y: x + y) #我觉得你能看懂
    print(sum) #结果是15
9.fold() #其实他实现的也是累积运算，不过提供了累计运算的初始值，但是这个初始值的含义我并不是很明白，只是这道如果累加用它，初始值得是0
         #累乘运算初始值得是1
    rdd = sc.parallelize([2,3,4])
    sum = rdd.fold(0, lambda x,y: x+y) #累加运算
    mul = rdd.fold(1, lambda x,y: x*y) #累乘运算
    print("sum = " + str(sum))         #其中的str(sum)的含义是将数值型的数据sum转换成字符串型，因为"+"号前边是字符串型，这样"+"才能起到字符串连接符的作用
    print("mul = " + str(mul))
10.aggregate() #没看懂
11.foreach() #没看懂

```

