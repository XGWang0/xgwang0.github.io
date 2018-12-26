---
layout: post
title:  "Closure Understand And Sample In Python"
categories: python
tags:  closure decorators
author: Root Wang
---

* content
{:toc}

### 闭包
在计算机科学中，闭包（Closure）是词法闭包（Lexical Closure）的简称，是引用了自由变量的函数。这个被引用的自由变量将和这个函数一同存在，即使已经离开了创造它的环境也不例外。所以，有另一种说法认为闭包是由函数和与其相关的引用环境组合而成的实体。闭包在运行时可以有多个实例，不同的引用环境和相同的函数组合可以产生不同的实例。



### 变量的作用域

#### 概念
在Python程序中`创建、改变、查找变量名`时，都是在一个保存变量名的空间中进行，我们称之为`命名空间`，也被称之为`作用域`。python的作用域是静态的，*在源代码中变量名被赋值的位置决定了该变量能被访问的范围。即Python变量的作用域由变量所在源代码中的位置决定。*

#### 高级语言对数据类型的使用过程
一般的高级语言在使用变量时，都会有下面4个过程。当然在不同的语言中也会有着区别。

* 声明变量：让编辑器知道有这一个变量的存在
* 定义变量：为不同数据类型的变量分配内存空间
* 初始化：赋值，填充分配好的内存空间
* 引用：通过引用对象(变量名)来调用内存对象(内存数据)

#### 作用域的产生
就作用域而言，Python与C有着很大的区别，`在Python中并不是所有的语句块中都会产生作用域`。只有当变量在`Module(模块)、Class(类)、def(函数)`中定义的时候，才会有作用域的概念。看下面的代码：

```python
#!/usr/bin/env python
def func():
    variable = 100
    print variable
print variable

代码的输出为：
NameError: name 'variable' is not defined
```

在作用域中定义的变量，一般只在作用域中有效。 需要注意的是：在`if-elif-else、for-else、while、try-except\try-finally`等关键字的语句块中并不会产成作用域。看下面的代码：
```python
if True:
    variable = 100
    print (variable)
print ("******")
print (variable)

代码的输出为：
100
******
100
```
所以，可以看到，虽然是在if语句中定义的variable变量，但是在if语句外部仍然能够使用。

#### 作用域的类型：
在Python中，使用一个变量时并不严格要求需要预先声明它，但是**在真正使用它之前，它必须被绑定到某个内存对象(被定义、赋值)**；
这种变量名的绑定将在**当前作用域中引入新的变量，同时屏蔽外层作用域中的同名变量**。

* L(local)局部作用域
局部变量包含在def关键字定义的语句块中，即在函数中定义的变量。**每当函数被调用时都会创建一个新的局部作用域**。Python中也有递归，即自己调用自己，每次调用都会创建一个新的局部命名空间。在函数内部的变量声明，除非特别的声明为全局变量，否则均默认为局部变量。有些情况需要在函数内部定义全局变量，这时可以使用global关键字来声明变量的作用域为全局。局部变量域就像一个 栈，仅仅是暂时的存在，依赖创建该局部作用域的函数是否处于活动的状态。所以，一般建议尽量少定义全局变量，因为全局变量在模块文件运行的过程中会一直存在，占用内存空间。
注意：如果需要在函数内部对全局变量赋值，需要在函数内部通过global语句声明该变量为全局变量。

* E(enclosing)嵌套作用域
E也包含在def关键字中，E和L是相对的，E相对于更上层的函数而言也是L。与L的区别在于，对一个函数而言，L是定义在此函数内部的局部作用域，而E是定义在此函数的上一层父级函数的局部作用域。主要是为了实现Python的闭包，而增加的实现。

* G(global)全局作用域
即在模块层次中定义的变量，每一个模块都是一个全局作用域。也就是说，在模块文件顶层声明的变量具有全局作用域，从外部开来，模块的全局变量就是一个模块对象的属性。
注意：全局作用域的作用范围仅限于单个模块文件内

* B(built-in)内置作用域
系统内固定模块里定义的变量，如预定义在builtin 模块内的变量。

#### 变量名解析LEGB法则
搜索变量名的优先级：**局部作用域 > 嵌套作用域 > 全局作用域 > 内置作用域**

LEGB法则： 当在函数中使用未确定的变量名时，Python会按照优先级依次搜索4个作用域，以此来确定该变量名的意义。首先搜索局部作用域(L)，之后是上一层嵌套结构中def或lambda函数的嵌套作用域(E)，之后是全局作用域(G)，最后是内置作用域(B)。按这个查找原则，在第一处找到的地方停止。如果没有找到，则会出发NameError错误。

