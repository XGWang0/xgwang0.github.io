---
layout: post
title:  "Linux SHELL AWK" 
categories: SHELL
tags:  array
author: Root Wang
---

* content
{:toc}

### awk命令
awk是一种编程语言，用于在linux/unix下对文本和数据进行处理。数据可以来自标准输入(stdin)、一个或多个文件，或其它命令的输出。它支持用户自定义函数和动态正则表达式等先进功能，是linux/unix下的一个强大编程工具。它在命令行中使用，但更多是作为脚本来使用。awk有很多内建的功能，比如数组、函数等，这是它和C语言的相同之处，灵活性是awk最大的优势。

#### awk命令格式和选项
* 语法格式
> awk [options] 'script' var=value file(s) 
> awk [options] -f scriptfile var=value file(s) 

* 常用命令选项
  * -F fs fs 指定输入分隔符，fs可以时字符串或正则表达式
  * -v var=value 赋值一个用户定义变量，将外部变量传递给awk
  * -f scriptfile 从脚本文件中读取awk命令

#### awk脚本
awk脚本是由`模式`和`操作`组成的。

##### 模式
模式可以是以下任意一种：
* 正则表达式：使用通配符的扩展集
* 关系表达式：使用运算符进行操作，可以是字符串或数字的比较测试
* 模式匹配表达式：用运算符～（匹配）和~!不匹配
* BEGIN 语句块， pattern语句块， END语句块

##### 操作
操作由一个或多个命令、函数、表达式组成，之间由换行符或分号隔开，并位于大刮号内，主要部分是：变量或数组赋值、输出命令、内置函数、控制流语句。

#### awk脚本基本格式

```sh
awk 'BEGIN{ commands } pattern{ commands } END{ commands }' file 
```
一个awk脚本通常由BEGIN， 通用语句块，END语句块组成，三部分都是可选的。 脚本通常是被单引号或双引号包住。

```sh
awk 'BEGIN{ i=0 } { i++ } END{ print i }' filename  
awk "BEGIN{ i=0 } { i++ } END{ print i }" filename 
```
awk执行过程分析
1. 执行BEGIN { commands } 语句块中的语句
   BEGIN语句块：在awk开始从输入输出流中读取行之前执行，在BEGIN语句块中执行如变量初始化，打印输出表头等操作。
2. 从文件或标准输入中读取一行，然后执行pattern{ commands }语句块。它逐行扫描文件，从第一行到最后一行重复这个过程，直到全部文件都被读取完毕。
> pattern语句块：pattern语句块中的通用命令是最重要的部分，它也是可选的。如果没有提供pattern语句块，则默认执行{ print }，即`打印每一个读取到的行`。`{ }类似一个循环体`，`会对文件中的每一行进行迭代`，通常将`变量初始化语句放在BEGIN语句块中`，将`打印结果等语句放在END语句块`中。
3. 当读至输入流末尾时，执行END { command }语句块
> END语句块:在awk从输入流中读取完所有的行之后即被执行，比如打印所有行的分析结果这类信息汇总都是在END语句块中完成，它也是一个可选语句块。

#### AWK内置变量
* $n : 当前记录的第n个字段，比如n为1表示第一个字段，n为2表示第二个字段。
* $0 : 这个变量包含执行过程中当前行的文本内容。
* ARGC : 命令行参数的数目。
* ARGIND : 命令行中当前文件的位置（从0开始算）。
* ARGV : 包含命令行参数的数组。
* CONVFMT : 数字转换格式（默认值为%.6g）。
* ENVIRON : 环境变量关联数组。
* ERRNO : 最后一个系统错误的描述。
* FIELDWIDTHS : 字段宽度列表（用空格键分隔）。
* FILENAME : 当前输入文件的名。
* NR : 表示记录数，在执行过程中对应于当前的行号
* FNR : 同NR :，但相对于当前文件。
* FS : 字段分隔符（默认是任何空格）。
* IGNORECASE : 如果为真，则进行忽略大小写的匹配。
* NF : 表示字段数，在执行过程中对应于当前的字段数。 print $NF答应一行中最后一个字段
* OFMT : 数字的输出格式（默认值是%.6g）。
* OFS : 输出字段分隔符（默认值是一个空格）。
* ORS : 输出记录分隔符（默认值是一个换行符）。
* RS : 记录分隔符（默认是一个换行符）。
* RSTART : 由match函数所匹配的字符串的第一个位置。
* RLENGTH : 由match函数所匹配的字符串的长度。
* SUBSEP : 数组下标分隔符（默认值是34）。

