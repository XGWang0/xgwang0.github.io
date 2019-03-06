---
layout: post
title:  "VirtIO On KVM-QEMU"
categories: Virtualization
tags:  kvm qemu virtio
author: Root Wang
---

* content
{:toc}

### 概念
virtIO是一种半虚拟化驱动规范， 广泛用于在XEN平台和KVM虚拟化平台，用于`提高客户机IO的效率`，事实证明，virtIO极大的提高了VM IO 效率，配备virtIO前后端驱动的情况下，客户机IO效率基本达到和宿主机(native)一样的水平。本次分析以qemu-kvm架构的虚拟化平台为基础，分析virtIO前后端驱动。当然`后端就指有qemu实现的虚拟PCI设备`，而`前端自然就是客户操作系统中的virtIO驱动`。需要前后配合才能完成数据的传输。

virtIO的出现所解决的另一个问题就是给众多的虚拟化平台提供了一个统一的IO模型，KVM、XEN、VMWare等均可以利用virtIO进行IO虚拟化，在提高IO效率的同时也极大的减少了自家软件开发的工作量。那么对于virtIO基本介绍我们就不详细深入，事实上，前面已经足以说明virtIO是何方神圣，下面主要是深入内在分析virtIO 其实现原理。

### 当前device虚拟化的问题
知其然，便要知其所以然。


使用QEMU模拟I/O的情况下，当客户机中的设备驱动程序（device driver）发起I/O操作请求之时，KVM模块中的I/O操作捕获代码会拦截这次I/O请求，然后经过处理后将本次I/O请求的信息存放到I/O共享页，并通知用户控件的QEMU程序。QEMU模拟程序获得I/O操作的具体信息之后，交由硬件模拟代码来模拟出本次的I/O操作，完成之后，将结果放回到I/O共享页，并通知KVM模块中的I/O操作捕获代码。最后，由KVM模块中的捕获代码读取I/O共享页中的操作结果，并把结果返回到客户机中。当然，这个操作过程中客户机作为一个QEMU进程在等待I/O时也可能被阻塞。另外，当客户机通过DMA（Direct Memory Access）访问大块I/O之时，QEMU模拟程序将不会把操作结果放到I/O共享页中，而是通过内存映射的方式将结果直接写到客户机的内存中去，然后通过KVM模块告诉客户机DMA操作已经完成。

QEMU模拟I/O设备的方式，其优点是可以通过软件模拟出各种各样的硬件设备，包括一些不常用的或者很老很经典的设备（如4.5节中提到RTL8139的网卡），而且它不用修改客户机操作系统，就可以实现模拟设备在客户机中正常工作。在KVM客户机中使用这种方式，对于解决手上没有足够设备的软件开发及调试有非常大的好处。而它的缺点是，每次I/O操作的路径比较长，有较多的VMEntry、VMExit发生，需要多次上下文切换（context switch），也需要多次数据复制，所以它的性能较差。

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/virtio_pic1.jpg)

其带来的缺点：
1.数据的复制
2.根模式和非根模式的频繁切换

优点：
QEMU模拟I/O设备的方式，其优点是可以通过软件模拟出各种各样的硬件设备，包括一些不常用的或者很老很经典的设备（如4.5节中提到RTL8139的网卡），而且它不用修改客户机操作系统，就可以实现模拟设备在客户机中正常工作


那么有没有一种方式能够彻底的解决上面两个问题呢？？当然要彻底消除根模式和非根模式的切换是不可能的，毕竟虚拟机还是有Hypervisor管理的，但是我们可以最大程度的减少这种不必要的切换。virtIO为这一问题提供了比较好的解决方案。

* 第一个问题：数据的复制

在virtIO实现了零复制。不管是什么虚拟化平台，虚拟机是运行在host内存中或者说虚拟机共享同一块内存，那么既然如此我们就没有必要在同一块内存不同区域之间复制数据，而可以进行简单的地址重映射即可。以KVM虚拟机为例，虚拟机运行在HOST的内存中，且在HOST上表现为一个普通的qemu进程。前面我们分析qemu网络虚拟化的时候已经分析，`宿主机接收到数据包会根据目的MAC进行数据包的转发，如果是发往客户机的，则把数据包转发到一个虚拟端口（tap设备模拟），其本质实际上只是把数据共享到一个用户空间应用程序(通过虚拟设备)`，这里我们就是指qemu，这个过程是不需要我们操心的。数据到了qemu,其实这里有一个Net client来接收，

* 第二个问题：根模式和非根模式的频繁切换、

