---
layout: post
title:  "Golang Import and Compile Process"
categories: GO
tags:  go
author: Root Wang
---

* content
{:toc}

### 包的使用
Golang使用包（package）这种语法元素来组织源码，所有语法可见性均定义在package这个级别，与Java 、python等语言相比，这算不上什么创新，但与C传统的include相比，则是显得“先进”了许多。

Golang中包的定义和使用看起来十分简单：

通过package关键字定义包：
```c
   package xxx
```
使用import关键字，导入要使用的标准库包或第三方依赖包。
```c
   import "a/b/c"
   import "fmt"

   c.Func1()
   fmt.Println("Hello, World")
 ```

很多Golang初学者看到上面代码，都会想当然的将import后面的"c"、"fmt"当成包名，将其与c.Func1()和 fmt.Println()中的c和fmt认作为同一个语法元素：包名。但在深入Golang后，很多人便会发现事实上并非如此。比如在使用实时分布式消 息平台nsq提供的go client api时：

我们导入的路径如下：
```
   import “github.com/bitly/go-nsq”
```
但在使用其提供的export functions时，却用nsq做前缀包名：
```
   q, _ := nsq.NewConsumer("write_test", "ch", config)
```
人们不禁要问：import后面路径中的最后一个元素到底代表的是啥? 是包名还是仅仅是一个路径？我们一起通过试验来理解一下。  实验环境：darwin_amd64 , go 1.4。

初始试验环境目录结果如下：
```sh
GOPATH = /Users/tony/Test/Go/pkgtest/
pkgtest/
    pkg/
    src/
       libproj1/
           foo/
              foo1.go
       app1/
           main.go
```

### 编译时使用的是包源码还是.a

我们知道一个非main包在编译后会生成一个.a文件（在临时目录下生成，除非使用go install安装到$GOROOT或$GOPATH下，否则你看不到.a），用于后续可执行程序链接使用。

比如Go标准库中的包对应的源码部分路径在：$GOROOT/src，而标准库中包编译后的.a文件路径在$GOROOT/pkg/darwin_amd64下。一个奇怪的问题在我脑袋中升腾起来，编译时，编译器到底用的是.a还是源码？

我们先以用户自定义的package为例做个小实验。
```sh
$GOPATH/src/
    libproj1/foo/
            – foo1.go
    app1
            – main.go
```

```c
//foo1.go
package foo

import "fmt"

func Foo1() {
    fmt.Println("Foo1")
}
```

```c
// main.go
package main

import (
    "libproj1/foo"
)

func main() {
    foo.Foo1()
}
```
> 执行go install libproj1/foo，*Go编译器编译foo包，并将foo.a安装到$GOPATH/pkg/darwin_amd64/libproj1下。*
> 编译app1：go build app1，*在app1目录下生成app1*可执行文件，执行app1，我们得到一个初始预期结果：*
```sh
$./app1
Foo1
``

现在我们无法看出使用的到底是foo的源码还是foo.a，因为目前它们的输出都是一致的。我们修改一下foo1.go的代码：

```c
//foo1.go
package foo

import "fmt"

func Foo1() {
    fmt.Println("Foo1 – modified")
}
```
重新编译执行app1，我们得到结果如下：
```sh
$./app1
Foo1 – modified
```
实际测试结果告诉我们：
1. 在使用第三方包的时候，`当源码和.a均已安装的情况下，编译器链接的是源码。`

那么是否可以只链接.a，不用第三方包源码呢？
我们临时删除掉libproj1目录，但保留之前install的libproj1/foo.a文件。

我们再次尝试编译app1，得到如下错误：
```sh
$go build app1
main.go:5:2: cannot find package "libproj1/foo" in any of:
    /Users/tony/.Bin/go14/src/libproj1/foo (from $GOROOT)
    /Users/tony/Test/Go/pkgtest/src/libproj1/foo (from $GOPATH)