##### 将外部变量值传递给awk
借助 -v 选项，可以将来自外部值（非stdin）传递给awk
```sh
VAR=10000
echo | awk -v VARIABLE=$VAR '{ print VARIABLE }'
`

##### 定义内部变量接收外部变量
```sh
var1="aaa"
var2="bbb"
echo | awk '{ print v1,v2 }' v1=$var1 v2=$var2
```

##### 当输入来自文件时
```sh
awk '{ print v1,v2 }' v1=$var1 v2=$var2 filename
```

#### awk运算
* 算术运算：（+，-，*，/，&，！，……，++，--）
>所有用作算术运算符进行操作时，操作数自动转为数值，所有非数值都变为0
* 赋值运算：（=， +=， -=，*=，/=，%=，……=，**=）
* 逻辑运算符: (||, &&)
* 关系运算符：（<, <=, >,>=,!=, ==）
* 正则运算符：（～，～!）(匹配正则表达式，与不匹配正则表达式)
```sh
awk 'BEGIN{a="100testa";if(a ~ /^100*/){print "ok";}}'
ok
```

#### awk高级输入输出

* 读取下一条记录：next 语句
awk中next语句使用：在循环逐行匹配，如果遇到next，就会跳过当前行，直接忽略下面语句。而进行下一行匹配。net语句一般用于多行合并：
```sh
awk 'NR%2==1{next}{print NR,$0;}' text.txt
```
>说明： 当记录行号除以2余1，就跳过当前行。下面的print NR,$0也不会执行。下一行开始，程序有开始判断NR%2值。这个时候记录行号是：2 ，就会执行下面语句块：print NR,$0

```sh
awk 'NR%2==1{line=$0; next}{print NR,$0,line;}' awk
```
> 获取两行合并输出，注意，变量的引用不需要`$`

* 读取一行记录：getline 语句

awk getline用法：输出重定向需用到getline函数。getline从标准输入、管道或者当前正在处理的文件之外的其他输入文件获得输入。它负责从输入获得下一行的内容，并给NF,NR和FNR等内建变量赋值。如果得到一条记录，getline函数返回1，如果到达文件的末尾就返回0，如果出现错误，例如打开文件失败，就返回-1。
语法格式：getline var 变量var包含了特定行的内容
用法说明：

```sh
awk:
var1=1000
aaa
bbb
var2=2000
-------
$ awk '{getline line; print NR,$0,line;}' awk 
2 var1=1000 aaa
4 bbb var2=2000
```

当其左右无重定向符时|，<时：getline作用于当前文件，读入当前文件的第一行给其后跟的变量var或$0（无变量），应该注意到，由于awk在处理getline之前已经读入了一行，所以getline得到的返回结果是隔行的。

当其左右有重定向符时|，<时：getline则作用于定向输入文件，由于该文件是刚打开，并没有被awk读入一行，只是getline读入，那么getline返回的是该文件的第一行，而不是隔行。

#### 文件操作
打开文件 open("filename")

关闭文件 close("filename")

输出到文件 重定向到文件，如echo | awk '{printf("hello word!n") > "datafile"}'

#### 循环结构

for循环
for(变量 in 数组)  
{语句} 
 
for(变量;条件;表达式) 
{语句} 
while循环
while(表达式) 
    {语句} 
do...while循环
do  
{语句} while(条件) 
其他相关语句
break：退出程序循环

continue: 进入下一次循环

next：读取下一个输入行

exit：退出主输入循环，进入END，若没有END或END中有exit语句，则退出脚本。

