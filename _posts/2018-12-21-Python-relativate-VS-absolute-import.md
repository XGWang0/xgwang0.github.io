---
layout: post
title:  "Relative VS Absolute import"
categories: python
tags:  closure decorators
author: Root Wang
---

* content
{:toc}

### 前言：
Python 相对导入与绝对导入，这两个概念是***相对于包内导入而言***的。包内导入即是包内的模块导入包内部的模块。

### Python import 的搜索路径
* 在当前目录下搜索该模块
* 在环境变量 PYTHONPATH 中指定的路径列表中依次搜索
* 在 Python 安装路径的 lib 库中搜索

### Python import 的步骤
python 所有加载的模块信息都存放在 `sys.modules` 结构中，当 import 一个模块时，会按如下步骤来进行

* 如果是 import A，检查 sys.modules 中是否已经有 A，如果有则不加载，如果没有则为 A 创建 module 对象，并加载 A
* 如果是 from A import B，先为 A 创建 module 对象，再解析A，从中寻找B并填充到 A 的 __dict__ 中

### 相对导入与绝对导入
绝对导入的格式为 import A.B 或 from A import B，相对导入格式为 from . import B 或 from ..A import B，.代表当前模块，..代表上层模块，...代表上上层模块，依次类推。

_相对导入可以避免硬编码带来的维护问题，例如我们改了某一顶层包的名，那么其子包所有的导入就都不能用了。但是 存在相对导入语句的模块，不能直接运行，否则会有异常：_

```sh
ValueError: Attempted relative import in non-package
```

这是什么原因呢？我们需要先来了解下导入模块时的一些规则：

在没有明确指定包结构的情况下，Python 是根据 __name__ 来决定一个模块在包中的结构的，如果是 __main__ 则它本身是顶层模块，没有包结构，如果是A.B.C 结构，那么顶层模块是 A。基本上遵循这样的原则：

* 如果是绝对导入，一个模块只能导入自身的子模块或和它的顶层模块同级别的模块及其子模块
* 如果是相对导入，一个模块必须有包结构且只能导入它的顶层模块内部的模块
* 如果一个模块被直接运行，则它自己为顶层模块，不存在层次结构，所以找不到其他的相对路径。

***Python2.x 缺省为相对路径导入，Python3.x 缺省为绝对路径导入。***
_绝对导入可以避免导入子包覆盖掉标准库模块（由于名字相同，发生冲突）。_ 如果在 Python2.x 中要默认使用绝对导入，可以在文件开头加入如下语句：

```python
from __future__ import absolute_import
from __future__ import absolute_import
```
这句 import 并不是指将所有的导入视为绝对导入，而是指禁用 implicit relative import（隐式相对导入）, 但并不会禁掉 explicit relative import（显示相对导入）。

那么到底什么是隐式相对导入，什么又是显示的相对导入呢？我们来看一个例子，假设有如下包结构：

```sh
thing
├── books
│   ├── adventure.py
│   ├── history.py
│   ├── horror.py
│   ├── __init__.py
│   └── lovestory.py
├── furniture
│   ├── armchair.py
│   ├── bench.py
│   ├── __init__.py
│   ├── screen.py
│   └── stool.py
└── __init__.py

```

那么如果在 stool 中引用 bench，则有如下几种方式:
```python
import bench                 # 此为 implicit relative import
from . import bench          # 此为 explicit relative import
from furniture import bench  # 此为 absolute import
```

_隐式相对就是没有告诉解释器相对于谁，但默认相对与当前模块_
_而显示相对则明确告诉解释器相对于谁来导入_
以上导入方式的第三种，才是官方推荐的，**第一种是官方强烈不推荐的，Python3 中已经被废弃，这种方式只能用于导入 path 中的模块**。

***相对与绝对仅针对包内导入而言***
最后再次强调，相对导入与绝对导入仅针对于包内导入而言，要不然本文所讨论的内容就没有意义。所谓的包，就是包含 __init__.py 文件的目录，该文件在包导入时会被首先执行，该文件可以为空，也可以在其中加入任意合法的 Python 代码。

相对导入可以避免硬编码，对于包的维护是友好的。绝对导入可以避免与标准库命名的冲突，实际上也不推荐自定义模块与标准库命令相同。

前面提到含有相对导入的模块不能被直接运行，实际上含有绝对导入的模块也不能被直接运行，会出现 ImportError：

ImportError: No module named XXX
这与绝对导入时是一样的原因。要运行包中包含绝对导入和相对导入的模块，可以用 python -m A.B.C 告诉解释器模块的层次结构。

