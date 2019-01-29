---
layout: post
title:  "属性与描述符"
categories: PYTHON
tags:  attribution descriptor
author: Root Wang
---

* content
{:toc}

### @property装饰器

在Python中我们使用@property装饰器来把***对属性的访问采用对函数的调用***。

那么为什么要这样做呢？因为`@property`让我们将自定义的代码同***变量的访问/设定联系在了一起***，同时为你的类保持一个简单的访问属性的接口。

举个栗子，假如我们有一个需要表示电影的类：
```python
class Movie(object):
 def __init__(self, title, description, score, ticket):
 self.title = title
 self.description = description
 self.score = scroe
 self.ticket = ticket
```
你开始在项目的其他地方使用这个类，但是之后你意识到：_如果不小心给电影打了负分怎么办？_你觉得这是错误的行为，希望Movie类可以阻止这个错误。 你首先想到的办法是将Movie类修改为这样：

```python
class Movie(object):
 def __init__(self, title, description, score, ticket):
 self.title = title
 self.description = description
　　　　 self.ticket = ticket
 if score < 0:
  raise ValueError("Negative value not allowed:{}".format(score))
 self.score = scroe
```
但这行不通。因为其他部分的代码都是直接通过Movie.score来赋值的。_这个新修改的类只会在__init__方法中捕获错误的数据，但对于已经存在的类实例就无能为力了。如果有人试着运行m.scrore= -100，那么谁也没法阻止。_那该怎么办？

*Python的property解决了这个问题。*

我们可以这样做
```python
class Movie(object):
 def __init__(self, title, description, score):
 	self.title = title
 	self.description = description
 	self.score = score
　　　  self.ticket = ticket
  
 @property
 def score(self):
 	return self.__score
  
 @score.setter
 def score(self, score):
 	if score < 0:
  		raise ValueError("Negative value not allowed:{}".format(score))
 	self.__score = score
  
 @score.deleter
 def score(self):
 	raise AttributeError("Can not delete score")
```
这样在任何地方修改score都会检测它是否小于0。

***property的不足***

对property来说，**最大的缺点就是它们不能重复使用**。举个例子，假设你想为ticket字段也添加非负检查。

下面是修改过的新类：

```python
class Movie(object):
 def __init__(self, title, description, score, ticket):
 self.title = title
 self.description = description
 self.score = score
 self.ticket = ticket
  
 @property
 def score(self):
 return self.__score
  
  
 @score.setter
 def score(self, score):
 if score < 0:
  raise ValueError("Negative value not allowed:{}".format(score))
 self.__score = score
  
 @score.deleter
 def score(self):
 raise AttributeError("Can not delete score")
  
  
 @property
 def ticket(self):
 return self.__ticket
  
 @ticket.setter
 def ticket(self, ticket):
 if ticket < 0:
  raise ValueError("Negative value not allowed:{}".format(ticket))
 self.__ticket = ticket
  
  
 @ticket.deleter
 def ticket(self):
 raise AttributeError("Can not delete ticket")
```
可以看到代码增加了不少，但重复的逻辑也出现了不少。_虽然property可以让类从外部看起来接口整洁漂亮，但是却做不到内部同样整洁漂亮。_

描述符登场

### 什么是描述符？
官方说法：python描述符是一个“绑定行为”的对象属性，在描述符协议中，它可以通过方法重写属性的访问。这些方法有 __get__(), __set__(), 和__delete__()。如果这些方法中的任何一个被定义在一个对象中，那么这个对象就是一个描述符。 
说啥呢，描述符是一个对象？？？我觉着吧，描述符应该是一个类，由这个类实例化的对象成为描述符对象 
这么说来，描述符本质就是一个新式类,在这个新式类中,至少实现了__get__(),__set__(),__delete__()中的一个，这三者也被称为描述符协议。


