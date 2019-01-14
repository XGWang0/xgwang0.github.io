---
layout: post
title:  "The difference amount RUN CMD and ENTERPOINT"
categories: DOCKER
tags:  
author: Root Wang
---

* content
{:toc}

### 简介
RUN、CMD 和 ENTRYPOINT 这三个 Dockerfile 指令看上去很类似，很容易混淆。

简单的说：

* RUN 执行命令并创建新的镜像层，RUN 经常用于安装软件包。
* CMD 设置容器启动后默认执行的命令及其参数，但 CMD 能够被 docker run 后面跟的命令行参数替换。
* ENTRYPOINT 配置容器启动时运行的命令。


### Shell 和 Exec 格式

我们可用两种方式指定 RUN、CMD 和 ENTRYPOINT 要运行的命令：Shell 格式和 Exec 格式，二者在使用上有细微的区别。

#### Shell 格式

<instruction> <command>

例如：
```sh
RUN apt-get install python3  

CMD echo "Hello world"  

ENTRYPOINT echo "Hello world" 
```

*当指令执行时，shell 格式底层会调用 /bin/sh -c <command> 。*

例如下面的 Dockerfile 片段：

```sh
ENV name Cloud Man  

ENTRYPOINT echo "Hello, $name" 
```

执行 docker run <image> 将输出：
```sh
Hello, Cloud Man
```

注意环境变量 name 已经被值 Cloud Man 替换。

下面来看 Exec 格式。

#### Exec 格式

<instruction> ["executable", "param1", "param2", ...]

 
例如：
```sh
RUN ["apt-get", "install", "python3"]  

CMD ["/bin/echo", "Hello world"]  

ENTRYPOINT ["/bin/echo", "Hello world"]
```
 

当指令执行时，会直接调用 <command>，不会被 shell 解析。
例如下面的 Dockerfile 片段：
```sh
ENV name Cloud Man  

ENTRYPOINT ["/bin/echo", "Hello, $name"]
```

运行容器将输出：
```sh
Hello, $name
```
 
*注意环境变量“name”没有被替换。*
如果希望使用环境变量，照如下修改

```sh
ENV name Cloud Man  

ENTRYPOINT ["/bin/sh", "-c", "echo Hello, $name"]
```

运行容器将输出：
```sh
Hello, Cloud Man
```
 
***CMD 和 ENTRYPOINT 推荐使用 Exec 格式，因为指令可读性更强，更容易理解。RUN 则两种格式都可以。***

### RUN

*RUN 指令通常用于安装应用和软件包。*

*RUN 在当前镜像的顶部执行命令，并通过`创建新的镜像层`。Dockerfile 中常常包含多个 RUN 指令。*

RUN 有两种格式：

* Shell 格式：RUN
* Exec 格式：RUN ["executable", "param1", "param2"]

下面是使用 RUN 安装多个包的例子：
```sh
RUN apt-get update && apt-get install -y \  
 bzr \
 cvs \
 git \
 mercurial \
 subversion
``` 

注意：apt-get update 和 apt-get install 被放在一个 RUN 指令中执行，这样能够保证每次安装的是最新的包。如果*apt-get install 在单独的 RUN 中执行，则会使用 apt-get update 创建的镜像层，而这一层可能是很久以前缓存的*

### CMD

cmd给出的是一个容器的`默认的可执行体`。也就是容器启动以后，默认的执行的命令。重点就是这个“默认”。意味着，如果docker run`没有指定任何的执行命令`或者`dockerfile里面也没有entrypoint`，那么，就会使用cmd指定的默认的执行命令执行。同时也*从侧面说明了entrypoint的含义，它才是真正的容器启动以后要执行命令。*

所以这句话就给出了cmd命令的一个角色定位，它主要作用是默认的容器启动执行命令。（注意不是“全部”作用）

这也是为什么大多数网上博客论坛说的“cmd会被覆盖”，其实为什么会覆盖？因为cmd的角色定位就是默认，如果你不额外指定，那么就执行cmd的命令，否则呢？只要你指定了，那么就不会执行cmd，也就是cmd会被覆盖。

