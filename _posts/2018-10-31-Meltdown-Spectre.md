---
layout: post
title:  "Hive Installation And Using"
categories: hive
tags:  bigdata HA cluster hive mapreduce
author: Root Wang
---

* content
{:toc}

## Meltdown

Meltdown breaks the most fundamental isolation between `user applications` and `the operating system`. This attack allows a program to access the memory, and thus also the secrets, of other programs and the operating system.

On modern processors, the isolation between the kernel and user processes is typically realized by `a supervisor bit of the processor that defines whether a memory page of the kernel can be accessed or not`. The basic idea is that this bit can only be set when entering kernel code and it is cleared when switching to user processes. This hardware feature allows operating systems to map the kernel into the address space of every process and to have very efficient transitions from the user process to the kernel, e.g., for interrupt handling. Consequently, in practice, there is no change of the memory mapping when switching from a user process to the kernel.

In this work, we present Meltdown1. Meltdown is anovel attack that allows overcoming memory isolationcompletely by providing a simple way for any user processto read the entire kernel memory of the machine itexecutes on, including all physical memory mapped inthe kernel region. Meltdown does not exploit any softwarevulnerability, i.e., it works on all major operatingsystems. Instead, Meltdown exploits side-channel informationavailable on most modern processors, e.g., modern Intel microarchitectures since 2010 and potentiallyon other CPUs of other vendors


While side-channel attacks typically require very specificknowledge about the target application and are tailoredto only leak information about its secrets, Meltdownallows an adversary who can run code on the vulnerableprocessor to obtain a dump of the entire kerneladdress space, including any mapped physical memory.`The root cause of the simplicity and strength of Meltdownare side effects caused by out-of-order execution.`

enclave : 用户空间运行环境
sid-channel attacks : 

威胁模型:

侧信道攻击主要目标是攻击enclave数据的机密性（confidentiality）。攻击者来自non-enclave 部分，包括应用程序和系统软件。系统软件包括OS，hypervisor，SMM，BIOS 等特权级软件。

侧信道攻击一般假设攻击者知道enclave 初始化时候的代码和数据，并且知道内存布局。内存布局包括虚拟地址，物理地址以及他们之间的映射关系。有些侧信道攻击假设攻击者知道enclave 的输?数据，并且可以反复触发enclave，进行多次观察记录。侧信道攻击还假设攻击者知道运行enclave 平台的硬件配置、特性和性能，比如CPU，TLB，cache，DRAM，页表，中断以及异常等各种系统底层机制。

侧信道的攻击面:
enclave 和non-enclave共享大量的系统资源，这就给侧信道攻击留下了非常大的攻击面。经过对现有资料的总结和系统结构的分析，我们把SGX的攻击总结在图2里面。

![](https://github.com/XGWang0/wiki/raw/master/_images/meltdown-spectre_1.jpg)

如图2所示，enclave 的运行过程中会用到

> 1. CPU 内部结构。比如pipeline，branch prediction Buffer（BPB）等等。这些结构不能够直接访问，但是如果可以间接利用[16]，仍然可能泄露enclave的控制流或数据流。
>
>2. TLB。TLB 有包括iTLB，dTLB 和L2 TLB。如果HyperThreading打开，两个逻辑核共享一个物理核，这个时候会大大增加侧信道的可能。
>
>3. Cache。Cache 包括L1 instruction cache，L1 data cache，L2cache 和L3 cache（又叫LLC cache）。
>
>4. DRAM。DRAM 包含channels，DIMMs，ranks，banks。每个banks又包含rows、columns 和row buffer。
>
>5. Pagetable（页表）。页表可以通过权限控制来触发缺页异常，也可以通过页表的状态位来表明CPU 的某些操作。对于不同的攻击面，攻击者需要了解具体的细节和工作原理。其中比较重要的参考的文档就是Intel 的手册[14, 13]。目前SGX 已经部署在SkyLake 的机器上面。因此我们需要对SkyLake 的一些硬件和性能细节重点掌握。文档[2]对SkyLake i7-6700 的一些CPU 细节和性能做了一个比较全面的介绍和测量

侧信道攻击:

1.基于页表的攻击:
最早的SGX 侧信道攻击就是基于页表的攻击[29, 27]。这类利用页表对enclave 页面的访问控制权，设置enclave 页面为不可访问。这个时候任何访问都会触发缺页异常，从而能够区分enclave 访问了哪些页面。按照时间顺序把这些信息组合，就能够反推出enclave 的某些状态和保护的数据。该类典型的攻击包括controlled-channel attack [29] 和pigeonholeattack [27]。这类攻击的缺点就是精度只能达到页粒度，无法区分更细粒度的信息。但是在某些场景下，这类攻击已经能够获得大量有用信息。例如图4所示，这类基于页表的侧信道攻击可以获得libjpeg 处理的图片信息.经过还原，基本上达到人眼识别的程度。pigeonhole 攻击也展示了大量对现有的安全库的攻击.

后来，基于页表的攻击有了新的变种。这些侧信道攻击主要利用页表的状态位[28]。如图6所示，一个页表项有很多位，有些是用来做访问控制，比如P, RW, US, XD，有些则标识状态，比如D（dirty bit）和A（accessbit）。如果A bit 被设置，则表明该页表项指向的页面已经被访问；如果Dbit被设置，则表明该页表项指向的页面发生了写操作。通过监控观察这些状态位，攻击者就可以获取和controlled-channel/pigeonhole 攻击类似的信息。

2.基于TLB 的攻击
目前还没有完全基于TLB 的攻击，但是已经出现TLB 作为辅助手段的侧信道攻击，我们会在混合侧信道攻击的章节3.3.6里面介绍。关于TLB的两点重要信息，我们需要了解，希望对提出新的基于TLB 的侧信道攻击和防御有所帮助。

>    \1. TLB 的层次结构。目前SkyLake 的机器，分为L1 和L2 两层。不同层次出现的TLB miss 的时间代价不同。
>
>    \2. TLB 对代码和数据的区分。L1 区分代码（iTLB）和数据（dTLB）。两者直接有cache coherence 的保证。L2 不区分代码和数据。


3.基于Cache 的攻击

传统侧信道有很多基于cache 的攻击[19, 30, 17, 10, 11]. 在SGX的环境里面，这些侧信道技术仍然适用，而且可以做的更好。原因在于，在SGX 环境里面攻击者可以控制整个系统的资源。因此，攻击者可以有针对性地调度资源，减小侧信道的噪音，增加侧信道的成功率。降低噪音的策略大体可以有以下几种[8, 21, 1, 25]：


> 1. Core Isolation(核隔离)。这个方法的主要目标就是让enclave 独自占有一个核（不允许其他程序运行在该核上面）。
> 
> 2. Cache Isolation(缓存隔离)。尽量使用L1 或者L2 级别的cache 进行侧信道攻击。L3 的cache 被所有的核共用，会引入不必要的噪音。
> 
> 3. Uninterupted Execution（不间断运行）。也就是不触发或尽量少触发AEX，因为AEX 和后续的ISR（interrupt sevice rountine) 都会使用cache，从而引入不必要噪音。少触发AEX 就是要使用中断绑定（interrupt affinity）和将时钟频率。不触发AEX 基本上就是让系统软件（比如OS）屏蔽所有中断。