下面举一个实用LEGB法则的例子：
```python
globalVar = 100           #G

def test_scope():
    enclosingVar = 200    #E
    def func():
        localVar = 300    #L
print __name__            #B
```

#### 实例讲解
下面我们来看几个例子，加深对于Python变量作用域的理解：
1. 示例1
```python
def func():
    variable = 300
    print variable

variable = 100
func()
print variable

代码的输出为：
300
100
```

本例中，有一个全局变量variable，值为100，有一个作用域为func函数内部的局部变量variable，值为300，func内部输出variable变量值时，优先搜索局部作用域，所以打印输出300。


2. 示例2
```python
def test_scopt():
    variable = 200
    print variable
    def func():
        print variable   #这里的变量variable在E中绑定了内存对象200，为函数func()引入了一个新的变量
    func()
variable = 100
test_scopt()
print variable
```

有两个variable变量，对于func函数来说，局部作用域中没有variable变量，所以打印时，在L层找不到，所以进一步在E层找，即在上层函数test_scopt中定义的variable，找到并输出。

3. 示例3
```python
variable = 300
def test_scopt():
    print variable   #variable是test_scopt()的局部变量，但是在打印时并没有绑定内存对象。
    variable = 200

test_scopt()
print variable

代码输出为：
UnboundLocalError: local variable 'variable' referenced before assignment
``

上面的例子会报出错误，因为在执行程序时的预编译能够在test_scopt()中找到局部变量variable(对variable进行了赋值)。在局部作用域找到了变量名，所以不会升级到嵌套作用域去寻找。但是在使用print语句将变量variable打印时，局部变量variable并有没绑定到一个内存对象(没有定义和初始化，即没有赋值)。本质上还是Python调用变量时遵循的LEGB法则和Python解析器的编译原理，决定了这个错误的发生。所以，在调用一个变量之前，需要为该变量赋值(绑定一个内存对象)。

注意：为什么在这个例子中触发的错误是UnboundLocalError而不是NameError：name ‘variable’ is not defined? 

因为变量variable不在全局作用域。Python中的模块代码在执行之前，并不会经过预编译，但是模块内的函数体代码在运行前会经过预编译，因此不管变量名的绑定发生在作用域的那个位置，都能被编译器知道。所以解释器认为variable已经被声明了即“variable = 200” 在test_scopt，但是当引用variable时，解释器会按照正常的顺序依次执行code，并发现variable没有绑定到具体的值，所以导致以上错误发生。Python虽然是一个静态作用域语言，但变量名查找是动态发生的，直到在程序运行时，才会发现作用域方面的问题。

4. 示例4
```python
variable = 300
def test_scopt():
    print variable   #没有在局部作用域找到变量名，会升级到嵌套作用域寻找，并引入一个新的变量到局部作用域(将局部变量variable赋值为300)。
#    variable = 200

test_scopt()
print variable

代码输出为:
300
300
```

跟示例3进行对比，这里把函数中的赋值语句注释了，所以打印时直接找到了全局变量variable并输出。

#### 不同作用域变量的修改
一个non-L的变量相对于L而言，**默认是只读而不能修改的**。如果希望在L中修改定义在non-L的变量，为其绑定一个新的值，Python会认为是在当前的L中引入一个新的变量(即便内外两个变量重名，但却有着不同的意义)。即在当前的L中，如果直接使用non-L中的变量，那么这个变量是只读的，不能被修改，否则会在L中引入一个同名的新变量。这是对上述几个例子的另一种方式的理解。
注意：而且在L中对新变量的修改不会影响到non-L的。当你希望在L中修改non-L中的变量时，可以使用global、nonlocal关键字。

* global关键字
如果我们希望在L中修改G中的变量，使用global关键字。
```python
spam = 99
def tester():
    def nested():
        global spam
        print('current=',spam)
        spam = 200
    return nested
tester()()
print spam

代码的输出为：
('current=', 99)
200
```

上段代码中，定义了一个内部函数，并作为一个变量返回，所以tester()相当于nested，而不是nested()，所以tester()()相当于nested()，关于函数嵌套的知识我们稍后会讲。这里需要注意的是global关键字，使用了这个关键字之后，在nested函数中使用的spam变量就是全局作用域中的spam变量，而不会新生成一个局部作用域中的spam变量。

* nonlocal关键字
在L中修改E中的变量。这是Python3.x增加的新特性，在python2.x中还是无法使用。
```python
def outer():
    count = 10
    def inner():
        nonlocal count
        count = 20
        print(count)
    inner()
    print(count)