#### 数组
在awk中数组叫做关联数组(associative arrays)。awk 中的数组不必提前声明，也不必声明大小。数组元素用0或空字符串来初始化，这根据上下文而定。
```sh
awk 'BEGIN{ 
        Array[1]="sun"  
        Array[2]="kai" 
        Array["first"]="www"  
        Array["last"]="name"  
        Array["birth"]="1987" 
         
        info = "it is a test"; 
        lens = split(info,tA," "); 
        for(item in tA) 
        {print tA[item];} 
        for(i=1;i<=lens;i++) 
        {print tA[i];} 
        print length(tA[lens]); 
        } { 
        print "item in array"; 
        for(item in Array) {print Array[item]}; 
        print "print in i++"; 
        for(i=1;i<=length(Array);i++) {print Array[i]};   
        }' 
```
获取数组长度
```sh
awk 'BEGIN{ 
        info="it is a test"; 
        lens=split(info,tA," ");    #使用split函数获取数组长度 
        print length(tA),lens;      #使用length函数获取数组长度（版本有要求） 
        }' 
```
**说明：** **版本够高**的awk当中，支持直接得到数组长度的方法length()，如果awk的版本过低，则不支持。另外，如果传给length的变量是一个字符串，那么length返回的则字符串的长度。
输出数组内容

有序输出 for...in

因为数组时关联数组，默认是无序的

无序输出 for(i=1;i<l=ens;i++)

数组下标从1开始

判断键值是否存在

##### 错误的判断方法，awk数组是关联数组，只要通过数组引用它的KEY，就会自动创建。 
```sh
awk 'BEGIN{ 
    tB["a"]="a1"; 
    tB["b"]="b1"; 
    if(tB["c"]!="1"){   #tB["c"]没有定义，但是循环的时候会输出 
        print "no found"; 
    }; 
    for(k in tB){ 
        print k,tB[k]; 
    }}' 
 ```
##### 正确的判定方法：使用 if ( key in array) 判断数组中是否包含 键值 
```sh
awk 'BEGIN{ 
        tB["a"]="a1"; 
        tB["b"]="b1"; 
        if( "c" in tB){ 
            print "ok"; 
        }; 
        for(k in tB){ 
            print k,tB[k]; 
        }}' 
```

##### 删除键值
delete array[key]可以删除，对应数组key的，序列值。
```sh
awk 'BEGIN{ 
        tB["a"]="a1"; 
        tB["b"]="b1"; 
        delete tB["a"]; 
        for(k in tB){ 
            print k,tB[k]; 
        }}' 
```

#### 二维，多维数组
awk的多维数组在本质上是一维数组，更确切一点，awk在存储上并不支持多维数组。awk提供了逻辑上模拟二维数组的访问方式。例如，array[2,4]=1这样的访问是允许的。awk使用一个特殊的字符串SUBSEP作为分割字段。 类似一维数组的成员测试，多维数组可以使用if ( (i,j) in array)这样的语法，但是下标必须放置在圆括号中。类似一维数组的循环访问，多维数组使用for ( item in array )这样的语法遍历数组。与一维数组不同的是，多维数组必须使用split()函数来访问单独的下标分量。
```sh
awk 'BEGIN{  
    for(i=1;i<=9;i++){  
        for(j=1;j<=9;j++){  
            tarr[i,j]=i*j;  
            print i,"*",j,"=",tarr[i,j];  
            } 
        } 
     }' 
 
awk 'BEGIN{  
        for(i=1;i<=9;i++){  
            for(j=1;j<=9;j++){  
                    tarr[i,j]=i*j; } } 
        for(m in tarr){  
            split(m,tarr2,SUBSEP);  
            print tarr2[1],"*",tarr2[2],"=",tarr[m]; } }' 
```

### 内置函数

#### 算术函数
格式	描述
atan2( y, x )	返回 y/x 的反正切。
cos( x )	返回 x 的余弦；x 是弧度。
sin( x )	返回 x 的正弦；x 是弧度。
exp( x )	返回 x 幂函数。
log( x )	返回 x 的自然对数。
sqrt( x )	返回 x 平方根。
int( x )	返回 x 的截断至整数的值。
rand( )	返回任意数字 n，其中 0 <= n < 1。
srand( [expr] )	将 rand 函数的种子值设置为 Expr 参数的值，或如果省略 Expr 参数则使用某天的时间。返回先前的种子值。

