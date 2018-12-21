---
layout: post
title:  "_xx __xx __xx__ usageIn Python"
categories: python
tags:  syntax
author: Root Wang
---

* content
{:toc}

### _xxx
弱“内部使用”标识 
如：”from M import *”，将不导入所有以下划线开头的对象，包括包、模块、成员。`除非__all__显性声明` 
表明该方法或属性不应该去调用 
Python中不存在真正的私有方法。为了实现类似于c++中私有方法，可以在类的方法或属性前加一个“_”单下划线，意味着该方法或属性不应该去调用，它并不属于API。

上干货：
File tree
```sh
.
├── call.py
└── lib
    ├── __init__.py
    ├── __init__.pyc
    ├── test.py
    └── test.pyc
``` 

__init__.py
```python
from test import *
print("lib:",dir())
#__all__ = [ 'BaseClass', '_Test', '_var1']
```

lib/test.py
```python
#__all__ = [ 'BaseClass', '_Test', '_var1']

class BaseClass(object):
    def __init__(self):
        self.name = 'Base'
    def __method(self):
        print("I'm Base")
    def method(self):
        self.__method()
    def _m1(self):
        print('i am base private')
    def get_var(self):
        print(_var1)

class _Test(object):
    def test(self):
        print("_Test class , function test")
 
_var1 = "aaaaaaaaaaaaaa"
```

call.py
```python
#!/bin/python
from lib import *

bc = BaseClass()
bc.method()
bc._m1()
bc.get_var()
test = _Test()
var = _var1
```

Result:
```sh
python call.py
------------

('lib:', ['BaseClass', '__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__', 'test'])
I'm Base
i am base private
aaaaaaaaaaaaaa
Traceback (most recent call last):
  File "call.py", line 10, in <module>
    test = _Test()
NameError: name '_Test' is not defined
```
> Indicate the Class _Test and vairable _var1 is not import from lib
> Uncomment __all__ in both __init__.py test.py, all is successful.
> _var1 can be get from inner function of class BaseClass althout it is not imported to out.
> All object with prefix '_', can be called through explicitly importing. Namely, add "from test import _Test, _var1, BaseClass" to __init__.py and "from lib import _Test, _var1, BaseClass" to call.py 


### _

1. 在解释器中：在这种情况下，"_"代表交互式解释器会话中上一条执行的语句的结果。这种用法首先被标准CPython解释器采用，然后其他类型的解释器也先后采用
```python
>>>print(1)
>>>1

>>>print(_)
>>>1
```

2. 作为一个名称：这与上面一点稍微有些联系，此时"_"作为临时性的名称使用。这样，当其他人阅读你的代码时将会知道，你分配了一个特定的名称，但是并不会在后面再次用到该名称。例如，下面的例子中，你可能对循环计数中的实际值并不感兴趣，此时就可以使用"_"。
```python
for _ in range(3):
    do_something()
```

### xxx_
只是为了避免与python关键字的命名冲突

### __xxx

名称（具体为一个方法名）前双下划线（__）的用法并不是一种惯例，对解释器来说它有特定的意义。Python中的这种用法是为了避免与子类定义的名称冲突。

Python文档指出，“__spam”这种形式（至少两个前导下划线，最多一个后续下划线）的任何标识符将会被“_classname__spam”这种形式原文取代，在这里“classname”是去掉前导下划线的当前类名。例如下面的例子：

```python
class BaseClass(object):
    def __init__(self):
        self.name = 'Base'
    def __method(self):
        print("I'm Base")
    def method(self):
        self.__method()
    def _m1(self):
        print('i am base private')

class SubClass(BaseClass):
    def __init__(self):
        super(SubClass, self).__init__()
        self.name = 'Sub'
    def __method(self):  # 覆写父类__method()
        print("I'm Sub")
    def method(self):    # 覆写父类method()
        self.__method()
sub = SubClass()
base = BaseClass()

print(dir(sub))
print(dir(base))
sub.__method()
```

result:
```sh
['_BaseClass__method', '_SubClass__method', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_m1', 'method', 'name']
['_BaseClass__method', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_m1', 'method', 'name']
Traceback (most recent call last):
  File "/syshome/pycharm/test.py", line 95, in <module>
    sub.__method()
AttributeError: 'SubClass' object has no attribute '__method'
```
> Found the function `__method` is named to `_SubClass__method`, so you can not call this function by `sub.__method()`, but can call this function by `sub._SubClass__method()`

### __xxx__
“魔术”对象或属性 
许多特殊的代码会调用对应的魔术方法。下面是总结的部分我遇到过的魔术方法：

#### __init__()
这个很常见，就是创建一个类的实例的时候会调用，相当于构造函数。

#### __call__()
如果一个类实现了这个函数，那么这个类就是“可调用对象”，可以通过如下方式调用：
```python
class C:
    def __call__(self, name):
        print(name)

c = C()
c('Hello!')  # 会调用__call__()方法

输出：
```sh
Hello!
1
```
#### __getitem__（）
```python
class C:
    def __init__(self):
        self.list = [1,2,3,4,5]

    def __getitem__(self, item):
        return self.list[item]

c = C()

for i in range(5):
    print(c[i]) # 会调用__getitem__()方法
```

#### __iter__()和__next__()
之所以把这两个放在一起，是因为我见到的这两个是在迭代器操作的时候同时出现的。直接看代码：

```python
class IterDemo:
    def __iter__(self):
        print('__iter__() is called')
        return NextDemo()   # 需要返回一个实现了__next__()方法的类的对象

class NextDemo:
    def __next__(self):
        print('__next__() is called')

iterDemo = IterDemo()

nextDemo = iter(iterDemo)   # 调用iterDemo.__iter__()方法
next(nextDemo)              # 调用nextDemo.__next__()方法
```

#### __setattr__（）
用在类内给成员变量赋值。
```python
class C:
    def __init__(self):
        self.a = 1        #调用一次__setattr__()

    def __setattr__(self, key, value):
        dict = self.__dict__
        dict[key] = value
        print("__setattr__ !")

    def modify(self,new_a):
        self.a = new_a    #调用一次__setattr__()

c = C()
c.modify(2)
```
输出：
```sh
__setattr__ !
__setattr__ !
```
