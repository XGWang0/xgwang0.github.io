---
layout: post
title:  "HDD 结构"
categories: disk
tags:  hdd
author: Root Wang
---

* content
{:toc}

### 硬盘结构

对于管理磁盘，分磁盘面、磁头、磁道、柱面和扇区:

* 磁盘面：磁盘是由一叠磁盘面组成，见下左图。
* 磁头(Heads)：每个磁头对应一个磁盘面，负责该磁盘面上的数据的读写。
* 磁道(Track)：每个盘面会围绕圆心划分出多个同心圆圈，每个圆圈叫做一个磁道。
* 柱面(Cylinders)：所有盘片上的同一位置的磁道组成的立体叫做一个柱面。
* 扇区(Sector)：以磁道为单位管理磁盘仍然太大，所以计算机前辈们又把每个磁道划分出了多个扇区，见下图

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/hdd_structure.jpg)

Linux上可以通过fdisk命令，来查看当前系统使用的磁盘的这些物理息。
```sh
[root@dbserver ~]# fdisk -l

 Disk /dev/sda: 1199.6 GB, 1199638052864 bytes
 255 heads, 63 sectors/track, 145847 cylinders
 Units = cylinders of 16065 * 512 = 8225280 bytes
 Sector size (logical/physical): 512 bytes / 512 bytes
 I/O size (minimum/optimal): 512 bytes / 512 bytes
 Disk identifier: 0x54ab02ca

    Device Boot      Start        End      Blocks  Id  System
/dev/sda1              1          5      40131  de  Dell Utility
 Partition 1 does not end on cylinder boundary.
 /dev/sda2  *          6        267    2097152    c  W95 FAT32 (LBA)
 ......
```
 
可以看出我的磁盘有255个`heads`，也就是说共有255个`盘面`。145847 个`cylinders`，也就是说每个盘面上都有145847 个`磁道`， 63`sectors/track`说的是每个磁道上共有63个扇区。命令结果也给出了`Sector size`的值是512bytes。那我们动笔算一下该磁盘的大小。

**255盘面  * 145847 柱面 * 63扇区 * 每个扇区512bytes =1199632412160 byte=1117.25GB**

结果是1117.25GB,和磁盘的总大小相符。

 在如上图可以发现一个错误（标红），是即/dev/sda1的start位置从第 1 扇区个删除开始，如果将第0至62个扇区,即第一磁道（cylinders）单独留给磁盘MBR并从第64个扇区，即第二个磁道（cylinders）开始分区，将会对文件系统的性能会带来很大的提升。
  
#### MBR:
MBR位于整个磁盘的的第一个扇区，总体分为三部分：

    boot loader：主要作用是把内核加载到内存中，引导系统加载

    分区表DPT（16字节*4）：保存着磁盘的分区信息，由于DPT只有64字节，因此最多只能划分四个分区，说到底对于磁盘的分区不过只是对DPT的分区而已，当然了，系统会预留一个扩展分区（Extended），扩展分区本身并不能创建文件系统格式化，对它继续划分，这样就可以划分出更多的分区（逻辑分区），而且每个逻辑分区中的前几个扇区也会用来记载分区信息

#### GPT:
GPT的全称是Globally Unique Identifier Partition Table，意即GUID分区表，它的推出是和UEFI BIOS相辅相成的，鉴于MBR的磁盘容量和分区数量已经不能满足硬件发展的需求，GPT首要的任务就是突破了2.2T分区的限制，最大支持18EB的分区。

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/GPT_structure.png)

而在分区数量上，GPT会为每一个分区分配一个全局唯一的标识符，理论上GPT支持无限个磁盘分区。在每一个分区上，这个标识符是一个随机生成的字符串，可以保证为地球上的每一个GPT分区都分配完全唯一的标识符。

而在安全性方面，GPT分区表也进行了全方位改进。在早期的MBR磁盘上，分区和启动信息是保存在一起的。如果这部分数据被覆盖或破坏，事情就麻烦了。相对的，GPT在整个磁盘上保存多个这部分信息的副本，因此它更为健壮，并可以恢复被破坏的这部分信息。GPT还为这些信息保存了循环冗余校验码（CRC）以保证其完整和正确——如果数据被破坏，GPT会发觉这些破坏，并从磁盘上的其他地方进行恢复


#### 磁盘IO时的过程。
1. 首先是磁头径向移动来寻找数据所在的磁道。这部分时间叫寻道时间。
2. 找到目标磁道后通过盘面旋转，将目标扇区移动到磁头的正下方。
3. 向目标扇区读取或者写入数据。到此为止，一次磁盘IO完成。

*故：单次磁盘IO时间 = 寻道时间 + 旋转延迟 + 存取时间。*

* 对于旋转延时，现在主流服务器上经常使用的是1W转/分钟的磁盘，每旋转一周所需的时间为60*1000/10000=6ms，故其旋转延迟为（0-6ms）。
* 对于存取时间，一般耗时较短，为零点几ms。
* 对于寻道时间，现代磁盘大概在3-15ms，其中寻道时间大小主要受磁头当前所在位置和目标磁道所在位置相对距离的影响。 

*操作系统通过按磁道对应的柱面划分分区，来降低磁盘IO所花费的的寻道时间 ，进而提高磁盘的读写性能。*