```sh
awk 'BEGIN{ 
        OFMT="%.3f";    #OFMT 设置输出数据格式是保留3位小数。 
        fs=sin(1); 
        fe=exp(10); 
        fl=log(10); 
        fi=int(3.1415); 
        print fs,fe,fl,fi; 
        }' 
输出结果为：0.841 22026.466 2.303 3 
 
awk 'BEGIN{ 
        srand(); 
        fr=int(100*rand()); 
        print fr; 
        }'  
输出：78
``` 

#### 字符串函数
格式	描述
gsub( Ere, Repl, [ In ] )	除了正则表达式所有具体值被替代这点，它和 sub 函数完全一样地执行。
sub( Ere, Repl, [ In ] )	用 Repl 参数指定的字符串替换 In 参数指定的字符串中的由 Ere 参数指定的扩展正则表达式的第一个具体值。sub 函数返回替换的数量。出现在 Repl 参数指定的字符串中的 &（和符号）由 In 参数指定的与 Ere 参数的指定的扩展正则表达式匹配的字符串替换。如果未指定 In 参数，缺省值是整个记录（$0 记录变量）。
index( String1, String2 )	在由 String1 参数指定的字符串（其中有出现 String2 指定的参数）中，返回位置，从 1 开始编号。如果 String2 参数不在 String1 参数中出现，则返回 0（零）。
length [(String)]	返回 String 参数指定的字符串的长度（字符形式）。如果未给出 String 参数，则返回整个记录的长度（$0 记录变量）。
blength [(String)]	返回 String 参数指定的字符串的长度（以字节为单位）。如果未给出 String 参数，则返回整个记录的长度（$0 记录变量）。
substr( String, M, [ N ] )	返回具有 N 参数指定的字符数量子串。子串从 String 参数指定的字符串取得，其字符以 M 参数指定的位置开始。M 参数指定为将 String 参数中的第一个字符作为编号 1。如果未指定 N 参数，则子串的长度将是 M 参数指定的位置到 String 参数的末尾 的长度。
match( String, Ere )	在 String 参数指定的字符串（Ere 参数指定的扩展正则表达式出现在其中）中返回位置（字符形式），从 1 开始编号，或如果 Ere 参数不出现，则返回 0（零）。RSTART 特殊变量设置为返回值。RLENGTH 特殊变量设置为匹配的字符串的长度，或如果未找到任何匹配，则设置为 -1（负一）。
tolower( String )	返回 String 参数指定的字符串，字符串中每个大写字符将更改为小写。大写和小写的映射由当前语言环境的 LC_CTYPE 范畴定义。
toupper( String )	返回 String 参数指定的字符串，字符串中每个小写字符将更改为大写。大写和小写的映射由当前语言环境的 LC_CTYPE 范畴定义。
sprintf(Format, Expr, Expr, . . . )	根据 Format 参数指定的 printf 子例程格式字符串来格式化 Expr 参数指定的表达式并返回最后生成的字符串。
说明： Ere都可以是正则表达式。

时间函数
格式	描述
mktime( YYYY MM dd HH MM ss[ DST])	生成时间格式
strftime([format [, timestamp]])	格式化时间输出，将时间戳转为时间字符串 具体格式，见下表.
systime()	得到时间戳,返回从1970年1月1日开始到当前时间(不计闰年)的整秒数
strftime日期和时间格式说明符 :

