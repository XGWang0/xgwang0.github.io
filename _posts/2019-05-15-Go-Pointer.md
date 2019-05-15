---
layout: post
title:  "Golang unsafe.Pointer 和 uintptr"
categories: GO
tags:  go
author: Root Wang
---

* content
{:toc}

### 这里有一些关于unsafe.Pointer和uintptr的事实：

* uintptr是一个整数类型.
	即使uintptr变量仍然有效，由uintptr变量表示的地址处的数据也可能被GC回收。

* unsafe.Pointer是一个指针类型。
	1. 但是unsafe.Pointer值不能被取消引用。
	2. 如果unsafe.Pointer变量仍然有效，则由unsafe.Pointer变量表示的地址处的数据不会被GC回收。
	3. unsafe.Pointer是一个通用的指针类型，就像* int等。

* 由于uintptr是一个整数类型，uintptr值可以进行算术运算。 所以通过使用uintptr和unsafe.Pointer，我们可以绕过限制，* T值不能在Golang中计算偏移量：

```c
package main

import (
    "fmt"
    "unsafe"
)

func main() {
    a := [4]int{0, 1, 2, 3}
    p1 := unsafe.Pointer(&a[1])
    p3 := unsafe.Pointer(uintptr(p1) + 2 * unsafe.Sizeof(a[0]))
    *(*int)(p3) = 6
    fmt.Println("a =", a) // a = [0 1 2 6]

    // ...

    type Person struct {
        name   string
        age    int
        gender bool
    }

    who := Person{"John", 30, true}
    pp := unsafe.Pointer(&who)
    pname := (*string)(unsafe.Pointer(uintptr(pp) + unsafe.Offsetof(who.name)))
    page := (*int)(unsafe.Pointer(uintptr(pp) + unsafe.Offsetof(who.age)))
    pgender := (*bool)(unsafe.Pointer(uintptr(pp) + unsafe.Offsetof(who.gender)))
    *pname = "Alice"
    *page = 28
    *pgender = false
    fmt.Println(who) // {Alice 28 false}
}
```
