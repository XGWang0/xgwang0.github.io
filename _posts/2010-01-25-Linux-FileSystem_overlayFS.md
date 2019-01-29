---
layout: post
title:  "Linux overlay FS" 
categories: IO
tags:  FileIO overlayFS
author: Root Wang
---

* content
{:toc}

### overlay文件系统解析
一个 overlay 文件系统包含两个文件系统，一个 `upper` 文件系统和一个 `lower` 文件系统，是一种新型的联合文件系统。overlay是“覆盖…上面”的意思，overlay文件系统则表示一个文件系统覆盖在另一个文件系统上面。
为了更好的展示 overlay 文件系统的原理，现新构建一个overlay文件系统。文件树结构如下：

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/overlayfs_1.png)

1. 在一个支持 overlay文件系统的 Linux (内核3.18以上)的操作系统上一个同级目录内（如/root下）创建四个文件目录 lower 、upper 、merged 、work其中 lower 和 upper 文件夹的内容如上图所示，merged 和work 为空，same文件名相同，内容不同。
2. 在/root目录下执行如下挂载命令，可以看到空的merged文件夹里已经包含了 lower 及 upper 文件夹中的所有文件及目录。
```sh
$mount -t overlay overlay -olowerdir=./lower,upperdir=./upper,workdir=./work ./merged
```
3. 使用df –h 命令可以看到新构建的 overlay 文件系统已挂载。
```sh
Filesystem       Size   Used  Avail  Use%   Mounted on 
overlay          20G   13G  7.8G  62% /root /merged
```

#### merge 
那么 lower 和 upper 目录里有相同的文件夹及相同的文件，合并到 merged 目录里时显示的是哪个呢？规则如下：

1. 文件名及目录不相同，则 lower 及 upper 目录中的文件及目录按原结构都融入到 merged 目录中；
2. 文件名相同，只显示 upper 层的文件。如上图在 lower 和 upper 目录下及下层目录 dir_A 下都有 same.txt 文件，但在合并到 merged 目录时，则只显示 upper 的，而 lower 的隐藏 ;
3. 目录名相同， 对目录进行合并成一个目录。如上图在 lower 及 upper 目录下都有 dir_A 目录，将目录及目录下的所有文件合并到 merged 的 dir_A 目录，目录内如有文件名相同，则同样只显示 upper 的，如上图中 dir_A 目录下的same.txt文件。

overlay只支持两层，upper文件系统通常是可写的；lower文件系统则是只读，这就表示着，当我们对 overlay 文件系统做任何的变更，都只会修改 upper 文件系统中的文件。那下面看一下overlay文件系统的读，写，删除操作。

#### 读
* 读 upper 没有而 lower 有的文件时，需从 lower 读；
* 读只在 upper 有的文件时，则直接从 upper 读
* 读 lower 和 upper 都有的文件时，则直接从 upper 读。

#### 写
* 对只在 upper 有的文件时，则直接在 upper 写
* 对在lower 和 upper 都有的文件时，则直接在 upper 写。
* 对只在 lower 有的文件写时，则会做一个copy_up 的操作，先从 lower将文件拷贝一份到upper，同时为文件创建一个硬链接。此时可以看到 upper 目录下生成了两个新文件，写的操作只对从lower 复制到 upper 的文件生效，而 lower 还是原文件。

#### 删
* 删除 lower 和 upper 都有的文件时，upper 的会被删除，在 upper 目录下创建一个 ‘without' 文件，而 lower 的不会被删除。
* 删除 lower 有而 upper 没有的文件时，会为被删除的文件在 upper 目录下创建一个 ‘without' 文件，而 lower 的不会被删除。
* 删除 lower 和 upper 都有的目录时，upper 的会被删除，在 upper 目录下创建一个类似‘without' 文件的  ‘opaque' 目录，而 lower 的不会被删除。

可以看到，因为 lower 是只读，所以无论对 lower 上的文件和目录做任何的操作都不会对 lower 做变更。所有的操作都是对在 upper 做， 。

copy_up只在第一次写时对文件做copy_up操作，后面的操作都不再需要做copy_up，都只操作这个文件，特别适合大文件的场景。overlay的 copy_up操作要比AUFS相同的操作要快，因为AUFS有很多层，在穿过很多层时可能会有延迟，而overlay 只有两层。而且overlay在2014年并入linux kernel mailline ，但是aufs并没有被并入linux kernel mailline ，所以overlay 可能会比AUFS快。

lower文件系统可以为任何linux支持的文件系统，甚至可以为另一个overlayfs。因为虽然overlay文件系统的底层是由两个文件系统构成，但它本身只是一个文件系统，就如前面用df命令看到的，所以也可以和其他文件系统组成新的overlay文件系统。而upper是可写的，不支持NFS。多层 lower 可执行如下命令：
```sh
$mount -t overlay overlay -olowerdir=/lower1:/lower2:/lower3 ,upperdir=./upper,workdir=./work ./merged
```
上例中，lower 是由三个文件系统合并成一个文件系统，其中lower1在最上面，lower3在最底下。