这里考虑下为何会有线程或者说操作系统中`用户模式`和`内核模式`都是同样的道理，线程出现的很大一部分原因就是进程切换代价太高，需要保存和恢复的东西太多，以至于每次切换都要做很多重复的工作，这才有了线程或者说是轻量级的进程。那么在这里，`根模式`和`非根模式`也是这个道理，只是这个模式的`切换比进程的切换需要消耗更多的资源`，因为`每次切换保存的不在是一个普通进程的上下文，而是一个虚拟机的上下文`，尽管`虚拟机在HOST上同样是表现为一个进程，但是其保存的资源更多`。仍然以网络数据包的传送为例。传统的方式，`物理网卡每接收到一个数据帧就需要中断CPU，让CPU处理调用相应的中断服务函数处理数据帧。那么虚拟网卡也是如此，HOST每转发一个数据包到客户机的虚拟网卡，在不使用DMA的情况下就一个数据帧触发一个软中断，客户机就必须VM-exit处理中断，然后VM-entry，该过程不仅包含了数据的复制还包含了根模式非根模式之间的频繁切换`。而即使qemu采用DMA的方式把数据帧直接写入到客户机内存，然后通知客户机，同样免不了数据复制带来的开销。

### virtIO的实现
基于上面描述的问题，virtIo给出了比较好的而解决方案。 而事实上，virtIO的出现不仅仅是解决了效率的问题。`其更是为各大虚拟化引擎提供了一个统一的外部设备驱动`。

先来看个virtIO整体架构图
![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/virtio_pic2.jpg)

先从存储的角度分析一个`数据帧`。首先一个数据帧可能会需要多个buffer块才能完成存储；而一个buffer在这里指我们调用函数申请的虚拟地址空间，对应到物理内存可能包含有多个物理内存块。

qemu中用`VirtQueueElement`结构表示一个`逻辑buffer`，用`VRingDesc结构`描述一个`物理内存块`，用一个`描述符数组`集中`管理所有的描述符`。而`前后端的配合通过两个ring来实现`：VRingAvail和VRingUsed。
当HOST需要向客户机发送数据时:
1. 先从对应的virtqueue获取客户机设置好的buffer空间（实际的buffer空间由客户机添加到virtqueue）,每次取出一个buffer，相关信息记录到VirtQueueElement结构中
2. 然后对其进行地址映射，因为这里记录的buffer信息是客户机的物理地址，需要映射成HOST的虚拟地址才可以对其进行访问。
3. 每完成一个VirtQueueElement 即buffer的的写入,就需要记录VirtQueueElement相关信息到VRingUsed，并撤销地址映射。
4. 一个数据帧写入完成后会设置VRingUsed的idx字段并对客户机注入软件中断以通知客户机



数据帧的逻辑存储结构如下：
![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/virtio_pic3.png)

而物理内存块由一个全局的描述符表统一管理，具体的管理如下图所示：
![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/virtio_pic4.png)

vring 主要通过两个环形缓冲区来完成数据流的转发，如下图所示。
![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/virtio_pic5.png)
深入了解下重要的几个数据结构：
```c
 1 struct VirtQueue
 2 {
 3     VRing vring;//每个queue一个vring
 4     hwaddr pa;//记录virtqueue中关联的描述符表的地址
 5     /*last_avail_idx对应ring[]中的下标*/
 6     uint16_t last_avail_idx;//上次写入的最后一个avail_ring的索引，下次给客户机发送的时候需要从avail_ring+1
 7     /* Last used index value we have signalled on */
 8     uint16_t signalled_used;
 9 
10     /* Last used index value we have signalled on */
11     bool signalled_used_valid;
12 
13     /* Notification enabled? */
14     bool notification;
15 
16     uint16_t queue_index;
17 
18     int inuse;
19 
20     uint16_t vector;
21     void (*handle_output)(VirtIODevice *vdev, VirtQueue *vq);
22     VirtIODevice *vdev;
23     EventNotifier guest_notifier;
24     EventNotifier host_notifier;
25 };
```
> VirtQueue是一个虚拟队列，之所以称之为队列是从其管理buffer的角度。HOST和客户机也正是通过VirtQueue来操作buffer。每个buffer包含一个VRing结构，对buffer的操作实际上是通过VRing来管理的。pa是描述符表的物理地址。last_avail_index对应VRingAvail中ring[]数组的下标，表示上次最后使用的一个buffer首个desc对应的ring[]中的下标。这里听起来有点乱，么关系，后面会详细解释。暂且先介绍这几个。

```c
1 typedef struct VRing
2 {
3     unsigned int num;//描述符表中表项的个数
4     unsigned int align;
5     hwaddr desc;//指向描述符表
6     hwaddr avail;//指向VRingAvail结构
7     hwaddr used;//指向VRingUsed结构
8 } VRing;
```

