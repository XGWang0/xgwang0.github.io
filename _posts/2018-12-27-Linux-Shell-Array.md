---
layout: post
title:  "Linux SHELL Array" 
categories: SHELL
tags:  array
author: Root Wang
---

* content
{:toc}

```sh
数组定义法1：
arr=(1 2 3 4 5) # 注意是用空格分开，不是逗号！！
 
数组定义法2：
array
array[0]="a"
array[1]="b"
array[2]="c"
 
获取数组的length（数组中有几个元素）：
${#array[@]}
 
遍历（For循环法）：
for var in ${arr[@]};
do
    echo $var
done
 
遍历（带数组下标）：
for i in "${!arr[@]}"; 
do 
    printf "%s\t%s\n" "$i" "${arr[$i]}"
done
 
遍历（While循环法）：
i=0
while [ $i -lt ${#array[@]} ]
do
    echo ${ array[$i] }
    let i++
done
 
向函数传递数组：
由于Shell对数组的支持并不号，所以这是一个比较麻烦的问题。
翻看了很多StackOverFlow的帖子，除了全局变量外，无完美解法。
这里提供一个变通的思路，我们可以在调用函数前，将数组转化为字符串。
在函数中，读取字符串，并且分为数组，达到目的。
 
fun() {
    local _arr=(`echo $1 | cut -d " "  --output-delimiter=" " -f 1-`)
    local _n_arr=${#_arr[@]}
    for((i=0;i<$_n_arr;i++));
    do  
       elem=${_arr[$i]}
       echo "$i : $elem"
    done; 
}
 
array=(a b c)
fun "$(echo ${array[@]})"
```