除了降低噪音，攻击者还可以提高攻击的精度，大体策略有：
>     1.高精度时钟。可以采用APIC 提供的高精度时钟和硬件TSC。
> 
>     2. 放大时间差异。比如攻击者可以配置侧信道攻击代码所在的CPU 以最高频率运行，而对enclave 所在的CPU 进行降频处理。

基于cache 的侧信道攻击可以进行细粒度的监控。最小粒度可以做到一个cache line，即64 个字节。由于粒度更小，基于cache 的侧信道可以比基于页表的侧信道（以及后面介绍的基于DRAM 的侧信道）获得更多的信息。


4.基于DRAM 的攻击

在讲解基于DRAM 的侧信道之前，我们首先了解一些DRAM 的基本知识。DRAM 一般由channel，DIMM, rank, bank 等部分构成，如图7所示。每个bank 又有columns 和rows 组成。每个bank里面还有一个row buffer 用来缓存最近访问过的一个row。在访问DRAM 的时候，如果访问地址已经被缓存在row buffer 当中（情况A），就直接从buffer 里面读取，否则需要把访问地址对应的整个row 都加载到row buffer 当中（情况B）。当然，如果row buffer 之前缓存了其他row 的内容，还需要先换出row buffer 的内容再加载新的row（情况C）。A、B、C 对应的三种情况，访问速度依次递减（情况A 最快，情况C 最慢）。这样，通过时间上的差异，攻击者就可以了解当前访问的内存地址是否在row buffer 里面，以及是否有被换出。文章[25] 在侧信道攻击过程中用到了基于DRAM 的侧信道信息。另外文章[23] 介绍了更多基于DRAM 的攻击细节，不过该文章不是在SGX 环境下的攻击。

![](https://github.com/XGWang0/wiki/raw/master/_images/meltdown-spectre_2.jpg)

基于DRAM 的侧信道攻击有一些不足[28]。第一，enclave 使用的内存通常都在缓存里面，只有少部分需要从DRAM 里面去取。第二，DRAM的精度不够。例如，一个页面（4KB) 通常分布在4 个DRAM row 上面。这样，基于DRAM 的侧信道攻击的精度就是1KB。仅仅比基于页表的侧信道攻击好一些，远远不及基于cache 的侧信道攻击的精度。第三，DRAM里面存在很难避免的噪音干扰，因为一个DRAM row 被很多页面使用，同时同一个bank 不同row的数据读取也会对时间测量造成干扰，使得误报时常发生。

However, we observed that out-of-order memorylookups influence the cache, which in turn can be detectedthrough the cache side channel. As a result, anattacker can dump the entire kernel memory by readingprivileged memory in an out-of-order execution stream,and transmit the data from this elusive state via a microarchitecturalcovert channel (e.g., Flush+Reload) tothe outside world. On the receiving end of the covertchannel, the register value is reconstructed. Hence, onthe microarchitectural level (e.g., the actual hardware implementation),there is an exploitable security problem.

Meltdown breaks all security assumptions given by theCPU’s memory isolation capabilities. We evaluated theattack on modern desktop machines and laptops, as wellas servers in the cloud. Meltdown allows an unprivilegedprocess to read data mapped in the kernel address space,including the entire physical memory on Linux and OSX, and a large fraction of the physical memory on Windows.This may include physical memory of other processes,the kernel, and in case of kernel-sharing sandboxsolutions (e.g., Docker, LXC) or Xen in paravirtualizationmode, memory of the kernel (or hypervisor),and other co-located instances. While the performanceheavily depends on the specific machine, e.g., processorspeed, TLB and cache sizes, and DRAM speed, we candump kernel and physical memory with up to 503 KB/s.Hence, an enormous number of systems are affected.




## Spectre

Spectre breaks the isolation between `different applications`. It allows an attacker to trick error-free programs, which follow best practices, into leaking their secrets. In fact, the safety checks of said best practices actually increase the attack surface and may make applications more susceptible to Spectre
