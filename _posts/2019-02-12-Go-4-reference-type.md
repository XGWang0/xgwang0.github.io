---
layout: post
title:  "Golang 4 种引用类型"
categories: GO
tags:  go
author: Root Wang
---

* content
{:toc}

### 如何区分值类型，还是引用类型
```go
b = a
b.Modify()
``
如果b的修改不会影响到a，那么就是值类型，否则，就是引用类型

### 值语义，值类型
Go语言中的大多数类型为值类型，包括
* 基本类型：byte, int, bool, float32, float64, string 等
* 复合类型：array, struct, pointer等

```go
var a = [3]int{1,2,3}
var b = a
b[0] = 100
fmt.Println(a,b)
-----------------
[1,2,3] [100,2,3]
```
>这表明b = a是数组内容的完整复制。

```go
var a = [3]int{1,2,3}
var b = &a
b[0] = 100
fmt.Printf("%p,%p\n%p,%p", &a,&b,a,b)
fmt.Println(a,b)
-----------------
&a=0xc42001c5c0,&b=0xc42000c030
a=%!p([3]int=[100 2 3]), b=0xc42001c5c0
[100 2 3] &[100 2 3]
```
> b指针的内容是一个地址`b=0xc42001c5c0`，并且这个地址就是a的内存地址。 所以更改b，相当于更改a的内容

### 引用语义，引用类型
* 数组切片：指向array的一个区间
* map
* channel
* 接口

#### 数组切片
本质是一个区间，可以大致将[]T表示为：
```go
type slice struct {
first *T
len int
cap int
}
```
>因为数组切片内部是个指针T，所以改变指针T的元素内容，一定会反映到array T中。 但是数组切片的类型本身赋值仍然是值语义
```go
	var a = [10]int{1, 2, 3, 4, 5, 6, 7, 8, 9, 0}
	var b = a[2:5]
	fmt.Printf("\n%p,%p\n%p,%p\n", &a, &b, a, b)
	fmt.Printf("\n&a=%p,&a[0]=%p,&a[2]=%p,b=%p\n", &a, &a[0], &a[2], b)

-------Result--------
&a=0xc420022050, &b=0xc42000a060
a=%!p([10]int=[1 2 3 4 5 6 7 8 9 0]),  b=0xc420022060
	
&a=0xc420022050,&a[0]=0xc420022050,&a[2]=0xc420022060,b=0xc420022060
```
> b为一个指针，指向a[2]地址，所以更改b的内容，会作用到a中。

#### map
map本质上是一个字典指针，大致可以表示map[key]value为：
```go
type Map_Key_Value struct {
	....
}

type map[key]value struct {
	impl *Map_Key_Value
}
```
> 可以看出更改map的值，将会作用到Map_Key_Value结构体。

#### channel
channel与map类似，本质上也是一个指针。


#### interface

```go
type interface struct {
	data *void
	itab *Itab
}
```

