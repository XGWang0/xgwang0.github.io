---
layout: post
title:  "C 空指针， 空指针常量， NULL， 0, （void *）0, 野指针"
categories: C
tags:  C 
author: Root Wang
---

* content
{:toc}

#### 什么是空指针常量（null pointer constant）?

[6.3.2.3-3] An integer constant expression with the value 0, or such an expression cast to type void *, is called a null pointer constant.

这里告诉我们：0、0L、'\0'、3 - 3、0 * 17 （它们都是“integer constant expression”）以及 (void*)0 （tyc： 我觉得(void*)0应该算是一个空指针吧，更恰当一点）等都是空指针常量（注意 (char*) 0 不叫空指针常量，只是一个空指针值）。至于系统选取哪种形式作为空指针常量使用，则是实现相关的。一般的 C 系统选择 (void*)0 或者 0 的居多（也有个别的选择 0L）；至于 C++ 系统，由于存在严格的类型转化的要求，void* 不能象 C 中那样自由转换为其它指针类型，所以通常选 0 作为空指针常量（tyc: C++标准推荐），而不选择 (void*)0。

#### 什么是空指针（null pointer）?

[6.3.2.3-3] If a null pointer constant is converted to a pointer type, the resulting pointer, called a null pointer, is guaranteed to compare unequal to a pointer to any object or function.

因此，如果 p 是一个指针变量，则 p = 0;、p = 0L;、p = '\0';、p = 3 - 3;、p = 0 * 17; 中的任何一种赋值操作之后（对于 C 来说还可以是 p = (void*)0;）， p 都成为一个空指针，由系统保证空指针不指向任何实际的对象或者函数。反过来说，任何对象或者函数的地址都不可能是空指针。（tyc: 比如这里的(void*)0就是一个空指针。把它理解为null pointer还是null pointer constant会有微秒的不同，当然也不是紧要了）

#### 什么是 NULL？

[6.3.2.3-Footnote] The macro NULL is defined in <stddef.h> (and other headers) as a null pointer constant

即 NULL 是一个标准规定的宏定义，用来表示空指针常量。因此，除了上面的各种赋值方式之外，还可以用 p = NULL; 来使 p 成为一个空指针。（tyc：很多系统中的实现：#define NULL (void*)0，与这里的“a null pointer constant”并不是完全一致的）

#### 空指针（null pointer）指向了内存的什么地方（空指针的内部实现）？

标准并没有对空指针指向内存中的什么地方这一个问题作出规定，也就是说用哪个具体的地址值（0x0 地址还是某一特定地址）表示空指针取决于系统的实现。我们常见的空指针一般指向 0 地址，即空指针的内部用全 0 来表示（zero null pointer，零空指针）；也有一些系统用一些特殊的地址值或者特殊的方式表示空指针（nonzero null pointer，非零空指针），具体请参见C FAQ。

幸运的是，在实际编程中不需要了解在我们的系统上空指针到底是一个 zero null pointer 还是 nonzero null pointer，我们只需要了解一个指针是否是空指针就可以了——编译器会自动实现其中的转换，为我们屏蔽其中的实现细节。注意：不要把空指针的内部表示等同于整数 0 的对象表示——如上所述，有时它们是不同的。

#### 如何判断一个指针是否是一个空指针？

这可以通过与空指针常量或者其它的空指针的比较来实现（注意与空指针的内部表示无关）。例如，假设 p 是一个指针变量，q 是一个同类型的空指针，要检查 p 是否是一个空指针，可以采用下列任意形式之一——它们在实现的功能上都是等价的，所不同的只是风格的差别。

指针变量 p 是空指针的判断：

```c
if ( p == 0 )
if ( p == '\0' )
if ( p == 3 - 3 )
if ( p == NULL )  /* 使用 NULL 必须包含相应的标准库的头文件 */
if ( NULL == p )
if ( !p )
if ( p == q )
...

指针变量 p 不是空指针的判断：
if ( p != 0 )
if ( p != '\0' )
if ( p != 3 - 3 )
if ( p != NULL )  /* 使用 NULL 必须包含相应的标准库的头文件 */
if ( NULL != p )
if ( p )
if ( p != q )
...
```

#### 可以用 memset 函数来得到一个空指针吗？

这个问题等同于：如果 p 是一个指针变量，那么

memset( &p, 0, sizeof(p) ); 和 p = 0;是等价的吗？

答案是否定的，虽然在大多数系统上是等价的，但是因为有的系统存在着“非零空指针” （nonzero null pointer），所以这时两者不等价。由于这个原因，要注意当想将指针设置为空指针的时候不应该使用 memset，而应该用空指针常量或空指针对指针变量赋值或者初始化的方法。

#### 可以定义自己的 NULL 的实现吗？兼答"NULL 的值可以是 1、2、3 等值吗？"类似问题

[7.1.3-2] If the program declares or defines an identifier in a context in which it is reserved (other than as allowed by 7.1.4), or defines a reserved identifier as a macro name, the behavior is undefined.

NULL 是标准库中的一个符合上述条件的 reserved identifier （保留标识符）。所以，如果包含了相应的标准头文件而引入了 NULL 的话，则再在程序中重新定义 NULL 为不同的内容是非法的，其行为是未定义的。也就是说，如果是符合标准的程序，其 NULL 的值只能是 0，不可能是除 0 之外的其它值，比如 1、2、3 等。

#### malloc 函数在分配内存失败时返回 0 还是 NULL？

malloc 函数是标准 C 规定的库函数。在标准中明确规定了在其内存分配失败时返回的是一个 “null pointer”（空指针）：

[7.20.3-1] If the space cannot be allocated, a null pointer is returned.

对于空指针值，一般的文档（比如 man）中倾向于用 NULL 表示，而没有直接说成 0。但是我们应该清楚：对于指针类型来说，返回 NULL 和 返回 0 是完全等价的，因为 NULL 和 0 都表示 “null pointer”（空指针）。（tyc：一般系统中手册中都返回NULL，那我们就用NULL吧）


#### 野指针

```c
int *p1 = NULL;//空指针
int *p2;//野指针
```

例如  int *p = 0x123456;   这就是一个野指针，我们并不知道这个地址存的是什么内容

注意下面的例子

```c
void freePoint(int *&p)
{
		free(p);
			//注意 释放指针后， 一定要将指针指向NULL  
			//否则p指向的空间是未知数据  p就成了野指针
			p = NULL;
}
 
int main()
{
		int a = 1;
			int *p1 = &a;
				freePoint(p1);
					return 0;
}
```
