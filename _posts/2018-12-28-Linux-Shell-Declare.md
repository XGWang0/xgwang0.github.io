---
layout: post
title:  "Linux SHELL Delcare" 
categories: SHELL
tags:  delcare
author: Root Wang
---

* content
{:toc}

### Declare

#### 用途说明

declare命令是bash的一个内建命令，它可以用来声明shell变量，设置变量的属性（Declare variables and/or give them attributes）。该命令也可以写作typeset。虽然人们很少使用这个命令，如果知道了它的一些用法，就会发现这个命令还是挺有用的。

 
#### 常用参数

* +/- 　"-"可用来指定变量的属性，"+"则是取消变量所设的属性。
* -f 　仅显示函数。
* r 　将变量设置为只读。
* x 　指定的变量会成为环境变量，可供shell以外的程序来使用。
* i 　[设置值]可以是数值，字符串或运算式。

```sh
格式：declare

格式：typeset

格式：declare -p

格式：typeset -p

显示所有变量的值。

 

格式：declare -p var

格式：typeset -p var

显示指定变量var的值。

 

格式：declare var=value

格式：typeset var=value

格式：var=value

声明变量并赋值。

 

格式：declare -i var

格式：typeset -i var

将变量var定义成整数。在之后就可以直接对表达式求值，结果只能是整数。如果求值失败或者不是整数，就设置为0。

 

格式：declare -r var

格式：typeset -r var

格式：readonly var

将变量var声明为只读变量。只读变量不允许修改，也不允许删除。

 

格式：declare -a var

格式：typeset -a var

将变量var声明为数组变量。但这没有必要。所有变量都不必显式定义就可以用作数组。事实上，在某种意义上，似乎所有变量都是数组，而且赋值给没有下标的变量与赋值给"[0]"相同。

 

格式：declare -f

格式：typeset -f

显示所有自定义函数，包括名称和函数体。

 

格式：declare -F

格式：typeset -F

显示所有自定义函数名称。

 

格式：declare -f func

格式：typeset -f func

只显示指定函数func的函数定义。

 

格式：declare -x var

格式：typeset -x var

格式：export var

将变量var设置成环境变量，这样在随后的脚本和程序中可以使用。

 

格式：declare -x var=value

格式：typeset -x var=value

格式：export var=value

将变量var设置陈环境变量，并赋值为value。

 
使用示例
示例一 declare是内建命令

[root@web ~]# type -a declare
declare is a shell builtin
[root@web ~]#

[root@jfht ~]# type -a typeset
typeset is a shell builtin
[root@jfht ~]#

 
示例二 declare -i之后可以直接对表达式求值

[root@web ~]# x=6/3
[root@web ~]# echo $x
6/3
[root@web ~]# declare -i x
[root@web ~]# echo $x    
6/3
[root@web ~]# x=6/3
[root@web ~]# echo $x
2

如果变量被声明成整数，可以把表达式直接赋值给它，bash会对它求值。

[root@jfht ~]# x=error
[root@jfht ~]# echo $x
0

如果变量被声明成整数，把一个结果不是整数的表达式赋值给它时，就会变成0.

[root@jfht ~]# x=3.14
-bash: 3.14: syntax error: invalid arithmetic operator (error token is ".14")
如果变量被声明成整数，把一个小数（浮点数）赋值给它时，也是不行的。因为bash并不内置对浮点数的支持。
[root@web ~]#

[root@jfht ~]# declare +i x

此命令的结果是取消变量x的整数类型属性。
[root@jfht ~]# x=6/3
[root@jfht ~]# echo $x
6/3

因为变量x不是整型变量，所以不会自动对表达式求值。可以采用下面两个方式。

[root@jfht ~]# x=$[6/3]
[root@jfht ~]# echo $x
2
[root@jfht ~]# x=$((6/3))
[root@jfht ~]# echo $x  
2
[root@jfht ~]#

 
示例三 声明只读变量

[root@jfht ~]# declare -r r
[root@jfht ~]# echo $r

[root@jfht ~]# r=xxx
-bash: r: readonly variable
[root@jfht ~]# declare -r r=xxx
-bash: declare: r: readonly variable
[root@jfht ~]# declare +r r   
-bash: declare: r: readonly variable
[root@jfht ~]#
[root@jfht ~]# declare +r r
-bash: declare: r: readonly variable
[root@jfht ~]#
[root@jfht ~]# unset r
-bash: unset: r: cannot unset: readonly variable
[root@jfht ~]#

 
示例四 声明数组变量（实际上，任何变量都可以当做数组来操作）

[root@jfht ~]# declare -a names
[root@jfht ~]# names=Jack
[root@jfht ~]# echo ${names[0]}
Jack
[root@jfht ~]# names[1]=Bone
[root@jfht ~]# echo ${names[1]}
Bone
[root@jfht ~]# echo ${names}
Jack
[root@jfht ~]# echo ${names[*]}
Jack Bone
[root@jfht ~]# echo ${#names}
4

直接引用names，相当于引用names[0]
[root@jfht ~]# echo ${#names[*]}
2

[root@jfht ~]# echo ${names[@]}
Jack Bone
[root@jfht ~]# echo ${#names[@]}
2

[root@jfht ~]# declare -p names   
declare -a names='([0]="Jack" [1]="Bone")'
[root@jfht ~]#

 
示例五 显示函数定义

[root@jfht ~]# declare -F
declare -f add_jar
declare -f add_jar2
declare -f add_jar3
[root@jfht ~]# declare -f
add_jar ()
{
    [ -e $1 ] && CLASSPATH=$CLASSPATH:$1
}
add_jar2 ()
{
    if [ -e $1 ]; then
        CLASSPATH=$CLASSPATH:$1;
    else
        if [ -e $2 ]; then
            CLASSPATH=$CLASSPATH:$2;
        fi;
    fi
}
add_jar3 ()
{
    if [ -e $1 ]; then
        CLASSPATH=$CLASSPATH:$1;
    else
        if [ -e $2 ]; then
            CLASSPATH=$CLASSPATH:$2;
        else
            if [ -e $3 ]; then
                CLASSPATH=$CLASSPATH:$3;
            fi;
        fi;
    fi
}
[root@jfht ~]# declare -f add_jar
add_jar ()
{
    [ -e $1 ] && CLASSPATH=$CLASSPATH:$1
}
[root@jfht ~]# declare -F add_jar
add_jar
[root@jfht ~]# declare -F add_
[root@jfht ~]# declare -F add_*
[root@jfht ~]# declare -F 'add_*'
```