```

`编译器还是去找源码，而不是.a`，因此我们要依赖第三方包，就必须搞到第三方包的源码，这也是Golang包管理的一个特点。

其实通过编译器的详细输出我们也可得出上面结论。我们在编译app1时给编译器传入`-x -v`选项：
```sh
$go build -x -v app1
WORK=/var/folders/2h/xr2tmnxx6qxc4w4w13m01fsh0000gn/T/go-build797811168
libproj1/foo
mkdir -p $WORK/libproj1/foo/_obj/
mkdir -p $WORK/libproj1/
cd /Users/tony/Test/Go/pkgtest/src/libproj1/foo
/Users/tony/.Bin/go14/pkg/tool/darwin_amd64/6g -o $WORK/libproj1/foo.a -trimpath $WORK -p libproj1/foo -complete -D _/Users/tony/Test/Go/pkgtest/src/libproj1/foo -I $WORK -pack ./foo1.go ./foo2.go
app1
mkdir -p $WORK/app1/_obj/
mkdir -p $WORK/app1/_obj/exe/
cd /Users/tony/Test/Go/pkgtest/src/app1
/Users/tony/.Bin/go14/pkg/tool/darwin_amd64/6g -o $WORK/app1.a -trimpath $WORK -p app1 -complete -D _/Users/tony/Test/Go/pkgtest/src/app1 -I $WORK -I /Users/tony/Test/Go/pkgtest/pkg/darwin_amd64 -pack ./main.go
cd .
/Users/tony/.Bin/go14/pkg/tool/darwin_amd64/6l -o $WORK/app1/_obj/exe/a.out -L $WORK -L /Users/tony/Test/Go/pkgtest/pkg/darwin_amd64 -extld=clang $WORK/app1.a
mv $WORK/app1/_obj/exe/a.out app1
```

可以看到编译器6g首先在临时路径下编译出依赖包foo.a，放在$WORK/libproj1下。但我们在最后6l链接器的执行语句中并未显式看到app1链接的是$WORK/libproj1下的foo.a。`但是从6l链接器的-L参数来看：-L $WORK -L /Users/tony/Test/Go/pkgtest/pkg/darwin_amd64，我们发现$WORK目录放在了前面，我们猜测6l首先搜索到的时$WORK下面的libproj1/foo.a。`

为了验证我们的推论，我们按照编译器输出，按顺序手动执行了一遍如上命令，但在最后执行6l命令时，去掉了-L $WORK：
```sh
/Users/tony/.Bin/go14/pkg/tool/darwin_amd64/6l -o $WORK/app1/_obj/exe/a.out -L /Users/tony/Test/Go/pkgtest/pkg/darwin_amd64 -extld=clang $WORK/app1.a
```
这样做的结果是：
```sh
$./app1
Foo1
```
编译器链接了$GOPATH/pkg下的foo.a。

2. 到这里我们明白了所谓的使用第三方包源码，实际上是链接了以该最新源码编译的临时目录下的.a文件而已。

Go标准库中的包也是这样么？
对于标准库，比如fmt而言，编译时，到底使用的时$GOROOT/src下源码还是$GOROOT/pkg下已经编译好的.a呢？

我们不妨也来试试，一个最简单的hello world例子：
```c
//main.go
import "fmt"

func main() {
    fmt.Println("Hello, World")
}
```
我们先将$GOROOT/src/fmt目录rename 为fmtbak，看看go compiler有何反应？
```sh
$go build -x -v ./
WORK=/var/folders/2h/xr2tmnxx6qxc4w4w13m01fsh0000gn/T/go-build957202426
main.go:4:8: cannot find package "fmt" in any of:
    /Users/tony/.Bin/go14/src/fmt (from $GOROOT)
    /Users/tony/Test/Go/pkgtest/src/fmt (from $GOPATH)
``` 
找不到fmt包了。`显然标准库在编译时也是必须要源码的`。`不过与自定义包不同的是，即便你修改了fmt包的源码（未重新编译GO安装包），用户源码编译时，也不会尝试重新编译fmt包的，依旧只是在链接时链接已经编译好的fmt.a`。通过下面的gc输出可以验证这点：

```sh
$go build -x -v ./
WORK=/var/folders/2h/xr2tmnxx6qxc4w4w13m01fsh0000gn/T/go-build773440756
app1
mkdir -p $WORK/app1/_obj/
mkdir -p $WORK/app1/_obj/exe/
cd /Users/tony/Test/Go/pkgtest/src/app1
/Users/tony/.Bin/go14/pkg/tool/darwin_amd64/6g -o $WORK/app1.a -trimpath $WORK -p app1 -complete -D _/Users/tony/Test/Go/pkgtest/src/app1 -I $WORK -pack ./main.go
cd .
/Users/tony/.Bin/go14/pkg/tool/darwin_amd64/6l -o $WORK/app1/_obj/exe/a.out -L $WORK -extld=clang $WORK/app1.a
mv $WORK/app1/_obj/exe/a.out app1
```

可以看出，编译器的确并未尝试编译标准库中的fmt源码。

### 目录名还是包名？

从第一节的实验中，我们得知了编译器在编译过程中依赖的是包源码的路径，这为后续的实验打下了基础。下面我们再来看看，Go语言中import后面路径中最后的一个元素到底是包名还是路径名？

本次实验目录结构：
```sh
$GOPATH
    src/
       libproj2/
             foo/
               foo1.go
       app2/
             main.go