格式	描述
%a	星期几的缩写(Sun)
%A	星期几的完整写法(Sunday)
%b	月名的缩写(Oct)
%B	月名的完整写法(October)
%c	本地日期和时间
%d	十进制日期
%D	日期 08/20/99
%e	日期，如果只有一位会补上一个空格
%H	用十进制表示24小时格式的小时
%I	用十进制表示12小时格式的小时
%j	从1月1日起一年中的第几天
%m	十进制表示的月份
%M	十进制表示的分钟
%p	12小时表示法(AM/PM)
%S	十进制表示的秒
%U	十进制表示的一年中的第几个星期(星期天作为一个星期的开始)
%w	十进制表示的星期几(星期天是0)
%W	十进制表示的一年中的第几个星期(星期一作为一个星期的开始)
%x	重新设置本地日期(08/20/99)
%X	重新设置本地时间(12：00：00)
%y	两位数字表示的年(99)
%Y	当前月份
%Z	时区(PDT)
%%	百分号(%)

#### mktime使用 
awk 'BEGIN{tstamp=mktime("2001 01 01 12 12 12");print strftime("%c",tstamp);}'  
输出：2001年01月01日 星期一 12时12分12秒  
 
awk 'BEGIN{tstamp1=mktime("2001 01 01 12 12 12");tstamp2=mktime("2001 02 01 0 0 0");print tstamp2-tstamp1;}'  
输出：2634468  
 
#求2个时间段中间时间差，介绍了strftime使用方法 
awk 'BEGIN{tstamp1=mktime("2001 01 01 12 12 12");tstamp2=systime();print tstamp2-tstamp1;}'  
输出：308201392 
 
#### 其他一般函数
格式	描述
close( Expression )	用同一个带字符串值的 Expression 参数来关闭由 print 或 printf 语句打开的或调用getline 函数打开的文件或管道。如果文件或管道成功关闭，则返回 0；其它情况下返回非零值。如果打算写一个文件，并稍后在同一个程序中读取文件，则 close 语句是必需的。
system(command )	执行 Command 参数指定的命令，并返回退出状态。等同于 system 子例程。
Expression | getline [ Variable ]	从来自 Expression 参数指定的命令的输出中通过管道传送的流中读取一个输入记录，并将该记录的值指定给 Variable 参数指定的变量。如果当前未打开将 Expression 参数的值作为其命令名称的流，则创建流。创建的流等同于调用 popen 子例程，此时 Command 参数取 Expression 参数的值且 Mode 参数设置为一个是 r 的值。只要流保留打开且 Expression 参数求得同一个字符串，则对 getline 函数的每次后续调用读取另一个记录。如果未指定 Variable 参数，则 $0 记录变量和 NF 特殊变量设置为从流读取的记录。
getline [ Variable ] < Expression	从 Expression 参数指定的文件读取输入的下一个记录，并将 Variable 参数指定的变量设置为该记录的值。只要流保留打开且 Expression 参数对同一个字符串求值，则对 getline 函数的每次后续调用读取另一个记录。如果未指定 Variable 参数，则 $0 记录变量和 NF 特殊变量设置为从流读取的记录。
getline [ Variable ]	将 Variable 参数指定的变量设置为从当前输入文件读取的下一个输入记录。如果未指定 Variable 参数，则 $0 记录变量设置为该记录的值，还将设置 NF、NR 和 FNR 特殊变量。
#打开外部文件（close用法） 
awk 'BEGIN{while("cat /etc/passwd"|getline){print $0;};close("/etc/passwd");}'  
输出: root:x:0:0:root:/root:/bin/bash bin:x:1:1:bin:/bin:/sbin/nologin daemon:x:2:2:daemon:/sbin:/sbin/nologin  
 
#逐行读取外部文件(getline使用方法）  
awk 'BEGIN{while(getline < "/etc/passwd"){print $0;};close("/etc/passwd");}'  
输出：root:x:0:0:root:/root:/bin/bash bin:x:1:1:bin:/bin:/sbin/nologin daemon:x:2:2:daemon:/sbin:/sbin/nologin  
 
awk 'BEGIN{print "Enter your name:";getline name;print name;}' 
Enter your name:  
chengmo  
chengmo  
 
#### 调用外部应用程序(system使用方法） b返回值，是执行结果。 
awk 'BEGIN{b=system("ls -al");print b;}'  
输出： total 42092 drwxr-xr-x 14 chengmo chengmo 4096 09-30 17:47 . drwxr-xr-x 95 root root 4096 10-08 14:01 ..  
 