总结如下：
*CMD 指令允许用户指定容器的默认执行的命令。*
*此命令会在容器启动且 docker run 没有指定其他命令时运行。*
*如果 docker run 指定了其他命令，CMD 指定的默认命令将被忽略。*

***如果 Dockerfile 中有多个 CMD 指令，只有最后一个 CMD 有效。***

CMD 有三种格式：

* Exec 格式：CMD ["executable","param1","param2"]
这是 CMD 的推荐格式。

* CMD ["param1","param2"] 为 ENTRYPOINT 提供额外的参数，此时 ENTRYPOINT 必须使用 Exec 格式。
* Shell 格式：CMD command param1 param2

Exec 和 Shell 格式前面已经介绍过了。
第二种格式 CMD ["param1","param2"] 要与 Exec 格式 的 ENTRYPOINT 指令配合使用，其用途是为 ENTRYPOINT 设置默认的参数。在后面讨论 ENTRYPOINT 时举例说明。


#### CMD 工作流程
下面看看 CMD 是如何工作的。Dockerfile 片段如下：
```sh
CMD echo "Hello world"
```

运行容器 docker run -it [image] 将输出：
```sh
Hello world
```
 
但当后面加上一个命令，比如 docker run -it [image] /bin/bash，*CMD 会被忽略掉*，命令 bash 将被执行：

root@10a32dc7d3d3:/#

 

### ENTRYPOINT

> An ENTRYPOINT allows you to configure a container that will run as an executable.
也就是说entrypoint才是正统地用于定义容器启动以后的执行体的，其实我们从名字也可以理解，这个是容器的“入口”。

ENTRYPOINT 指令可让容器以应用程序或者服务的形式运行。

ENTRYPOINT 看上去与 CMD 很像，它们都可以指定要执行的命令及其参数。不同的地方在于 *ENTRYPOINT 不会被忽略，一定会被执行，即使运行 docker run 时指定了其他命令。*

ENTRYPOINT 有两种格式：

* Exec 格式：ENTRYPOINT ["executable", "param1", "param2"] 这是 ENTRYPOINT 的推荐格式。
* Shell 格式：ENTRYPOINT command param1 param2
	在这种模式下，任何run和cmd的参数都无法被传入到entrypoint里。官网推荐第一种用法。


在为 ENTRYPOINT 选择格式时必须小心，因为这两种格式的效果差别很大。

#### Exec 格式
ENTRYPOINT 的 Exec 格式用于设置要执行的命令及其参数，同时可通过 CMD 提供额外的参数。

如果docker run命令后面有东西，那么后面的全部都会作为entrypoint的参数。如果run后面没有额外的东西，但是cmd有，那么cmd的全部内容会作为entrypoint的参数，这同时是cmd的第二种用法。这也是网上说的entrypoint不会被覆盖。当然如果要在run里面覆盖，也是有办法的，使用--entrypoint即可。

ENTRYPOINT 中的参数始终会被使用，而 CMD 的额外参数可以在容器启动时动态替换掉。

比如下面的 Dockerfile 片段：

```sh
ENTRYPOINT ["/bin/echo", "Hello"]  

CMD ["world"]
```
当容器通过 docker run -it [image] 启动时，输出为：

```sh
Hello world
```

而如果通过 docker run -it [image] CloudMan 启动，则输出为：
```sh
Hello CloudMan
```

#### Shell 格式

ENTRYPOINT 的 Shell 格式会忽略任何 CMD 或 docker run 提供的参数。

***在这种模式下，任何run和cmd的参数都无法被传入到entrypoint里。官网推荐第一种用法。***

总结下一般该怎么使用：一般还是会用entrypoint的中括号形式作为docker 容器启动以后的默认执行命令，里面放的是不变的部分，可变部分比如命令参数可以使用cmd的形式提供默认版本，也就是run里面没有任何参数时使用的默认参数。如果我们想用默认参数，就直接run，否则想用其他参数，就run 里面加参数。