有人可能会问：假如有两个模块 a.py 和 b.py 放在同一个目录下，为什么能在 b.py 中 import a 呢？

这是因为这两个文件所在的目录不是一个包，那么每一个 python 文件都是一个独立的、可以直接被其他模块导入的模块，就像你导入标准库一样，它们不存在相对导入和绝对导入的问题。相对导入与绝对导入仅用于包内部。


#### 相对导入
PEP 328介绍了引入相对导入的原因，以及选择了哪种语法。具体来说，是使用句点来决定如何相对导入其他包或模块。这么做的原因是为了避免偶然情况下导入标准库中的模块产生冲突。这里我们以PEP 328中给出的文件夹结构为例，看看相对导入是如何工作的：

```sh
my_package/
    __init__.py
    subpackage1/
        __init__.py
        module_x.py
        module_y.py
    subpackage2/
        __init__.py
        module_z.py
    module_a.py
```
在本地磁盘上找个地方创建上述文件和文件夹。在顶层的__init__.py文件中，输入以下代码：
```python
from . import subpackage1
from . import subpackage2
```

接下来进入subpackage1文件夹，编辑其中的__init__.py文件，输入以下代码：

```python
from . import module_x
from . import module_y
```
现在编辑module_x.py文件，输入以下代码：

```python
from .module_y import spam as ham

def main():
    ham()
```
最后编辑module_y.py文件，输入以下代码：

```python
def spam():
    print('spam ' * 3)
```
打开终端，cd至my_package包所在的文件夹，但不要进入my_package。在这个文件夹下运行Python解释器。我使用的是IPython，因为它的自动补全功能非常方便：
```python
In [1]: import my_package

In [2]: my_package.subpackage1.module_x
Out[2]: <module 'my_package.subpackage1.module_x' from 'my_package/subpackage1/module_x.py'>

In [3]: my_package.subpackage1.module_x.main()
spam spam spam
```
***相对导入适用于你最终要放入包中的代码***。如果你编写了很多相关性强的代码，那么应该采用这种导入方式。你会发现PyPI上有很多流行的包也是采用了相对导入。还要注意一点，如果你想要跨越多个文件层级进行导入，只需要使用多个句点即可。不过，PEP 328建议相对导入的层级不要超过两层。

_还要注意一点，如果你往module_x.py文件中添加了if __name__ == ‘__main__’，然后试图运行这个文件，你会碰到一个很难理解的错误。编辑一下文件，试试看吧！_

```python
from . module_y import spam as ham

def main():
    ham()

if __name__ == '__main__':
    # This won't work!
    main()
```
现在从终端进入subpackage1文件夹，执行以下命令：

```sh
python module_x.py
```
如果你使用的是Python 2，你应该会看到下面的错误信息：

```sh
Traceback (most recent call last):
  File "module_x.py", line 1, in <module>
    from . module_y import spam as ham
ValueError: Attempted relative import in non-package
```
如果你使用的是Python 3，错误信息大概是这样的：

```sh
Traceback (most recent call last):
  File "module_x.py", line 1, in <module>
    from . module_y import spam as ham
SystemError: Parent module '' not loaded, cannot perform relative import
```
这指的是，module_x.py是某个包中的一个模块，而你试图以脚本模式执行，但是这种模式不支持相对导入。

如果你想在自己的代码中使用这个模块，那么你必须将其添加至Python的导入检索路径（import search path）。最简单的做法如下：

```python
import sys
sys.path.append('/path/to/folder/containing/my_package')
import my_package
```
注意，你需要添加的是my_package的上一层文件夹路径，而不是my_package本身。原因是my_package就是我们想要使用的包，所以如果你添加它的路径，那么将无法使用这个包。


#### 循环导入
如果你创建两个模块，二者相互导入对方，那么就会出现循环导入。例如：
```python
# a.py
import b

def a_test():
    print("in a_test")
    b.b_test()

a_test()
```
然后在同个文件夹中创建另一个模块，将其命名为b.py。

```python
import a

def b_test():
    print('In test_b"')
    a.a_test()

b_test()
```
如果你运行任意一个模块，都会引发AttributeError。这是因为这两个模块都在试图导入对方。简单来说，模块a想要导入模块b，但是因为模块b也在试图导入模块a（这时正在执行），模块a将无法完成模块b的导入。我看过一些解决这个问题的破解方法（hack），但是一般来说，你应该做的是重构代码，避免发生这种情况。
