---
layout: post
title:  "Some Ways To Execute Shell In Python"
categories: PYTHON
tags:  c-extension
author: Root Wang
---

* content
{:toc}

#### os.system(command)

在一个子shell中运行command命令，并返回command命令执行完毕后的退出状态。这实际上是使用C标准库函数system()实现的。这个函数在执行command命令时需要重新打开一个终端，并且无法保存command命令的执行结果。

#### os.popen(command,mode)
打开一个与command进程之间的管道。这个函数的返回值是一个`文件对象`，可以读或者写(由mode决定，mode默认是'r')。如果mode为'r'，可以使用此函数的返回值调用read()来获取command命令的执行结果。

#### commands.getstatusoutput(command)
使用os. getstatusoutput ()函数执行command命令并返回一个元组(status,output)，分别表示command命令执行的`返回状态`和`执行结果`。对command的执行实际上是按照`{command;} 2>&1`的方式，所以output中包含控制台`输出信息`和`错误信息`。output中不包含尾部的换行符。

#### subprocess module
##### subprocess.call(command,shell=True)
执行指定的命令，返回命令执行状态，其功能类似于os.system(cmd)。

##### subprocess.Popen(command, shell=True)
如果`command不是一个可执行文件`，`shell=True`不可省。

使用subprocess模块可以创建新的进程，可以与新建进程的输入/输出/错误管道连通，并可以获得新建进程执行的返回状态。使用subprocess模块的目的是替代os.system()、os.popen*()、commands.*等旧的函数或模块。

最简单的方法是使用class subprocess.Popen(command,shell=True)。Popen类有Popen.stdin，Popen.stdout，Popen.stderr三个有用的属性，可以实现与子进程的通信。

将调用shell的结果赋值给python变量

##### subprocess.run()
Python 3.5中新增的函数。执行指定的命令，等待命令执行完成后返回一个包含执行结果的CompletedProcess类的实例。

##### subprocess.check_call()
Python 2.5中新增的函数。 执行指定的命令，如果执行成功则返回状态码，否则抛出异常。其功能等价于subprocess.run(..., check=True)。

##### subprocess.check_output()
Python 2.7中新增的的函数。执行指定的命令，如果执行状态码为0则返回命令执行结果，否则抛出异常。

##### subprocess.getoutput(cmd)
接收字符串格式的命令，执行命令并返回执行结果，其功能类似于os.popen(cmd).read()和commands.getoutput(cmd)。

##### subprocess.getstatusoutput(cmd)
执行cmd命令，返回一个元组(命令执行状态, 命令执行结果输出)，其功能类似于commands.getstatusoutput()。