The default behavior for attribute access is to get, set, or delete the attribute from an object's dictionary. For instance, a.x has a lookup chain starting witha.__dict__[‘x'], then type(a).__dict__[‘x'], and continuing through the base classes of type(a) excluding metaclasses. If the looked-up value is an object defining one of the descriptor methods, then Python may override the default behavior and invoke the descriptor method instead. Where this occurs in the precedence chain depends on which descriptor methods were defined.—–摘自官方文档

简单的说描述符会改变一个属性的基本的获取、设置和删除方式。

先看如何用描述符来解决上面 property逻辑重复的问题。
```python
class Integer(object):
 def __init__(self, name):
 self.name = name
  
 def __get__(self, instance, owner):
 return instance.__dict__[self.name]
  
 def __set__(self, instance, value):
 if value < 0:
  raise ValueError("Negative value not allowed")
 instance.__dict__[self.name] = value
  
class Movie(object):
 score = Integer('score')
 ticket = Integer('ticket')
```
因为描述符优先级高并且会改变默认的get、set行为，这样一来，当我们访问或者设置Movie().score的时候都会受到描述符Integer的限制。

不过我们也总不能用下面这样的方式来创建实例。
```python
a = Movie()
a.score = 1
a.ticket = 2
a.title = 'test'
a.descript = '…'
```
这样太生硬了，所以我们还缺一个构造函数。
```python
class Integer(object):
 def __init__(self, name):
 self.name = name
  
 def __get__(self, instance, owner):
 if instance is None:
  return self
 return instance.__dict__[self.name]
  
 def __set__(self, instance, value):
 if value < 0:
  raise ValueError('Negative value not allowed')
 instance.__dict__[self.name] = value
  
  
class Movie(object):
 score = Integer('score')
 ticket = Integer('ticket')
  
 def __init__(self, title, description, score, ticket):
 self.title = title
 self.description = description
 self.score = score
 self.ticket = ticket

```
这样在获取、设置和删除score和ticket的时候都会进入Integer的__get__ 、 __set__ ，从而减少了重复的逻辑。

现在虽然问题得到了解决，但是你可能会好奇这个描述符到底是如何工作的。具体来说，在__init__函数里访问的是自己的self.score和self.ticket，怎么和类属性score和ticket关联起来的？

==================================

#### 数据描述符 VS 非数据描述符
* 数据描述符：至少实现了 __get__()和__set__()
* 非数据描述符:没有实现 __set__()

##### 这两者的区别
***在访问属性时的搜索顺序上： ***
搜索链（或者优先链）的顺序：数据描述符＞实体属性（存储在实体的dict中）>非数据描述符。解释如下： 

1. 获取一个属性的时候： 
    1. 首先，看这个属性是不是一个数据描述符，如果是，就直接执行描述符的__get__()，并返回值。 
    2. 其次，如果这个属性不是数据描述符，那就按常规去从__dict__里面取。如果__dict__里面还没有，但这是一个非数据描述符，则执行非数据描述符的__get__()方法，并返回。 
    3. 最后，找不到的属性触发__getattr__()执行 

2. 而设置一个属性的值时，访问的顺序又有所不同，请看以下讲解。 
三个方法（协议）： 
```python
__get__(self, instance, owner):调用一个属性时,触发 
__set__(self, instance, value):为一个属性赋值时,触发 
__delete__(self, instance):采用del删除属性时,触发
```
其中，instance是这个描述符属性所在的类的实体，而owner是描述符所在的类。 
那么以上的 self, instance owner 到底指的是个什么东西呢？我们先来看一个描述符定义：

```python
class Desc(object):
    def __get__(self, instance, owner):
        print("__get__...")
        print("self : \t\t", self)
        print("instance : \t", instance)
        print("owner : \t", owner)
        print('='*40, "\n")     
    def __set__(self, instance, value):
        print('__set__...')
        print("self : \t\t", self)
        print("instance : \t", instance)
        print("value : \t", value)
        print('='*40, "\n")
class TestDesc(object):
    x = Desc()
#以下为测试代码
t = TestDesc()
t.x
#以下为输出信息：
__get__...
self :          <__main__.Desc object at 0x0000000002B0B828>
instance :      <__main__.TestDesc object at 0x0000000002B0BA20>
owner :      <class '__main__.TestDesc'>
```

可以看到，实例化类TestDesc后，调用对象t访问其属性x，会自动调用类Desc的__get__方法，由输出信息可以看出： 
* ① self: Desc的实例对象，其实就是TestDesc的属性x 
* ② instance: TestDesc的实例对象，其实就是t 
* ③ owner: 即谁拥有这些东西，当然是 TestDesc这个类，它是最高统治者，其他的一些都是包含在它的内部或者由它生出来的

包含这三个方法的新式类称为描述符,***由这个类产生的实例进行属性的调用/赋值/删除，并不会触发这三个方法**，那何时,何地,会触发这三个方法的执行呢？

#### 描述符有什么用
* 可以在设置属性时，做些检测等方面的处理
* 缓存？
* 设置属性不能被删除？那定义__delete__()方法，并raise 异常。
* 还可以设置只读属性
* 把一个描述符作为某个对象的属性。这个属性要更改，比如增加判断，或变得更复杂的时候，所有的处理只要在描述符中操作就行了。
* 对属性操作提供限制，验证，管理等相关权限的操作
* 这些都是摘抄的，我确实不知道描述符有什么用，也不知道为什么要用描述符，先记下吧。

#### 描述符触发执行条件以及访问优先级
一 描述符本身应该定义成新式类,owner类也应该是新式类 
二 必须把描述符定义成这个类的类属性，不能为定义到构造函数中 
三 要严格遵循该优先级,优先级由高到底分别是 
    1. 类属性 
    2. 数据描述符 
    3. 实例属性 
    4. 非数据描述符 
    5. 找不到的属性触发__getattr__()

##### 类属性优先级大于数据描述符
```python
class Str:
    def __get__(self, instance, owner):
        print('Str调用')
    def __set__(self, instance, value):
        print('Str设置...')
    def __delete__(self, instance):
        print('Str删除...')
class People:
    name=Str()
    def __init__(self,name,age): #name被Str类代理
        self.name=name
        self.age=age
```
> 基于上面的演示,我们已经知道,在一个类中定义描述符它就是一个类属性,存在于类的属性字典中,而不是实例的属性字典
> 那既然描述符被定义成了一个类属性,直接通过类名也一定可以调用吧,没错People.name 
> 恩,调用类属性name,本质就是在调用描述符Str,触发了__get__()，类去操作属性时,会把None传给instance

```python
People.name='egon'  #那赋值呢,我去,并没有触发__set__()
del People.name     #赶紧试试del,我去,也没有触发__delete__()

原因:描述符在使用时被定义成另外一个类的类属性,因而类属性比二次加工的描述符伪装而来的类属性有更高的优先级
People.name 调用类属性name,找不到就去找描述符伪装的类属性name,触发了__get__()
People.name='egon'
#那赋值呢,直接赋值了一个类属性,它拥有更高的优先级,相当于覆盖了描述符,肯定不会触发描述符的__set__()
del People.name #同上
```

##### 数据描述符优先级大于实例属性
要验证，需要将实例的属性名与类的数据描述符同名
```python
class Str:
    def __get__(self, instance, owner):
        print('Str调用')
    def __set__(self, instance, value):
        print('Str设置...')
    def __delete__(self, instance):
        print('Str删除...')

class People:
    name=Str()
    def __init__(self,name,age): 
        self.name=name
        self.age=age

p1=People('egon',18)

> 如果描述符是一个数据描述符(即有__get__又有__set__),那么p1.name的调用与赋值都是触发描述符的操作,
> 与p1本身无关了,相当于覆盖了实例的属性
p1.name='egonnnnnn'
p1.name
print(p1.__dict__)

> 实例属性字典中没有name,因为name是数据描述符,优先级高于实例属性,查看/赋值/删除都是跟描述符有关,与实例无关
del p1.name
```

##### 实例属性优先级大于非数据描述符
```python
class Foo:
    def func(self):
        print('我胡汉三又回来了')
f1=Foo()
f1.func() #调用类的方法,也可以说是调用非数据描述符
#函数是一个非数据描述符对象(一切皆对象么)
print(dir(Foo.func))
print(hasattr(Foo.func,'__set__'))
print(hasattr(Foo.func,'__get__'))
print(hasattr(Foo.func,'__delete__'))
#有人可能会问,描述符不都是类么,函数怎么算也应该是一个对象啊,怎么就是描述符了
#笨蛋哥,描述符是类没问题,描述符在应用的时候不都是实例化成一个类属性么
#函数就是一个由非描述符类实例化得到的对象
#没错，字符串也一样

f1.func='这是实例属性啊'
print(f1.func)

del f1.func #删掉了非数据
f1.func()
class Foo:
    def __get__(self, instance, owner):
        print('get')
class Room:
    name=Foo()
    def __init__(self,name,width,length):
        self.name=name
        self.width=width
        self.length=length

#name是一个非数据描述符,因为name=Foo()而Foo没有实现set方法,因而比实例属性有更低的优先级
#对实例的属性操作,触发的都是实例自己的
r1=Room('厕所',1,1)
r1.name
r1.name='厨房'
================
厕所
厨房
```

#### 描述符使用
python是弱类型语言，即参数的赋值没有类型限制，下面我们通过描述符机制来实现类型限制功能
```python
class Typed:
    def __init__(self,name,expected_type):
        self.name=name
        self.expected_type=expected_type
    def __get__(self, instance, owner):
        print('get--->',instance,owner)
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        print('set--->',instance,value)
        if not isinstance(value,self.expected_type):
            raise TypeError('Expected %s' %str(self.expected_type))
        instance.__dict__[self.name]=value
    def __delete__(self, instance):
        print('delete--->',instance)
        instance.__dict__.pop(self.name)

def typeassert(**kwargs):
    def decorate(cls):
        print('类的装饰器开始运行啦------>',kwargs)
        for name,expected_type in kwargs.items():
            # 相当于给类People添加了3个类属性，即 name = Typed(name, str); age = Typed(age, int); salary = Typed(salary, int)
            # 初始化函数__init__的优先级小于数据描述符，所以类的属性会覆盖__init__的属性。 
            setattr(cls,name,Typed(name,expected_type))
        return cls
    return decorate
#有参:1.运行typeassert(...)返回结果是decorate,此时参数都传给kwargs 2.People=decorate(People)
@typeassert(name=str,age=int,salary=float) 
class People:
    def __init__(self,name,age,salary):
        self.name=name
        self.age=age
        self.salary=salary

print(People.__dict__)
p1=People('egon',18,3333.3)

=============================
set---> <__main__.People object at 0x7f589be544a8> egon
set---> <__main__.People object at 0x7f589be544a8> 18
set---> <__main__.People object at 0x7f589be544a8> 3333.3
```

#### 描述符使用陷阱
为了让描述符能够正常工作，它们必须定义在类的层次上。如果你不这么做，那么Python无法自动为你调用__get__和__set__方法。 
访问类层次上的描述符可以自动调用__get__。但是访问实例层次上的描述符只会返回描述符本身，真是魔法一般的存在啊。 
确保实例的数据只属于实例本身，否则所有的实例都共享相同的数据
```python
class Desc(object):
    def __init__(self, name):
        self.name = name
    def __get__(self, instance, owner):
        print("__get__...")
        print('name = ', self.name)
        print('=' * 40, "\n")
class TestDesc(object):
    x = Desc('x')

    def __init__(self):
        self.y = Desc('y')

# 以下为测试代码
t = TestDesc()
t.x
print(t.__dict__)
print(t.y)
'''
输出结果：
__get__...
name =  x
======================================== 
{'y': <__main__.Desc object at 0x7f514d6ba9e8>}
<__main__.Desc object at 0x7f514d6ba9e8>
'''
```

#### 如何检测一个对象是不是描述符
如果把问题换成——一个对象要满足什么条件，它才是描述符呢——那是不是回答就非常简单了？ 
只要定义了（set,get,delete）方法中的任意一种或几种，它就是个描述符。 
那么，继续问：怎么判断一个对象定义了这三种方法呢？ 
立马有人可能就会回答：你是不是傻啊？看一下不就看出来了。。。 
问题是，你看不到的时候呢？python内置的staticmethod，classmethod怎么看？ 
正确的回答应该是：看这个对象的dict。 
写到这里，我得先停一下，来解释一个问题。不知道读者有没有发现，上面我一直再说“对象”，“对象”，而实际上指的明明是一个类啊？在python中，这样称呼又是妥当的。因为，“一切皆对象”，类，不过也是元类的一种对象而已。 
要看对象的dict好办，直接dir(对象）就行了。现在可以写出检测对象是不是描述符的方法了：

```python
def has_descriptor_attrs(obj):
    return set(['__get__', '__set__', '__delete__']).intersection(dir(obj))

def is_descriptor(obj):
    """obj can be instance of descriptor or the descriptor class"""
    return bool(has_descriptor_attrs(obj))

def has_data_descriptor_attrs(obj):
    return set(['__set__', '__delete__']) & set(dir(obj))

def is_data_descriptor(obj):
    return bool(has_data_descriptor_attrs(obj))

print(is_descriptor(classmethod), is_data_descriptor(classmethod))
print(is_descriptor(staticmethod), is_data_descriptor(staticmethod))
print(is_data_descriptor(property))
'''
输出：
(True, False)
(True, False)
True
看来，特性（property）是数据描述符
'''
```

### @property把函数调用伪装成对属性的访问
```python
class Foo:
  @property
  def attr(self):
    print('getting attr')
    return 'attr value'

  def bar(self): pass
foo = Foo()
```

上面这个例子中， attr 是类 Foo 的一个成员函数，可通过语句 foo.attr() 被调用。 但当它被 @property 修饰后，这个成员函数将不再是一个函数，而变为一个描述符。 bar 是一个未被修饰的成员函数。 type(Foo.attr) 与 type(Foo.bar) 的结果分别为： 

```python class Foo: @property def AAA(self): print('get的时候运行我啊') @AAA.setter def AAA(self,value): print('set的时候运行我啊') @AAA.deleter def AAA(self): print('delete的时候运行我啊') #只有在属性AAA定义property后才能定义AAA.setter,AAA.deleter f1=Foo() f1.AAA f1.AAA='aaa' del f1.AAA #方式2 class Foo: def get_AAA(self): print('get的时候运行我啊') def set_AAA(self,value): print('set的时候运行我啊') def delete_AAA(self): print('delete的时候运行我啊') AAA=property(get_AAA,set_AAA,delete_AAA) #内置property三个参数与get,set,delete一一对应 f1=Foo() f1.AAA f1.AAA='aaa' del f1.AAA ``` property将一个函数变成了类似于属性的使用，无非只是省略了一个括号而已，可是这有什么意义？以属性的方式来调用函数，换句话说，我以为我调用的是属性，但是其实是函数，这样就完成了一个封装，不需要setter和getter，而直接将setter和getter内嵌进去，大大减少了代码量，使代码简洁美观 案例一： ```python class Goods: def __init__(self): # 原价 self.original_price = 100 # 折扣 self.discount = 0.8 @property
    def price(self):
        # 实际价格 = 原价 * 折扣
        new_price = self.original_price * self.discount
        return new_price

    @price.setter
    def price(self, value):
        self.original_price = value

    @price.deleter
    def price(self):
        del self.original_price

obj = Goods()
obj.price         # 获取商品价格
obj.price = 200   # 修改商品原价
print(obj.price)
del obj.price     # 删除商品原价
```

案例二：

#实现类型检测功能
#第一关：

```python
class People:
    def __init__(self,name):
        self.name=name

    @property
    def name(self):
        return self.name

# p1=People('alex') 
```
#property自动实现了set和get方法属于数据描述符,比实例属性优先级高,
#所以你这面写会触发property内置的set,抛出异常

#第二关：修订版
```python
class People:
    def __init__(self,name):
        self.name=name #实例化就触发property

    @property
    def name(self):
        # return self.name #无限递归
        print('get------>')
        return self.DouNiWan

    @name.setter
    def name(self,value):
        print('set------>')
        self.DouNiWan=value

    @name.deleter
    def name(self):
        print('delete------>')
        del self.DouNiWan

p1=People('alex') #self.name实际是存放到self.DouNiWan里
print(p1.name)
print(p1.name)
print(p1.name)
print(p1.__dict__)

p1.name='egon'
print(p1.__dict__)

del p1.name
print(p1.__dict__)
```

#第三关:加上类型检查

```python
class People:
    def __init__(self,name):
        self.name=name #实例化就触发property

    @property
    def name(self):
        # return self.name #无限递归
        print('get------>')
        return self.DouNiWan

    @name.setter
    def name(self,value):
        print('set------>')
        if not isinstance(value,str):
            raise TypeError('必须是字符串类型')
        self.DouNiWan=value

    @name.deleter
    def name(self):
        print('delete------>')
        del self.DouNiWan

p1=People('alex') #self.name实际是存放到self.DouNiWan里
p1.name=1
```
