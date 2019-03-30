---
layout: post
title:  "PCI 配置空间"
categories: IO
tags:  PCI
author: Root Wang
---

* content
{:toc}

### PCI设备空间

PCI设备(PCI device)都有一个配置空间，大小为256字节，实际上是一组连续的寄存器，位于设备上。其中头部64字节是PCI标准规定的，格式如下：

pic1

剩余的部分是PCI设备自定义的。

PCI配置空间头部有6个BAR(Base Address Registers)，BAR记录了设备所需要的地址空间的类型(memory space或者I/O space)，基址以及其他属性。BAR的格式如下：

pci2

可以看出，设备可以申请两类地址空间，memory space和I/O space，它们用BAR的最后一位区别开来。

#### 内存地址空间 I/O地址空间
说到地址空间，计算机系统中，除了我们常说的memory address(包括逻辑地址、虚拟地址(线性地址)、CPU地址(物理地址))，还有I/O address，这是为了访问I/O设备(`主要是设备中的寄存器`)而设立的，大部分体系结构中，memory address和I/O address都是分别编址的，且使用不同的寻址指令，构成了两套地址空间，也有少数体系结构将memory address和I/O address统一编址(如ARM)。

有两套地址空间并不意味着计算机系统中需要两套地址总线，实际上，memory address和I/O address是共用一套地址总线，但通过控制总线上的信号区别当前地址总线上的地址是memory address还是I/O address。北桥芯片(Northbridge，Intel称其Memory Controller Hub，MCH)负责地址的路由工作，它内部有一张address map，记录了memory address，I/O address的映射信息，一个典型的address map如图：

pic3

我们来看北桥是如何进行地址路由的。根据控制总线上的信号，北桥首先可以识别地址属于memory space还是I/O space，然后分别做处理。

比如若是memory space，则根据address map找出目标设备(DRAM或Memory Mapped I/O)，若是DRAM或VGA，则转换地址然后发送给内存控制器或VGA控制器，若是其它I/O设备，则发送给南桥(Southbridge，Intel称其I/O Controller Hub，ICH)，南桥负责解析出目标设备的bus, device, function号，并发送信息给它。

PCI设备会向计算机系统申请很多资源，比如memory space, I/O space, 中断请求号等，相当于在计算机系统中占位，使得计算机系统认识自己。

PCI设备可以通过两种方式将自己的I/O存储器(Registers/RAM/ROM)暴露给CPU：

#### 在memory space申请地址空间，或者在I/O space申请地址空间。

这样，PCI设备的I/O存储器就分别被映射到CPU-relative memory space和CPU-relative I/O space，使得驱动以及操作系统得以正常访问PCI设备。对于没有独立I/O space的体系结构(如ARM)，memory space和I/O space是统一编址的，也就是说memory space与I/O space等价了，这时，即使PCI设备在BAR表明了要申请I/O space，实际上也是分配在memory space的，所以驱动无法使用I/O端口指令访问I/O，只能使用访存指令。在Windows驱动开发中，PCM_PARTIAL_RESOURCE_DESCRIPTOR记录了为PCI设备分配的硬件资源，可能有CmResourceTypePort, CmResourceTypeMemory等，后者表示一段memory地址空间，顾名思义，是通过memory space访问的，前者表示一段I/O地址空间，但其flag有CM_RESOURCE_PORT_MEMORY和CM_RESOURCE_PORT_IO两种，分别表示通过memory space访问以及通过I/O space访问，这就是PCI请求与实际分配的差异，在x86下，CmResourceTypePort的flag都是CM_RESOURCE_PORT_IO，即表明PCI设备请求的是I/O地址空间，分配的也是I/O地址空间，而在ARM或Alpha等下，flag是CM_RESOURCE_PORT_MEMORY，表明即使PCI请求的I/O地址空间，但分配在了memory space，我们需要通过memory space访问I/O设备(通过MmMapIoSpace映射物理地址空间到虚拟地址空间，当然，是内核的虚拟地址空间，这样驱动就可以正常访问设备了)。

为了为PCI设备分配CPU-relative space，计算机系统需要知道其所申请的地址空间的类型、基址等，这些信息记录在设备的BAR中，每个PCI配置空间拥有6个BAR，因此每个PCI设备最多能映射6段地址空间(实际很多设备用不了这么多)。PCI配置空间的初始值是由厂商预设在设备中的，于是设备需要哪些地址空间都是其自己定的，可能造成不同的PCI设备所映射的地址空间冲突，因此在PCI设备枚举(也叫总线枚举，由BIOS或者OS在启动时完成)的过程中，会重新为其分配地址空间，然后写入PCI配置空间中。

通过memory space访问设备I/O的方式称为memory mapped I/O，即MMIO，这种情况下，CPU直接使用普通访存指令即可访问设备I/O。

通过I/O space访问设备I/O的方式称为port I/O，或者port mapped I/O，这种情况下CPU需要使用专门的I/O指令如IN/OUT访问I/O端口。

常见的MMIO例子有，VGA card将framebuffer映射到memory space，NIC将自己的片上缓冲映射到memory space，实际上，最典型的MMIO应该是DRAM，它将自己的存储空间映射到memory space，是占用CPU地址空间最多的“设备”