> 前面说过，VRing管理buffer，其实事实上，VRing是通过描述符表管理buffer的。究竟是怎么个管理法？这里num表示描述符表中的表项数。align是对其粒度。desc表示描述符表的物理地址。avail是VRingAvail的物理地址，而used是VRingUsed的物理地址。到这里是不是有点清楚了捏？？每一个描述符表项都对应一个物理块，参考下面的数据结构，每个表项都记录了其对应物理块的物理地址，长度，标志位，和next指针。同一buffer的不同物理块正是通过这个next指针连接起来的。现在应该比较清晰了吧！

```c
1 typedef struct VRingDesc
2 {
3     uint64_t addr;//buffer 的地址
4     uint32_t len;//buffer的大小，需要注意当描述符作为节点连接一个描述符表时，描述符项的个数为len/sizeof(VRingDesc)
5     uint16_t flags;
6     uint16_t next;
7 } VRingDesc;
```

```c
1 /*一个数据帧可能有多个VirtQueueElement，VirtQueueElement中的index */
 2 typedef struct VirtQueueElement
 3 {
 4     unsigned int index;
 5     unsigned int out_num;
 6     unsigned int in_num;
 7     /*in_addr和 out_addr保存的是客户机的物理地址，而in_sg和out_sg中的地址是host的虚拟地址，两者之间需要映射*/
 8     hwaddr in_addr[VIRTQUEUE_MAX_SIZE];
 9     hwaddr out_addr[VIRTQUEUE_MAX_SIZE];
10     struct iovec in_sg[VIRTQUEUE_MAX_SIZE];
11     struct iovec out_sg[VIRTQUEUE_MAX_SIZE];
12 } VirtQueueElement;
```

> 再说这个VirtQueueElement，前面也说过其对应的是一个逻辑buffer块。而一个逻辑buffer块由多个物理内存块组成。index记录该逻辑buffer块的首个物理内存块对应的描述符在描述符表中的下标，out_num和in_num是指输出和输入块的数量。因为这里一个逻辑buffer可能包含可读区和可写区，即有些物理块是可读的而有些物理块是可写的，out_num记录可读块的数量，而in_num记录可写块的数量。in_addr是一个数组，记录的是可读块的物理地址，out_addr同理。但是由于物理地址是客户机的，所以要想在HOST访问，需要把这些地址映射成HOST的虚拟地址，下面两个就是保存的对应物理块在HOST的虚拟地址和长度。

```c

 2 {
 3     uint16_t flags;//限制host是否向客户机注入中断
 4     uint16_t idx;
 5     uint16_t ring[0];//这是一个索引数组，对应在描述符表中表项的下标，代表一个buffer的head，即一个buffer有多个description组成，其head会记录到
 6                     //ring数组中，使用的时候需要从ring数组中取出一个head才可以
 7 } VRingAvail;
 8 
 9 typedef struct VRingUsedElem
10 {
11     uint32_t id;
12     uint32_t len;//应该表示它代表的数据段的长度
13 } VRingUsedElem;
14 
15 typedef struct VRingUsed
16 {
17     uint16_t flags;//用于限制客户机是否增加buffer后是否通知host
18     uint16_t idx;//
19     VRingUsedElem ring[0];//意义同VRingAvail
20 } VRingUsed;
```
> 这三个放在一起说是因为这三个之间联系密切，而笔者也曾被这几个关系搞得晕头转向。先说VRingAvail和VRingUsed，两个字段基本一致，flags是标识位主要限制HOST和客户机的通知。VRing中的flags限制当HOST写入数据完成后是否向客户机注入中断，而VRingUsed中的flags限制当客户机增加buffer后，是否通知给HOST。这一点在高流量的情况下很有效。就像现在网络协议栈中的NAPI，为何采用中断加轮训而不是采用单纯的中断或者轮询。回到前面，二者也都有idx。VRingAvail中的idx表明客户机驱动下次添加buffer使用的ring下标，VRingUsed中的idx表明qemu下次添加VRingUsedElem使用的ring下标。

然后两者都有一个数组，VRingAvail中的ring数组记录的是`可用buffer 的head index`.即

如果 ring[0]=2， then desctable[2] 记录的就是一个逻辑buffer的首个物理块的信息。

virtqueue中的last_avail_idx记录ring[]数组中`首个可用的buffer头部`。即根据last_avail_idx查找ring[],根据ring[]数组得到desc表的下标。然后last_avail_idx++。

每次HOST向客户机发送数据就需要从这里获取一个buffer head。

当HOST完成数据的写入，可能会产生多个VirtQueueElement，即使用多个逻辑buffer，每个VirtQueueElement的信息记录到VRingUsed的VRingUsedElem数组中，一个元素对应一个VRingUsedElem结构，其中id记录对应buffer的head,len记录长度。

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/virtio_pic6.png)

 小结：上面结合重要的数据结构分析了virtIO后端驱动的工作模式，虽然笔者尽可能的想要分析清楚，但是总感觉表达能力有限，不足之处还请谅解！下面会结合qemu源代码就具体的网络数据包的接收，做简要的分析。