```
按照Golang语言习惯，一个`go package的所有源文件放在同一个目录下，且该目录名与该包名相同`，比如libproj1/foo目录下的package为foo，foo1.go、 foo2.go…共同组成foo package的源文件。`但目录名与包名也可以不同，我们就来试试不同的`。

我们建立libproj2/foo目录，其中的foo1.go代码如下：

```c
//foo1.go
package bar

import "fmt"

func Bar1() {
    fmt.Println("Bar1")
}
```

> 注意：这里`package名为bar`，与`目录名foo`完全不同。

*接下来就给app2带来了难题：该如何import bar包呢？*

我们假设import路径中的最后一个元素是包名，而非路径名。
```c
//app2/main.go

package main

import (
    "libproj2/bar"
)

func main() {
    bar.Bar1()
}
```
编译app2：
```sh
$go build -x -v app2
WORK=/var/folders/2h/xr2tmnxx6qxc4w4w13m01fsh0000gn/T/go-build736904327
main.go:5:2: cannot find package "libproj2/bar" in any of:
    /Users/tony/.Bin/go14/src/libproj2/bar (from $GOROOT)
    /Users/tony/Test/Go/pkgtest/src/libproj2/bar (from $GOPATH)
```
编译失败，在两个路径下无法找到对应libproj2/bar包。

我们的假设错了，我们把它改为路径：
```c
//app2/main.go

package main

import (
    "libproj2/foo"
)

func main() {
    bar.Bar1()
}
```
再编译执行：

```sh
$go build app2
$app2
Bar1
```

这回编译顺利通过，执行结果也是OK的。这样我们得到了结论：
3. *import后面的最后一个元素应该是路径，就是目录，并非包名。*

go编译器在这些`路径(libproj2/foo)下找bar包`。这样看来，go语言的惯例只是一个特例，即恰好目录名与包名一致罢了。也就是说下面例子中的两个foo含义不同：

```c
import "libproj1/foo"

func main() {
    foo.Foo()
}
```
`import中的foo`只是一个`文件系统的路径`罢了。而下面`foo.Foo()中的foo则是包名`。而这个包是在libproj1/foo目录下的源码中找到的。

再类比一下标准库包fmt。

```c
import "fmt"
fmt.Println("xxx")
```

这里上下两行中虽然都是“fmt"，但同样含义不同，一个是路径 ，对于标准库来说，是$GOROOT/src/fmt这个路径。而第二行中的fmt则是包名。gc会在$GOROOT/src/fmt路径下找到fmt包的源文件。

### import m "lib/math"

Go language specification中关于import package时列举的一个例子如下：
```c
Import declaration          Local name of Sin

import   "lib/math"         math.Sin
import m "lib/math"         m.Sin
import . "lib/math"         Sin
```

我们看到import m "lib/math"  m.Sin一行。我们说过lib/math是路径，import语句用m替代lib/math，并在代码中通过m访问math包中的导出函数Sin。

那m到底是包名还是路径呢？既然能通过m访问Sin，那m肯定是包名了，Right！那import m "lib/math"该如何理解呢？ 

根据上面两节中得出的结论，我们尝试理解一下m：

4. *m指代的是lib/math路径下唯一的那个包。*

一个目录下是否可以存在两个包呢？我们来试试。


*我们在libproj1/foo下新增一个go源文件，bar1.go：*

```c
package bar

import "fmt"

func Bar1() {
    fmt.Println("Bar1")
}
```
我们重新构建一下这个目录下的包：

```sh
$go build libproj1/foo
can't load package: package libproj1/foo: found packages bar1.go (bar) and foo1.go (foo) in /Users/tony/Test/Go/pkgtest/src/libproj1/foo
```

> 我们收到了错误提示，编译器在这个路径下发现了两个包，这是不允许的。

我们再作个实验，来验证我们对m含义的解释。

我们建立app3目录，其main.go的源码如下：

```c
//main.go
package main

import m "libproj2/foo"

func main() {
    m.Bar1()
}
```
libproj2/foo路径下的包的包名为bar，按照我们的推论，m指代的就是bar这个包，通过m我们可以访问bar的Bar1导出函数。

编译并执行上面main.go：
```sh
$go build app3
$app3
Bar1
```
执行结果与我们推论完全一致。

附录：6g, 6l文档位置：

> 6g – $GOROOT/src/cmd/gc/doc.go
> 6l – $GOROOT/src/cmd/ld/doc.go
