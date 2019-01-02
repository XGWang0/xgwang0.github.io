---
layout: post
title:  "Linux 文件读写流扯" 
categories: IO
tags:  FileIO
author: Root Wang
---

* content
{:toc}

### 用户读写文件的流程
***file->dentry->inode->iops->address_space->disk 的流程：***

![](https://github.com/XGWang0/xgwang0.github.io/raw/master/_images/file_sys_structure.png)

#### 通过struct找到磁盘inode节点对象： 
一个进程打开的文件用struct file结构表示，这是VFS可访问的（file中的file_operations）。在file结构中可找到这个文件对应的`dentry`对象，如果两个进程打开同一个文件，那它们的file就指向同一个`dentry`。通过`dentry`就可以找到这个文件对应的`inode`对象，到了`inode`就与特定文件系统（如ext3/ext4）相关了，这个`inode`有读写文件的`file_operations`。那么，如果一个dentry是另一个`dentry`的硬链接，那这两个`dentry`就指向同一个`inode`对象。

#### VFS中的通用read/write调用实际文件系统的read/write： 
在程序`open()`一个文件时，`inode`的`file_operations`就会被填到供VFS使用的`file`结构的`file_operations`，这样实际文件和VFS就建立了联系，就可以开始实际操作这个文件了。

#### 通过address_space接触磁盘： 
在`open`文件之后进行read/write时，读写操作（file_operations）并不是直接跟硬盘交互，而是会经过`address_space`。每个`inode有自己的一个address_space`（inode的i_mapping字段），`address_space`中的`address_space_operations`（如readpage/writepage/readpages/writepages等）才会跟磁盘打交道进行读写。

`address_space`是一个基数树（redix tree），它记录`inode`的内容在`page cache`中是否命中：在读写文件的时候，先会去查是否在page cache中命中，如果在page cache中命中就不用去读写磁盘了。如果没在page cache中，就会通过`address_space_operations`去读写磁盘并添加到这个inode的`address_space`中，这样方便管理且减少和磁盘交互次数。

也就是说，page cache和address_space可认为是同一个东西，这里面可能有脏页，drop_cache和脏页回写都是去找address_space。

每个打开的文件的inode都有其redix树存放它们各自的address_space（也就是它们产生的page cache）。

块设备本身也是一个文件（你也可以打开/dev/sda来读写裸设备），块设备的inode存放在block_device里面的bd_inode成员，即块设备也是有自己的address_space(详见下文),实际上块设备文件是虚拟的文件系统bdevfs中的一个文件。

#### address_space的内存管理方式： 
接下来，在page cache中又有一个概念“buffer”，page cache中的一个page由若干`buffer`组成，一个buffer等于文件系统中一个block的大小，加入buffer的概念是为了方便写磁盘时将`page`转换为`block`。每个inode都有一个`struct buffer_head`链表（inode->i_data.private_list），记录了这个inode里产生的`page cache`里的所有`buffer`，每个buffer_head元素的`b_page`指向该`buffer`位于redix中的`哪个page`，而`b_data`成员就是该`buffer`在page中的`位置的指针`。我们在内核中就可以通过`sb_bread(sb, block_no)`得到文件系统中`block_no`块的数据了。

所以`buffer`是`page cache`里面更小的单元，即`page cache`的redix树记录所有page，每个page又由多个buffer组成。

虽然上层文件系统文件的page cache已经是块设备之上的东西了，但它的page里面仍分成一个个的buffer，一方面文件系统和块设备文件的address_space结构一致方便管理，另外page cache在回写时就不用做额外转换，块设备层可以直接识别其结构并使用。

> buffer cache和page cache:
> 里“buffer cache”中的buffer指的是以前块设备层中用来缓存磁盘内容的结构，一个buffer大小就是磁盘中一个block的大小。这里“page cache”指的是文件系统层用于缓存读写内容的cache，因为这一层在设备层之上，因此和内核其他地方一样，以page为单位来管理。 
> 我们看到free命令打印中，有的版本cached和buffers是分开的，有的版本是“cached/buffers”合并在一起的，和本文说的是一回事儿。
> 
> 这里的“合并”指的是，将两层中的结构统一，都改为page cache，且page中包含一个一个的buffer结构，另外对缓存管理做了优化：在文件系统层缓存的page就无需在块设备层再缓存一份了，而是直接用（块设备中buffer）指针指向（文件系统page cache数据）的方式。当然如果只存在于块设备中的缓存（inode的元数据或直接读写块设备的缓存）还是只产生在块设备层


以前的Linux版本在通过文件系统读的时候，肯定也会走块设备，那么会在块设备层产生buffer，而在文件系统层产生page cache。那么同一份数据就在这两层分别产生了一份，这样的话一致性和效率就不好保证，因此后来，两层都缓存都采用page cache，page cache内部再细分buffer的管理方式。如果是直接操作块设备去读，buffer就产生在块设备文件的page cache，而如果通过文件系统读的，buffer就只产生在文件系统层的page cache，块设备层就只保留相关的元数据（元数据里的数据指针直接指向文件系统层的buffer）。

buffer cache/page cache会存在一致性问题：通过文件系统读文件，那读出的buffer已经在文件系统层的页缓存里了，这时我如果用dd去写相同地址的话，尽管上层已经有这个地址的buffer，但由于是两个独立的读操作，设备层还是会产生一个新的buffer，因为设备层不去感知文件系统层的buffer情况，就可能产生不一致问题。因此实际场景中，尽量避免对一个设备既通过文件系统访问，又通过设备文件的访问，dd之前做一下umount。

#### 直接IO（Direct IO）的流程差异： 
那么Direct IO就是不经过address_space（即page cache）而是直接读写硬盘，所以Direct IO是要求扇区对齐的，避免page和block的转换。 
不经过page cache的方法有两种： 
O_DIRECT：应用程序直接操作硬盘，不产生page cache。一般用于有用户在用户态自己搞cache的情况（例如数据库缓存）。 
O_SYNC：写透（write through）模式，应用程序写page cache的同时也写硬盘。所以会立即更新硬盘，但也产生page cache。

不建议一个系统中有的应用程序用O_DIRECT，有的应用程序又使用page cache，因为这可能会导致page cache不一致的问题，道理很简单，就和DMA要访问内存一样，在DMA读内存时要先刷CPU的cache，page cache也会出现这种情况。当然内核帮你做了这些工作，但是一旦一个应用程序direct模式写硬盘，那对应的page cache就失效，内核工作变复杂，效率也变低。

除了直接IO，page cache和磁盘之间的交互就是address_space的operations操作了。

#### free命令中的cached/buffers： 
我们看free命令中有cached和buffers，现在这两个已经合并了，也就是上面文章中刚刚说到的“合并”。如果非要细分的话，我们访问磁盘时，如果通过文件系统层打开文件（open(“/home/test.txt”, …)），读写文件时inode产生的page cache在free命令中算在“cached”中，而直接操作裸分区（open(“/dev/sda”, …)或直接操作分区）的读写操作产生的page cache在free命令中算在“buffers”中。所以你通过打开/dev/sda设备文件直接操作设备（例如“dd /dev/sda”）产生的page cache也是算在“buffers”中的哦，因为这时读写磁盘是在块设备层。 
就如我上面说的，文件的数据会被缓存在inode本身的page cache中（cached），块设备里面的page cache只有一些这个inode的元数据（buffers）。直接操作块设备的话所有数据就都被缓存在块设备自己的page cache了（buffers）。

buffers和cached都是由inode的address_space统计得来的。例如对于free命令中的buffers或是/proc/meminfo里的buffers的值就是在nr_blockdev_pages()里遍历所有的块设备，把这些设备的bd_inode的address_space（i_mapping）的nr_pages相加得来的。

```c
long nr_blockdev_pages(void)
{
    struct block_device *bdev;
    long ret = 0;
    spin_lock(&bdev_lock);
    list_for_each_entry(bdev, &all_bdevs, bd_list) {
        ret += bdev->bd_inode->i_mapping->nrpages;
    }
    spin_unlock(&bdev_lock);
    return ret;
}
```

### 用户发起IO行为时，数据的走向
在读写文件时，读写操作只和page cache打交道就好了，例如进程的写只是把数据放到page cache并标记dirty。那么page cache中的数据真正写到磁盘的过程是怎样的呢？

#### block和page 
文件系统里的管理单元是block，内存管理是以page为单位，而内核中读写磁盘是通过page cache的，所以就要了解bio是怎么将page和block对应起来的。例如，如果格式化文件系统时指定一个block是4K，那一个block就对应一个page，而如果一个block大小是1K，那一个page就对应4个block，那每次读磁盘就只能每次最小读4个block的大小。 

sector（扇区）是硬件读写的最小操作单元，例如如果一个sector是512字节，而格式化文件系统时指定一个block是1K，那文件系统层面只能每次两个sector一起操作。block是文件系统格式化时确定的，sector是由你的硬盘决定的。但是如果你的block越大，那么你的空间浪费可能就会越大（内部碎片，一个文件的末尾占的block的空闲部分）。

BIO：即Block IO。就是管硬盘的哪些blocks要读到内存的哪些pages。把inode读到内存时，磁盘里这个inode表里记录了这个inode的数据位于磁盘的哪些blocks，当然这些block在硬盘中可能不连续存放，例如要读出一个inode的32KB的内容，但这些block的分布在4个不连续的位置（b1…b2…b3b4b5b6…b7b8），那readpages会将每一段连续的blocks转化成一个bio结构，每个bio结构都记录它里面的blocks在磁盘里的位置以及这些blocks要填到page cache的哪些位置。例如这里就是要生成4个bio对象。那么在一次读过程中，即使一个block大小是1KB，但由于它和其他blocks不连续，那也要单独生成一个bio。

应用程序在读写磁盘时，是通过address_space的operations将page cache中的buffer转换成bio对象再读写磁盘的，但写磁盘的时候并不是以bio为单位的，我们知道一个bio对应一块连续的blocks，可能两个进程都在写这个磁盘或者一个进程两次写请求，提交的bio恰好能拼接成一段更大的连续blocks。注意这时组装bio的过程仍处在每个进程自己的环境中，那么你就会想到，系统中多个进程都读写磁盘时，肯定要在进程之下维护一个请求队列以及相应的调度算法来决定这些bio如何发给磁盘。

每个进程把自己的bio对象先放到自己的plug队列（task->plug）里，这过程中同时会把bio对象转化为request对象，最简单的情形，一个bio对应一个request，但如果发现两个bio的blocks是连续的，那这两个bio就可以合并为一个request。

当这个进程认为自己plug队列够大了（例如在schedule()或io_schedule()释放CPU之前），就着手处理plug队列。例如readpages要读8KB，那这8K的bio组完并且转换成request后，就通过IO调度器（__elv_add_request(),电梯调度算法）向下发（进程相应地进行unplug）。就如同发包的时候，肯定不能一个字节一个字节地发，而是写到缓冲区里再统一发，plug队列就是类似的意思。

接下来，IO调度器开始根据某种调度策略来决定如何将进来的reqeusts向下发。电梯调度的策略有几种，可通过 cat /sys/block/sda/queue/scheduler 来查看sda这个设备使用的电梯调度策略，也可以修改该文件来改变调度策略。有三种：

Noop: 最简单的调度器，把临近的bio进行合并处理。它不会对bio进行排序，因此不适合机械硬盘，因为可能导致磁头来回移动，而适合固态硬盘。 
Deadline: 会给bio排序，优先保证读，但同时写不会饿死。 
CFQ: 也就是完全公平的bio调度，它考虑了进程的优先级，可以设置实时io和非实时io，非实时的也可以设置一个io的nice值（ionice值有0-7，也是越小优先级越高）。

另外，IO调度器就和进程无关了，图中画了多个，分别是cfs/deadline/noop，注册一个新的elevator调度器是通过elv_register()完成的。它们都定义在block/目录下相应文件里，也就是说电梯调度是专门给块设备的IO设计的。

另外，request除了在进程内部由bio合并，在elevator里对连续的request也会进行合并，反正就是尽量合并，减少写磁盘的次数。

ionice可以设置进程的io优先级，通过ionice –help可以查看对io优先级的描述。用ionice启动进程例如 ionice -c 2 -n 7 ./a.out 。-c指定调度策略（实时、完全公平），-n指定nice值。 
通过iotop可以看到进程的io占用率。

经过IO调度后出来的reqeusts就都进入了一个dispatch队列，这时终于进入了块设备驱动，dispatch队列这里就是块设备的“request queue”了。

跟踪块设备的io流程和性能

使用ftrace跟踪块设备：跟踪函数级别的IO流程。例如write过程很慢，到底慢在哪一步，就可以通过ftrace跟踪时间，可以查看走过的函数以及每一步的时间消耗。依赖于/sys/kernel/debug/的存在。 
blktrace/blkparse可以跟踪block级别的IO操作分析，可以看到做了哪些IO操作。

iotop 可以看每个进程的IO流量情况。 
iostat 可以看到每个硬盘上的IO流程情况。例如：
```sh
cd /sys/block/sda/queue
iostat -txz 1
```

### 基于cgroup的IO

我们可以将一些进程加到一个cgroup，另一些进程加到另一个cgroup里面。两个group可以配置不同的权重，相当于基于group来设置ionice。例如： 
在/sys/fs/cgroup/blkio中，创建A和B两个group：
```sh
cd /sys/fs/cgroup/blkio
mkdir A
mkdir B
然后修改A和B的权重（权重越高，拿到的io使用率就越高。看看默认权重是多少，可设置的weight值的范围是多少）：

cd A; echo 100 > blkio.weight
cd ../B; echo 10 > blkio.weight
我分别在指定cgroup里执行IO型程序 dd if=/dev/sda of=/dev/null ，即一直读/dev/sda的内容：

cgexec -g blkio:A dd if=/dev/sda of=/dev/null &
cgexec -g blkio:B dd if=/dev/sda of=/dev/null &
然后通过iotop去看两个进程的io占用率： 
iotop 
就可以看到属于A的进程的io速率就远高于B的进程了。
```

注意，在使用cfq的IO调度算法时（通过/sys/block/sda/queue/schedule查看和修改），weight才起作用，其他的调度算法就没作用。

还可以限制某个group的bio的流量。例如：
```sh
/sys/fs/cgroup/blkio
cd A
echo "8:0 1048576" > blkio.throttle.read_bps_device
其中8:0是设备的主次设备号，1048576是以字节为单位的速率限制，那么这里就限制了设备8:0的读速率最大为1MB。 
运行一个io程序：

cgexec -g blkio:A dd if=/dev/sda of=/dev/null &
通过iotop就可以看到（DISK READ列）读速率被限制了。修改速率值可以看到读速率的变化。

上面是限制读，限制写的话就是修改write_bps_device：

echo "8:0 1048576" > blkio.throttle.write_bps_device
运行一个io程序，写300MB数据到文件/mnt/a：

cgexec -g blkio:A dd if=/dev/zero of=/mnt/a oflag=direct bs=1M count=300 &
通过iotop就可以看到（DISK WRITE列）写速率被限制了。修改速率值可以看到写速率的变化。
```

但这个功能有个缺陷，在cgroup v1版本里面，对于write，你只能限制direct io形式的写的流量，因为如果你先写进page cache，由内核后台线程再去写磁盘的，你并没有将这个内核线程放到cgroup里面，并且这个回写线程是为所有io服务的，是整个系统范围的writeback，也就是说它也负责其他cgroup的进程的写，因此也不能简单地将这个内核线程加到某一个cgroup里面。 
所以在cgroup v2中，对于放进blkio cgroup的进程，它同时会监控这个group里面的进程的dirty情况，因此能够通过控制dirty pages的写回流量来控制blkio流量。 
cgroup的版本是要在kernel里面选择的，kernel同时支持这两种cgroup