outer()

输出为
20
20
```
由于声明了nonlocal，这里inner中使用的count变量就是E即outer函数中生命的count变量，所以输出两个20。

### Python函数嵌套
理解了Python中变量的作用域，那么Python函数嵌套就非常容易理解了，我们这里需要注意的一点是Python中的函数也可以当作变量来对待。
python是允许创建嵌套函数的，也就是说我们可以在函数内部定义一个函数，这些函数都遵循各自的作用域和生命周期规则。

```python
def outer():  
    x = 1  
    def inner():  
        print x # 1  
    inner() # 2  
  
outer()  
```

相信大家都知道输出是什么了，输出是1，了解了Python变量的作用域就很容易正确判断函数嵌套的输出啦，不过我还是想多啰嗦两句：
1. #1的地方，python寻找名为x的local变量，在inner作用域内的locals中寻找不到，python就在外层作用域中寻找，其外层是outer函数。x是定义在outer作用域范围内的local变量。
2. #2的地方，调用了inner函数。这里需要特别注意：inner也只是一个变量名，是遵循python的变量查找规则的（Python先在outer函数的作用域中寻找名为inner的local变量）
4、闭包
闭包的原理我们直接通过下面的例子来解释：
def outer():  
    x = 1  
    def inner():  
        print x # 1  
    return inner  
foo = outer()  
print foo.func_closure #2 doctest: +ELLIPSIS  
  
foo()  

输出为：
(<cell at 0x189da2f0: int object at 0x188b9d08>,)
1

在这个例子中，我们可以看到inner函数作为返回值被outer返回，然后存储在foo变量中，我们可以通过foo()来调用它。但是真的可以跑起来吗？让我们来关注一下作用域规则。
python里运行的东西，都按照作用域规则来运行。

x是outer函数里的local变量
在#1处，inner打印x时，python在inner的locals中寻找x，找不到后再到外层作用域（即outer函数）中寻      找，找到后打印。

看起来一切OK，那么从变量生命周期（lifetime）的角度看，会发生什么呢：

x是outer的local变量，这意味着只有outer运行时，x才存在。那么按照python运行的模式，我们不能在         outer结束后再去调用inner。
在我们调用inner的时候，x应该已经不存在了。应该发生一个运行时错误或者其他错误。
但是这一些都没有发生，inner函数依旧正常执行，打印了x。

Python支持一种特性叫做函数闭包（function closures）：在非全局（global）作用域中定义inner函数（即嵌套函数）时，会记录下它的嵌套函数namespaces（嵌套函数作用域的locals），可以称作：定义时状态，可以通过func_closure 这个属性来获得inner函数的外层嵌套函数的namespaces。(如上例中#2，打印了func_closure ，里面保存了一个int对象，这个int对象就是x)
注意：每次调用outer函数时，inner函数都是新定义的。上面的例子中，x是固定的，所以每次调用inner函数的结果都一样。
如果上面的x不固定呢？我们继续来看下面的例子：
def outer(x):  
    def inner():  
        print x # 1  
    return inner  
print1 = outer(1)  
print2 = outer(2)  
print print1.func_closure  
print1()  
print print2.func_closure  
print2() 

输出为：
(<cell at 0x147d3328: int object at 0x146b2d08>,)
1
(<cell at 0x147d3360: int object at 0x146b2cf0>,)
2

在这个例子中，我们能看到闭包实际上是记录了外层嵌套函数作用域中的local变量。通过这个例子，我们可以创建多个自定义函数。
5、再回首
说了这么多，相信你们都知道文章一开始的错误怎么修正了，同时也知道为什么报的UnboundLocalError错误了。我们只需要生命nonlocal关键词让内部函数使用E作用域中的变量就好啦：
class Solution(object):
    def longestPalindrome(self, s):
        """
        :type s: str
        :rtype: str
        """
        if len(s) < 2:
            return s
        maxlen = 0
        res = ''
        def extendPalidrome(j, k):
            while j >= 0 and k < len(s) and s[j] == s[k]:
                j = j - 1
                k = k + 1
                nonlocal maxlen
                nonlocal res
            if k - j - 1 > maxlen:
                maxlen = k - j - 1
                res = s[j+1:k]
        for i in range(len(s) - 1):
            extendPalidrome(i, i)
            extendPalidrome(i, i + 1)
        return res



s = Solution()
print (s.longestPalindrome('abccbaaeb'))

作者：石晓文的学习日记
链接：https://www.jianshu.com/p/17a9d8584530
來源：简书
简书著作权归作者所有，任何形式的转载都请联系作者获得授权并注明出处。
