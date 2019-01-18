---
layout: post
title:  "Python C Extension"
categories: PYTHON
tags:  c-extension
author: Root Wang
---

* content
{:toc}

### C 扩展

#### 什么情况下扩展

* Python 没有的额外功能
* 改善性能瓶颈
* 隐藏专有代码，当然也可以用PYC

#### 什么情况不该扩展
* 必须编写C代码
* 需要理解C与PYTHON之间的数据传递
* 需要手动的管理引用


### 示例

#### 创建C代码

上干货 exten_c.c
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int fac(int n)
{
        if (n<2) return(1);
        return n * fac(n-1);
}

char *reserve(char *s)
{
        register char t,
                *p = s,
                *q = (s + strlen(s) - 1);

        while(p < q)
        {

                t = *p;
                *p++ = *q;
                *q-- = t;
        }

        return s;
}

void main()
{
        char s[BUFSIZ];
        char *w = "abcdefg";
        printf("4!=%d\n", fac(4));

        strcpy(s, w);
        printf("Reserve string %s to %s\n", w, reserve(s));
}
```
> Make sure the c code could be right and accessiable and run sucessfully.

#### 根据样板编写封装代码

python 与 C之间是通过一套C的库来完成相互之间的数据传递的。
其目录为： /usr/include/python[23].X/, 可以得到所有所需的函数
m distutils.core import setup, Extension

MOD="extest"

setup(name=MOD, ext_modules=[Extension(MOD, sources=['exten_c.c'])])

封装后的代码为：
```C
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int fac(int n)
{
        if (n<2) return(1);
        return n * fac(n-1);
}

char *reserve(char *s)
{
        register char t,
                *p = s,
                *q = (s + strlen(s) - 1);

        while(p < q)
        {

                t = *p;
                *p++ = *q;
                *q-- = t;
        }

        return s;
}

// 必须用static PyObject 来声明自己的函数
//必须使用 modulename_functionname 的格式定义函数
static PyObject *
extest_fac(PyObject *self, PyObject *args) {
        int res; //parse result
        int num; // fac parameter

        PyObject *retval; //return value

        res = PyArg_ParseTuple(args, "i", &num); 
        //获取python传进来的参数，并转化成C可以使用的类型
        // 具体python的数据类型与C的数据类型对应关系，需要参照对照表 
        if (!res) {
                return NULL;
        }

        res = fac(num); //执行真正的C函数
        retval = (PyObject*)Py_BuildValue("i", res);
        // 转换C的结果成python可以识别的类型
        return retval;
}

static PyObject *
extest_rev1(PyObject *self, PyObject *args) {
        char *orig_str;
        char *dupe_str;
        PyObject *retval; //return value
        if (!PyArg_ParseTuple(args, "s", &orig_str)) return NULL;

        retval = (PyObject*)Py_BuildValue("ss", orig_str, dupe_str=reverse(strdup(orig_str)));
        free(dupe_str);
        return retval;
}

//必须使用PyMethodDef去声明， 
static PyMethodDef extestMethods[] = {
        { "fac", extest_fac, METH_VARARGS }, // {python中的函数名称， 对应的封装函数，返回的值}
        { "rev1", extest_rev1, METH_VARARGS },
        { NULL, NULL},

};


//python2.7可以编译成功， python3需要更改
PyMODINIT_FUNC initextest(void) {

        Py_InitModule("extest", extestMethods);// {python module的名称，对应的module方法列表}
}

``` 

#### 创建安装脚本

```python
#!/usr/bin/env python

from distutils.core import setup, Extension

MOD="extest"

setup(name=MOD, ext_modules=[Extension(MOD, sources=['exten_c.c'])])

```

#### 编译与安装

```sh
python setup build

python setup install
```

#### 使用

```python
#> python
>>> import extest
>>>dir(extest)
['__doc__', '__file__', '__name__', '__package__', 'fac', 'rev2']

>>>extest.fac(4)
24
```
