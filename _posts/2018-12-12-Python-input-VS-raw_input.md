---
layout: post
title:  "input VS raw_input in python2 and python3"
categories: PYTHON
tags:  syntax
author: Root Wang
---

* content
{:toc}

### Diff in both input and raw_input

* Python 2:
    * raw_input() takes exactly what the user typed and passes it back as a string.
    * input() first takes the raw_input() and then performs an eval() on it as well. It means that python automatically identifies whether you entered a number, string or even a list.

* Python 3:
    * raw_input() was renamed to input() so now input() returns the exact string.
    * Old input() was removed.
        If you want to use the old input(), meaning you need to evaluate a user input as a python statement, you have to do it manually by using eval(input()).


### Sample in python2

* raw_input:

    ```python
    >>> abc = raw_input("please input :")
    please input :abcd
    >>> print abc
    abcd
    
    >>> abc = raw_input("please input :")
    please input :1345
    >>> print abc
    1345
    ```

* input:

    ```python
    >>> name = "this is new name"
    >>> abc = input("please input:")
    please input:123
    >>> print abc
    123

    >>> abc = input("please input:")
    please input:"abcdefg"
    >>> print abc
    abcdefg

    >>> abc = input("please input:")
    please input:name
    >>> print abc
    this is new name
    ```


>这里不难看出raw_input不管你输入的是数字还是字符，系统都默认为字符格式。而input 要求用户需要知道要输入的是什么类型。


### Sample in python3

* input

    ```python
    >>> abc = input("please input:")                                                                                                        
    please input:abcd
    >>> print(abc)
    abcd
     
    >>> abc = input("please input:")                                                                                                        
    please input:123456
    >>> print(abc)
    123456
    ```
> The raw_input is removed in python3, and use input to replace raw_input.


* old input

    ```python
    >>> name = "this is new  name in python3"
    
    >>> abc = eval(input("please input:"))                                                                                                  
    please input:12345
    >>> print(abc)
    12345
    >>> abc = eval(input("please input:"))                                                                                                  
    please input:"aaaaaaaa"
    >>> print(abc)
    aaaaaaaa
    >>> abc = eval(input("please input:"))
    please input:name
    >>> print(abc)
    this is new  name in python3
    ```
