---
layout: post
title:  "Golang  Goroutine"
categories: GO
tags:  go
author: Root Wang
---

* content
{:toc}

### 基本概念
在操作系统中，有两个重要的概念：一个是进程、一个是线程。当我们运行一个程序的时候，比如你的IDE或者QQ等，操作系统会为这个程序创建一个进程
进程:包含了运行这个程序所需的各种资源，可以说它是一个容器，是属于这个程序的工作空间，比如它里面有内存空间、文件句柄、设备和线程等等。

#### 线程
线程:是一个执行的空间，比如要下载一个文件，访问一次网络等等。线程会被操作系统调用，来在不同的处理器上运行编写的代码任务，这个处理器不一定是该程序进程所在的处理。操作系统过的调度是操作系统负责的，不同的操作系统可能会不一样，但是对于我们程序编写者来说，不用关心，因为对我们都是透明的。

一个进程在启动的时候，会创建一个主线程，这个主线程结束的时候，程序进程也就终止了，所以一个进程至少有一个线程，这也是我们在main函数里，使用goroutine的时候，要让主线程等待的原因，因为主线程结束了，程序就终止了，那么就有可能会看不到goroutine的输出。



#### goroutine

goroutine : go语言中并发指的是让某个函数独立于其他函数运行的能力，一个goroutine就是一个独立的工作单元. 当一个 Go 程序启动时，一个执行 main function 的 goroutine 会被创建，称之为 main goroutine, Go的runtime（运行时）会在逻辑处理器上调度这些goroutine来运行，一个逻辑处理器绑定一个操作系统线程，所以说goroutine不是线程，它是一个协程，也是这个原因，它是由Go语言运行时本身的算法实现的。

这里我们总结下几个概念：

概念	说明
* 进程	一个程序对应一个独立程序空间
* 线程	一个执行空间，一个进程可以有多个线程
* 逻辑处理器	执行创建的goroutine，绑定一个线程
* 调度器	Go运行时中的，分配goroutine给不同的逻辑处理器
* 全局运行队列	所有刚创建的goroutine都会放到这里
* 本地运行队列	逻辑处理器的goroutine队列

当我们创建一个`goroutine`后，会先存放在`全局运行队列中`，等待Go`运行时的调度器`进行调度，把他们`分配`给其中的一个`逻辑处理器`，并放到这个`逻辑处理器`对应的`本地运行队列`中，最终等着被逻辑处理器执行即可。

这一套管理、调度、执行`goroutine`的方式称之为Go的`并发`。
并发可以同时做很多事情，比如有个goroutine执行了一半，就被暂停执行其他goroutine去了，这是Go控制管理的。
所以并发的概念和并行不一样.
* 并行:指的是在不同的物理处理器上同时执行不同的代码片段，并行可以同时做很多事情.
* 并发:是同时管理很多事情，因为操作系统和硬件的总资源比较少，所以并发的效果要比并行好的多，使用较少的资源做更多的事情，也是Go语言提倡的。

那么问题来了, goroutine什么时候才能得到执行机会呢？

答案：当正在执行的goroutine遇到系统IO（timer，channel read/write，file read/write...)的时候，go scheduler会切换出去看看是不是有别的goroutine可以执行一把，这个时候其他goroutine就有机会了。实际上，这就是golang协程的概念。同时用少数的几个线程来执行大量的goroutine协程，谁正在调用系统IO谁就歇着，让别人用CPU。

#### 实例
Go的并发原理我们刚刚讲了，那么Go的并行是怎样的呢？其实答案非常简单，多创建一个逻辑处理器就好了，这样调度器就可以同时分配全局运行队列中的goroutine到不同的逻辑处理器上并行执行。

```go
func main() {
	var wg sync.WaitGroup
	wg.Add(2)
	go func(){
		defer wg.Done()
		for i:=1;i<100;i++ {
			fmt.Println("A:",i)
		}
	}()
	go func(){
		defer wg.Done()
		for i:=1;i<100;i++ {
			fmt.Println("B:",i)
		}
	}()
	wg.Wait()
}
```
这是一个简单的并发程序。创建一个goroutine是通过go 关键字的，其后跟一个函数或者方法即可。

这里的sync.WaitGroup其实是一个计数的信号量，使用它的目的是要main函数等待两个goroutine执行完成后再结束，不然这两个goroutine还在运行的时候，程序就结束了，看不到想要的结果。

sync.WaitGroup的使用也非常简单，先是使用Add 方法设设置计算器为2，每一个goroutine的函数执行完之后，就调用Done方法减1。Wait方法的意思是如果计数器大于0，就会阻塞，所以main 函数会一直等待2个goroutine完成后，再结束。

我们运行这个程序，会发现A和B前缀会交叉出现，并且每次运行的结果可能不一样，这就是Go调度器调度的结果。

默认情况下，Go默认是给每个可用的物理处理器都分配一个逻辑处理器，因为我的电脑是4核的，所以上面的例子默认创建了4个逻辑处理器，所以这个例子中同时也有并行的调度，如果我们强制只使用一个逻辑处理器，我们再看看结果。

```go
func main() {
	runtime.GOMAXPROCS(1)
	var wg sync.WaitGroup
	wg.Add(2)
	go func(){
		defer wg.Done()
		for i:=1;i<100;i++ {
			fmt.Println("A:",i)
		}
	}()
	go func(){
		defer wg.Done()
		for i:=1;i<100;i++ {
			fmt.Println("B:",i)
		}
	}()
	wg.Wait()
}
```

#### goroutine的嵌套
goroutinue 协程嵌套，会产生依赖关系(父子关系)么？
上货
```go
package main
 
import (
    "fmt"
    "time"
)
 
func main() {
    go func() {
        fmt.Println("father alive")
 
        go func() {
            time.Sleep(time.Second * 2)
            fmt.Println("child alive")
        }()
        defer fmt.Println("father dead")
        return
    }()
    time.Sleep(time.Second * 3)
    fmt.Println("main alive")

}
----------------Result--------------------
father alive
father dead
child alive
main alive
```
> 不同于linux里的进程依赖，golang里，协程都是互相独立的，没有依赖（父子）关系。main函数本身也运行在一个goroutine中，main是所有协程的被依赖者，这里是个特例。

#### Q&A

```go

ch := chan int
ch-<1

----------Result----------
fatal error: all goroutines are asleep – deadlock!
```
> 原因为：当channel为非缓冲类型channel时候，ch<-num和<-ch都会保持等待状态。main goroutine线中，期待从其他goroutine线读取数据，但是其他goroutine线都已经执行完了或者没有其他goroutine(all goroutines are asleep)，那么就永远不会从管道中取出数据。所以，main goroutine线在等一个永远不会被取出的数据，那整个程序就永远等下去了。


```go
ch := make(chan int, 10)
ch <- 10
ch <- 10
for value := range ch {
	fmt.Println("value is ", value)
}
----------Result----------
fatal error: all goroutines are asleep – deadlock!

```
> 原因为：尽管使用了缓冲channel，但是range ch 将会持续的读取channel数据指导ch被关闭，当range ch读取完2个数据后，没有其他的goroutine会放入新的数据到channel，并且ch也没有被close，这将导致整个程序会永远等待下去。



