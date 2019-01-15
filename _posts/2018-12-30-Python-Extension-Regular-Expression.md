---
layout: post
title:  "Python Extension Regular Expression"
categories: PYTHON
tags:  re
author: Root Wang
---

* content
{:toc}

### Extension RE

#### 命名分组

命名分组就是给具有默认分组编号的组另外再给一个别名。命名分组的语法格式如下：

> (?P<name>正则表达式)#name是一个合法的标识符

如：提取字符串中的ip地址
```python
>>> s = "ip='230.192.168.78',version='1.0.0'"
>>> re.search(r"ip='(?P<ip>\d+\.\d+\.\d+\.\d+).*", s)
>>> res.group('ip')#通过命名分组引用分组
'230.192.168.78'
```

#### 后向引用

正则表达式中，放在圆括号“()”中的表示是一个组。然后你可以对整个组使用一些正则操作,例如重复操作符。 
要注意的是,只有圆括号”()”才能用于形成组。”“用于定义字符集。”{}”用于定义重复操作。 
当用”()”定义了一个正则表达式组后,正则引擎则会把被匹配的组按照顺序编号,存入缓存。这样我们想在后面对已经匹配过的内容进行引用时，就可以用”\数字”的方式或者是通过命名分组进行”(?P=name)“进行引用。\1表示引用第一个分组,\2引用第二个分组,以此类推,\n引用第n个组。而\0则引用整个被匹配的正则表达式本身。这些引用都必须是在正则表达式中才有效，用于匹配一些重复的字符串。 
如：

#通过命名分组进行后向引用
```python
>>> re.search(r'(?P<name>go)\s+(?P=name)\s+(?P=name)', 'go go go').group('name')
'go'
```

#通过默认分组编号进行后向引用
```python
>>> re.search(r'(go)\s+\1\s+\1', 'go go go').group()
'go go go'
```

交换字符串的位置
```python
>>> s = 'abc.xyz'
>>> re.sub(r'(.*)\.(.*)', r'\2.\1', s)
'xyz.abc'
```

#### 断言

正则表达式的先行断言和后行断言一共有4种形式： 
* (?=pattern) 零宽正向先行断言(zero-width positive lookahead assertion) 
* (?!pattern) 零宽负向先行断言(zero-width negative lookahead assertion) 
* (?<=pattern) 零宽正向后行断言(zero-width positive lookbehind assertion) 
* (?<!pattern) 零宽负向后行断言(zero-width negative lookbehind assertion) 

如同^代表开头，$代表结尾，\b代表单词边界一样，先行断言和后行断言也有类似的作用，它们只匹配某些位置，在匹配过程中，不占用字符，所以被称为“零宽”。所谓位置，是指字符串中(每行)第一个字符的左边、最后一个字符的右边以及相邻字符的中间（假设文字方向是头左尾右）。

##### (?=pattern) 正向先行断言 

代表字符串中的一个位置，紧接该位置之后的字符序列能够匹配pattern。 
例如对”a regular expression”这个字符串，要想匹配regular中的re，但不能匹配expression中的re，可以用”re(?=gular)”，该表达式限定了re右边的位置，这个位置之后是gular，但并不消耗gular这些字符，将表达式改为”re(?=gular).”，将会匹配reg，元字符.匹配了g，括号这一砣匹配了e和g之间的位置。

```python
# 只匹配regex
str = 'regex represents regular expression'

s1 = re.findall(r"re(?=gex)\w+",str)
print(s1)
---------------------
['regex']
```

##### (?!pattern) 负向先行断言 
代表字符串中的一个位置，紧接该位置之后的字符序列不能匹配pattern。 
例如对”regex represents regular expression”这个字符串，要想匹配除regex和regular之外的re，可以用”re(?!g)”，该表达式限定了re右边的位置，这个位置后面不是字符g。负向和正向的区别，就在于该位置之后的字符能否匹配括号中的表达式。

##### (?<=pattern) 正向后行断言 
代表字符串中的一个位置，紧接该位置之前的字符序列能够匹配pattern。 
例如对”regex represents regular expression”这个字符串，有4个单词，要想匹配单词内部的re，但不匹配单词开头的re，可以用”(?<=\w)re”，单词内部的re，在re前面应该是一个单词字符。之所以叫后行断言，是因为正则表达式引擎在匹配字符串和表达式时，是从前向后逐个扫描字符串中的字符，并判断是否与表达式符合，当在表达式中遇到该断言时，正则表达式引擎需要往字符串前端检测已扫描过的字符，相对于扫描方向是向后的。

##### (?<!pattern) 负向后行断言 
代表字符串中的一个位置，紧接该位置之前的字符序列不能匹配pattern。 
例如对”regex represents regular expression”这个字符串，要想匹配单词开头的re，可以用”(?<!\w)re”。单词开头的re，在本例中，也就是指不在单词内部的re，即re前面不是单词字符。当然也可以用”\bre”来匹配。


#### 对于这4个断言的理解 
1. 关于先行(lookahead)和后行(lookbehind)：正则表达式引擎在执行字符串和表达式匹配时，会从头到尾（从前到后）连续扫描字符串中的字符，设想有一个扫描指针指向字符边界处并随匹配过程移动。先行断言，是当扫描指针位于某处时，引擎会尝试匹配指针还未扫过的字符，先于指针到达该字符，故称为先行。后行断言，引擎会尝试匹配指针已扫过的字符，后于指针到达该字符，故称为后行。 
2. 关于正向(positive)和负向(negative)：正向就表示匹配括号中的表达式，负向表示不匹配。


#### 限制
括号里的pattern本身是一个正则表达式。但对2种`后行断言`有所限制，在Python中，这个表达式必须是定长(fixed length)的，即不能使用`*、+、?`等元字符，如(?<=abc)没有问题，但(?<=a*bc)是不被支持的，特别是当表达式中含有|连接的分支时，各个分支的长度必须相同。之所以不支持变长表达式，是因为当引擎检查后行断言时，无法确定要回溯多少步。
