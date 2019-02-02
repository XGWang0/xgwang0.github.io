---
layout: post
title:  "Golang Panic And Recover"
categories: GO
tags:  go
author: Root Wang
---

* content
{:toc}

### 简介

func panic(interface{})和func recover() interface{}是Golang中用于错误处理的两个函数。
panic的作用就是抛出一条错误信息，从它的参数类型可以看到它可以抛出任意类型的错误信息。在函数执行过程中的某处调用了panic，则立即抛出一个错误信息，同时函数的正常执行流程终止，但是该函数中panic之前定义的defer语句将被依次执行。之后该goroutine立即停止执行。

recover()用于将panic的信息捕捉。recover必须定义在panic之前的defer语句中。在这种情况下，当panic被触发时，该goroutine不会简单的终止，而是会执行在它之前定义的defer语句。

#### Sample
1. panic
```go
func sample(a int) int {
	defer func() {
		fmt.Println("defer in smaple before panic")
	}()

	if a == 1 {
		panic(404)
		defer func() {
			fmt.Println("defer in smaple after panic")
		}()
		return 10
	} else {
		return 100
	}

}

func main() {
	sample(1)

	fmt.Println("Goroutine continue")
}

result:
-----------------------------
defer in smaple before panic

panic: 404

goroutine 1 [running]:
main.sample(0x1, 0x0)
	/root/golang/test.go:22 +0x96
main.main()
	/root/golang/test.go:38 +0x2a
exit status 2

exit status 1

```
> Panic 抛出错误异常, defer（panic之前声明的） 仍然会执行， defer（panic之后声明的）将被舍弃

2. recover

```go
func sample(a int) int {
	defer func() {
		if r := recover(); r != nil {
			fmt.Println("Catch panic in sample", r)
		}
		fmt.Println("defer in smaple before panic")
	}()

	if a == 1 {
		panic(404)
		defer func() {
			fmt.Println("defer in smaple after panic")
		}()
		return 10
	} else {
		return 100
	}

}

func main() {
	sample(1)
	fmt.Println("Goroutine continue")

result:
--------------------------------
Catch panic in sample 404
defer in smaple before panic
Goroutine continue

```
> recover 相当于python中的catch函数, 用来捕获panic抛出的错误信息。 捕获之后，终止panic和recover所在函数，不影响调用者继续执行。

> panic抛出的错误可以透传到调用者， 参考下例

```go
func sample(a int) int {
	defer func() {
		fmt.Println("defer in smaple before panic")
	}()

	if a == 1 {
		panic(404)
		defer func() {
			fmt.Println("defer in smaple after panic")
		}()
		return 10
	} else {
		return 100
	}

}

func main() {

	defer func() {
		if r := recover(); r != nil {
			fmt.Println("Catch panic in main before sample", r)
		}
		fmt.Println("defer in main before sample")
	}()
	sample(1)

	defer func() {
		if r := recover(); r != nil {
			fmt.Println("Catch panic in main after sample", r)
		}
		fmt.Println("defer in main AFTER sample function")
	}()

	fmt.Println("Goroutine continue")
}

result:
----------------------------------
defer in smaple before panic
Catch panic in main before sample 404
defer in main before sample

```
