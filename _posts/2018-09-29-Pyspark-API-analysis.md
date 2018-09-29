---
layout: post
title:  "Pyspark API Analysis"
categories: Spark
tags:  bigdata structure mapreduce spark
author: Root Wang
---

* content
{:toc}


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






