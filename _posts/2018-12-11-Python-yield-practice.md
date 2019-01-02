---
layout: post
title:  "Yeild Practice In Python"
categories: python
tags:  yield interateor generator
author: Root Wang
---

* content
{:toc}

### yield

#### 概念
要理解 yield 语句，关键要理解 python 的生成器。 用官网的说法1、2， 生成器就是一个返回迭代器（iterator）的函数。 和普通函数唯一的区别就是这个函数包含 yield 语句。

包含了 `yield` 的函数，就是一个`生成器`

Sample:
```python
# countdown.py
#
# A simple generator function

def countdown(n):
    print "Counting down from", n
    while n > 0:
        yield n
        n -= 1
    print "Done counting down"

# Example use
if __name__ == '__main__':
    for i in countdown(10):
        print i
```

>countdown(10) return a generator instead of running the function body, it is tricky!

另外要理解`yield`，必须理解什么是迭代，生成器

#### 迭代（Iterables）

`Iteration`：is a general term for taking each item of something, one after another. Any time you use a loop, explicit or implicit, to go over a group of items, that is iteration.

`iterable`： is an object that has an `__iter__` method which returns an `iterator`, or which defines a `__getitem__` method that can take sequential indexes starting from zero (and raises an IndexError when the indexes are no longer valid). So an `iterable` is an object that you can get an `iterator` from. 或者说迭代器是有一个`next（）`方法的对象。

`iterator`： is an object with `__iter__` and a `next()` (Python 2) or `__next__` (Python 3) method.

当创建一个list。一个一个读取list item的过程就叫迭代过程（Iteration）
```python
>>> mylist = [1, 2, 3]
>>> for i in mylist:
...    print(i)
1
2
3
```

`mylist` 是一个iterable， Everything you can use `for... in...` on is an iterable; lists, strings, files...
```python
>>> mylist = [x*x for x in range(3)]
>>> for i in mylist:
...    print(i)
0
1
4
```
这些`iterable`可以根据你的意愿尽可能多的读取其item，但是`所有的items被存储在内存中`。


```python
lass Fib:
    def __init__(self, n):
        self.prev = 0
        self.cur = 1
        self.n = n

    def __iter__(self):
        return self

    # python3 use next()
    def __next__(self):
        if self.n > 0:
            value = self.cur
            self.cur = self.cur + self.prev
            self.prev = value
            self.n -= 1
            return value
        else:
            raise StopIteration()
    # 兼容python2
    def next(self):
        return self.next()

f = Fib(10)
print([i for i in f])

#[1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```


#### 生成器（Generators）
生成器是一个迭代器（iterator）， 一种类型的（iterable）,`只可以迭代一次(you can only iterate over once)`. 生成器不会把所有的值存储在内存中，他们会在运行中生成值（`they generate the values on the fly`）
```python
>>> mygenerator = (x*x for x in range(3))
>>> for i in mygenerator:
...    print(i)
0
1
4
```
It is just the same except you used () instead of []. BUT, you cannot perform for i in mygenerator a second time since generators can only be used once: they calculate 0, then forget about it and calculate 1, and end calculating 4, one by one

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/interable_generator.jpg)

#### Yield
yield 就像函数`return`, 只是包含有`yield`函数的`function`将会返回一个生成器，而不是function本身.
```python
>>> def createGenerator():
...    mylist = range(3)
...    for i in mylist:
...        yield i*i
...
>>> mygenerator = createGenerator() # create a generator
>>> print(mygenerator) # mygenerator is an object!
<generator object createGenerator at 0xb7555c34>
>>> for i in mygenerator:
...     print(i)
0
1
4
```
> 当调用函数体`createGenerator`，所有在`函数体内的功能不会被运行`。而是`返回一个生成器对象`。

此代码执行过程：
1. 第一次`for`调用生成器`mygenerator`，它将从代码开始运行到碰见`yield`，然后返回yield后面的值（0×0）
2. 第二次执行`for`循环的时候，将从yield后面的代码执行，直到第二次碰见yield，并返回yield的值（1×1）
3. 以此类推


#### 示例解析

* 多yield与list连用
    * 生成器：

    ```python
    # Here you create the method of the node object that will return the generator
    def _get_child_candidates(self, distance, min_dist, max_dist):
    
        # Here is the code that will be called each time you use the generator object:
    
        # If there is still a child of the node object on its left
        # AND if distance is ok, return the next child
        if self._leftchild and distance - max_dist < self._median:
            yield self._leftchild
    
        # If there is still a child of the node object on its right
        # AND if distance is ok, return the next child
        if self._rightchild and distance + max_dist >= self._median:
            yield self._rightchild
    
        # If the function arrives here, the generator will be considered empty
        # there is no more than two values: the left and the right children
    ```

    * 调用程序：

    ```python
    # Create an empty list and a list with the current object reference
    result, candidates = list(), [self]
    
    # Loop on candidates (they contain only one element at the beginning)
    while candidates:
    
        # Get the last candidate and remove it from the list
        node = candidates.pop()
    
        # Get the distance between obj and the candidate
        distance = node._get_dist(obj)
    
        # If distance is ok, then you can fill the result
        if distance <= max_dist and distance >= min_dist:
            result.extend(node._values)
    
        # Add the children of the candidate in the candidates list
        # so the loop will keep running until it will have looked
        # at all the children of the children of the children, etc. of the candidate
        candidates.extend(node._get_child_candidates(distance, min_dist, max_dist))
    
    return result
    ```
执行过程：
1. 第一此while执行，`candidates`将会扩展list，添加生成器结果`node._get_child_candidates(distance, min_dist, max_dist)`到自己。
> 为什么没有使用`.next()`,`__next__()`,`for`等方法，依然会触发生成器工作呢？ 原因是`list.extend`隐性的使用了`for`循环，所以得以使生成器工作。
2. `node._get_child_candidates`会根据`if else`判断，返回相应的值，即`self._leftchild`或者`self._rightchild`

下面是一个更直观的例子

* 多yield示例

```python
def countdown(n):
    print("Counting down from", n)
    while n > 0:
        print("1st yield")
        yield n
        print("2st yield")
        yield "---" + str(n)
        n -= 1
    print("Done counting down")

# Example use
if __name__ == '__main__':
    w = countdown(10)
    l = list()
    l.extend(w)
    print(l)
```
>Result: [10, '---10', 9, '---9', 8, '---8', 7, '---7', 6, '---6', 5, '---5', 4, '---4', 3, '---3', 2, '---2', 1, '---1']

执行过程：
1. l.extend()即为`for`循环处理`w`，触发生成器。
2. l.extend()第一次循环，执行code到第一个yield, 返回10, append 10到list `l`，结束
3. l.extend()第二次循环，从第一个yield开始执行，到第二个yield结束，返回"---10" append "---10"到list `l`
4. l.extend()第三次循环，n减一，执行while函数体到第一个yield, 返回9,append 9到list `l`,结束
5. l.extend()第四次循环，从第一个yield开始执行，到第二个yield结束，返回"---9",然后append "---9"到list `l`
6. 以此类推，直到 n不大于0,结束整个过程

* 控制生成器的消费

```python
>>> class Bank(): # Let's create a bank, building ATMs
...    crisis = False
...    def create_atm(self):
...        while not self.crisis:
...            yield "$100"
>>> hsbc = Bank() # When everything's ok the ATM gives you as much as you want
>>> corner_street_atm = hsbc.create_atm()
>>> print(corner_street_atm.next())
$100
>>> print(corner_street_atm.next())
$100
>>> print([corner_street_atm.next() for cash in range(5)])
['$100', '$100', '$100', '$100', '$100']
>>> hsbc.crisis = True # Crisis is coming, no more money!
>>> print(corner_street_atm.next())
<type 'exceptions.StopIteration'>
>>> wall_street_atm = hsbc.create_atm() # It's even true for new ATMs
>>> print(wall_street_atm.next())
<type 'exceptions.StopIteration'>
>>> hsbc.crisis = False # The trouble is, even post-crisis the ATM remains empty
>>> print(corner_street_atm.next())
<type 'exceptions.StopIteration'>
>>> brand_new_atm = hsbc.create_atm() # Build a new one to get back in business
>>> for cash in brand_new_atm:
...    print cash
$100
$100
$100
$100
$100
$100
$100
$100
$100
...
```



