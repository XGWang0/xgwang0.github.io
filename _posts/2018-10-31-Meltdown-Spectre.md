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

#### Software Guard eXtensions (SGX):
Intel Software Guard eXtensions (SGX) 是现代Intel处理器的一个特征，允许应用创建enclave，enclave可以理解为一个数据运行的安全环境，我们可以称它为“小黑匣”。SGX对于软件的保护并不是识别或者隔离系统中出现的恶意软件，而是将合法软件对于敏感数据（如加密密钥、密码、用户数据等）的操作封装在一个“小黑匣”中，使得恶意软件无法对这些数据进行访问。

enclave : 用户空间运行环境
sid-channel attacks : 

威胁模型:
俄亥俄州立大学的六位科学家组成的研究小组揭示了一种新型的攻击技术。研究小组表示，被命名为“SgxSpectre”的新型攻击技术可以从英特尔SGX建立的“小黑匣”中提取数据。

研究小组表示，SgxSpectre的工作原理基于软件库中的特定代码模式，这种模式允许开发人员将SGX支持添加到他们的应用程序中。这些脆弱的开发套件包括英特尔SGX SDK、Rust-SGX SDK和Graphene-SGX SDK。

攻击者可以利用这些开发套件在SGX中引入的重复代码执行模式来观察缓存大小的细微变化，进而推断出“小黑匣”中存储的敏感数据。这属于一种典型的“边信道攻击（side-channel attack，SCA） ”，并且非常有效。

研究小组强调，SgxSpectre攻击可以完全破坏SGX的 “小黑匣”的机密性。由于开发套件运行时库中存在易受攻击的代码模式，因此任何使用英特尔官方SGXSDK开发的代码都将受到SgxSpectre攻击的影响，这与“小黑匣”的实施无关。



侧信道攻击主要目标是攻击enclave数据的机密性（confidentiality）。攻击者来自non-enclave 部分，包括应用程序和系统软件。系统软件包括OS，hypervisor，SMM，BIOS 等特权级软件。

侧信道攻击一般假设攻击者知道enclave 初始化时候的代码和数据，并且知道内存布局。内存布局包括虚拟地址，物理地址以及他们之间的映射关系。有些侧信道攻击假设攻击者知道enclave 的输入数据，并且可以反复触发enclave，进行多次观察记录。侧信道攻击还假设攻击者知道运行enclave 平台的硬件配置、特性和性能，比如CPU，TLB，cache，DRAM，页表，中断以及异常等各种系统底层机制。

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


In this paper, we analyze the security implications of suchincorrect speculative execution. We present a class of microarchitecturalattacks which we call Spectre attacks. At a highlevel, Spectre attacks trick the processor into speculativelyexecuting instruction sequences that should not have beenexecuted under correct program execution. As the effects ofthese instructions on the nominal CPU state are eventually reverted, we call them transient instructions. By influencingwhich transient instructions are speculatively executed, we areable to leak information from within the victim’s memoryaddress space.
We empirically demonstrate the feasibility of Spectre attacksby exploiting transient instruction sequences to leak informationacross security domains both from unprivileged nativecode, as well as from portable JavaScript code

Attacks using Native Code. As a proof-of-concept, wecreate a simple victim program that contains secret data withinits memory address space. Next, we search the compiledvictim binary and the operating system’s shared libraries forinstruction sequences that can be used to leak informationfrom the victim’s address space. Finally, we write an attackerprogram that exploits the CPU’s speculative execution featureto execute the previously-found sequences as transient instructions.Using this technique, we are able to read memory fromthe victim’s address space, including the secrets stored withinit.
Attacks using JavaScript and eBPF. In addition to violatingprocess isolation boundaries using native code, Spectre attackscan also be used to violate sandboxing, e.g., by mountingthem via portable JavaScript code. Empirically demonstratingthis, we show a JavaScript program that successfully readsdata from the address space of the browser process runningit. In addition, we demonstrate attacks leveraging the eBPFinterpreter and JIT in Linux

At a high level, Spectre attacks violate memory isolationboundaries by combining speculative execution withdata exfiltration via microarchitectural covert channels. Morespecifically, to mount a Spectre attack, an attacker starts bylocating or introducing a sequence of instructions within theprocess address space which, when executed, acts as a covertchannel transmitter that leaks the victim’s memory or registercontents. The attacker then tricks the CPU into speculativelyand erroneously executing this instruction sequence, therebyleaking the victim’s information over the covert channel.Finally, the attacker retrieves the victim’s information overthe covert channel. While the changes to the nominal CPUstate resulting from this erroneous speculative execution areeventually reverted, previously leaked information or changesto other microarchitectural states of the CPU, e.g., cachecontents, can survive nominal state reversion.The above description of Spectre attacks is general, andneeds to be concretely instantiated with a way to induceerroneous speculative execution as well as with a microarchitecturalcovert channel. While many choices are possiblefor the covert channel component, the implementations describedin this work use cache-based covert channels [64],i.e., Flush+Reload [74] and Evict+Reload [25, 45].We now proceed to describe our techniques for inducingand influencing erroneous speculative execution.


### Variant 1: 

Exploiting Conditional Branches. In this variantof Spectre attacks, the attacker mistrains the CPU’s branchpredictor into mispredicting the direction of a branch, causingthe CPU to temporarily violate program semantics by executingcode that would not have been executed otherwise. As weshow, this incorrect speculative execution allows an attacker toread secret information stored in the program’s address space.Indeed, consider the following code example:
```c
if (x < array1_size)
y = array2[array1[x] * 4096];
```
In the example above, assume that the variable x containsattacker-controlled data. To ensure the validity of the memoryaccess to array1, the above code contains an if statementwhose purpose is to verify that the value of x is within alegal range. We show how an attacker can bypass this ifstatement, thereby reading potentially secret data from theprocess’s address space.
First, during an initial mistraining phase, the attacker invokesthe above code with valid inputs, thereby trainingthe branch predictor to expect that the if will be true.Next, during the exploit phase, the attacker invokes thecode with a value of x outside the bounds of array1.Rather than waiting for determination of the branch result,the CPU guesses that the bounds check will be trueand already speculatively executes instructions that evaluatearray2[array1[x]*4096] using the malicious x. Notethat the read from array2 loads data into the cache at anaddress that is dependent on array1[x] using the maliciousx, scaled so that accesses go to different cache lines and toavoid hardware prefetching effects.When the result of the bounds check is eventually determined,the CPU discovers its error and reverts anychanges made to its nominal microarchitectural state. However,changes made to the cache state are not reverted, so theattacker can analyze the cache contents and find the value ofthe potentially secret byte retrieved in the out-of-bounds readfrom the victim’s memory

### Variant 2: Exploiting Indirect Branches. 
Drawing fromreturn-oriented programming (ROP) [63], in this variant theattacker chooses a gadget from the victim’s address spaceand influences the victim to speculatively execute the gadget.Unlike ROP, the attacker does not rely on a vulnerability inthe victim code. Instead, the attacker trains the Branch TargetBuffer (BTB) to mispredict a branch from an indirect branchinstruction to the address of the gadget, resulting in speculativeexecution of the gadget. As before, while the effects ofincorrect speculative execution on the CPU’s nominal state areeventually reverted, their effects on the cache are not, therebyallowing the gadget to leak sensitive information via a cacheside channel. We empirically demonstrate this, and show howcareful gadget selection allows this method to read arbitrarymemory from the victim.
To mistrain the BTB, the attacker finds the virtual addressof the gadget in the victim’s address space, then performsindirect branches to this address. This training is done fromthe attacker’s address space. It does not matter what resides atthe gadget address in the attacker’s address space; all that isrequired is that the attacker’s virtual addresses during trainingmatch (or alias to) those of the victim. In fact, as long as theattacker handles exceptions, the attack can work even if thereis no code mapped at the virtual address of the gadget in theattacker’s address space.Other Variants. Further attacks can be designed by varyingboth the method of achieving speculative execution andthe method used to leak the information. Examples includemistraining return instructions, leaking information via timingvariations, and contention on arithmetic units

###  Targeted Hardware and Current Status
Hardware. We have empirically verified the vulnerabilityof several Intel processors to Spectre attacks, includingIvy Bridge, Haswell, Broadwell, Skylake, and Kaby Lakeprocessors. We have also verified the attack’s applicabilityto AMD Ryzen CPUs. Finally, we have also successfullymounted Spectre attacks on several ARM-based Samsung andQualcomm processors found in popular mobile phones.Current Status. Using the practice of responsible disclosure,disjoint groups of authors of this paper provided preliminaryversions of our results to partially overlapping groups of CPUvendors and other affected companies. In coordination withindustry, the authors also participated in an embargo of theresults. The Spectre family of attacks is documented underCVE-2017-5753 and CVE-2017-5715.

### Meltdown VS Spectre
Meltdown [47] is a related microarchitectural attack whichexploits out-of-order execution to leak kernel memory. Meltdownis distinct from Spectre attacks in two main ways. First,unlike Spectre, Meltdown does not use branch prediction.Instead, it relies on the observation that when an instructioncauses a trap, following instructions are executed out-oforderbefore being terminated. Second, Meltdown exploits avulnerability specific to many Intel and some ARM processorswhich allows certain speculatively executed instructions tobypass memory protection. Combining these issues, Meltdownaccesses kernel memory from user space. This access causes atrap, but before the trap is issued, the instructions that followthe access leak the contents of the accessed memory througha cache covert channel.In contrast, Spectre attacks work on a wider range of processors,including most AMD and ARM processors. Furthermore,the KAISER mechanism [29], which has been widely appliedas a mitigation to the Meltdown attack, does not protect againstSpectre.


### Spectre v1 Mitigation:
Spectre v1 mitigation 目前基于软件实现去屏蔽speculative执行路径，此方案不需要更改任何硬件。 但是目前无法指导此问题是否对xen pv产生影响。

### Spectre v2 Mitigation:
Spectre v2 mitigation 需要更新microcode去得以解决， 目前增加了Indirect Branch Restricted Speculation (IBRS), Indirect Branch Prediction Barrier (IBPB), and Single Thread Indirect Branch Predictors (STIBP) to CPUID through new MSRs (Model-Specific Register)。此MSRs 以SPEC_CTRL MSR命名以方便澄清。在这些CPU（Skylake -vs- IvyBridge -vs- Nehalem）上， IBRS and IBPB 存在性能下降的问题。 去解决性能问题，要使用急于`软件`的Mitigation（such as retpolines）并且软件的Mitigation不需要`硬件的feature支持`.

对于某些情况，基于软件的Mitigation可能也会导致性能下降。所以大部分的spectre V2 Mitigation通过硬件，软件组合的方式去解决Spectre V2和性能的问题。

### Spectre v3 Mitigation:

Spectre v3 Mitigation 只需要mircocode 更新即可。

### Spectre v4 Mitigation:

Spectre V4 Mitigation 需要disable 处理器“Memory Disambiguation” 功能， 可以通过关闭Speculative Store Bypass Disable (SSBD)flag去解决此问题;也可以通关软件方式，即在通过强制使用prctl() system call (using PR_SET_SECCOMP arg), or through seccomp filtering (SECure COMputing mode)去解决。

### Meltdown：

Meltdown 只影响intel CPUs， 其解决方法是通过调用 Kernel Page Table Isolation (KPTI) 在bare machine 和 KVM or Xen Page Table Isolation (XPTI) 在xen环境下，当代码执行期间，此方法会从用户空间unmap 内核地址空间。 KPTI/XPTI 会有较明显的性能下降。 通过使用Process-Context Identifiers (PCID) and Invalidate Process-Context Identifiers (INVPCID) 硬件功能可以有效的减少性能下降。 目前PCID在xen环境中无法被支持 (PCID support in XPTI is expected in the near future.)
note: Meltdown 不会被在guest内部使用去攻击host或者其他guest.

### L1TF (L1 Terminal Fault)
L1TF是speculative execution side channel cache timing漏洞，其影响intel的微架构，并且支持SGX（side-channel attack）。其主要是访问L1（内存池，保存处理器接下来要执行的数据）。 L1TF也会影响虚拟机，它会绕过Extended Page Table (EPT) 保护机制而获取其他程序的信息。Mitigation需要增加micorcode（硬件） 的L1Flush能力，允许主动刷新L1; 在软件方面可以使用Core Scheduling去减少漏洞发生; 在较老的机器上，推荐使用Hyper Threading. L1TF会影响整体性能。


| |Software-based Factors | Hardware-based Factors|
|Spectre v1 | kernel/hypervisor |---- |
|Spectre v2 | kernel/hypervisor (retpolines, etc.) | Updated microcode (IBRS, IBPB, STIBP) |
|Spectre v3 | ---- |  Updated microcode |
|Spectre v4 | kernel/hypervisor （prctl(), seccomp) | updated microcode (SSBD) |
|Meltdown   | KPTI, XPTI | PCID, INVPCID |
|L1TF       |Core Scheduling | Updated microcode (L1D_Flush) Disable Sibling Thread |


### Enable/Disable Mitigation

|           | Disable(SoftWare) | Disable (HardWare) | Enable (SoftWare) | Enable (HardWare) |
|Spectre v1 | nospectre_v2 | nospec (SLE12 and earlier)/nospectre_v2 |  Default | Default|
|Spectre v2 | nospectre_v2 | nospec (SLE12 and earlier)/nospectre_v2 | spectre_v2=on/auto/retpoline/retpoline,generic/retpoline,amd | spectre_v2=ibrs (Only for SLE15) |
|Spectre v3 |  nospectre_v2 | nospec (SLE12 and earlier)/nospectre_v2 | Default | Default |
|Spectre v4 | ucode + nospec_store_bypass_disable/spec_store_bypass_disable=off | ucode + nospec_store_bypass_disable/spec_store_bypass_disable=off/seccomp/prctl | spec_store_bypass_disable=on/auto | -- |
|Meltdown   | nopti | nopti/pti=off | pti=on/auto | pti=on/auto|
|L1TF       | on in file /sys/devices/system/cpu/smt/control | -- |nosmt/nosmt=force/(off/forceoff/notsupported in control file) | nosmt/nosmt=force/(off/forceoff/notsupported in control file) | 

*Details for each vulnerability:*

#### Spectre v2 mitigation (for x86_64 environments)

*.Hardware-based Spectre v2 mitigation can be completely disabled using the kernel parameter nospec. (SLE12 and earlier)
*.ALL Spectre v2 mitigation (IBRS, IBPB, retpolines, etc.) can be completely disabled using the nospectre_v2 kernel commandline
parameter.
*.Software-based Spectre v2 can also be tuned using the "spectre_v2" kernel commandline parameter:

`spectre_v2`=<VALUE>
<VALUE> :
**.on - unconditionally enable the mitigation
**.off - unconditionally disable the mitigation (same as nospectre_v2)
**.auto- kernel detects whether your CPU model is vulnerable (default)

Selecting on will, and auto may, choose a mitigation method at run time according to the CPU, the available microcode, the setting of the CONFIG_RETPOLINE configuration option, and the compiler with which the kernel was built.

Specific mitigation implementations can also be selected manually:
**.retpoline - replace indirect branches
**.retpoline,generic - google’s original retpoline
**.retpoline,amd - AMD-specific minimal thunk
**.ibrs - Force IBRS support (SLE15 only)

### Spectre v4 mitigation (for x86_64 environments)
*.Spectre v4 mitigation requires disabling the "Memory Disambiguation" feature of the processor. This can be done system-wide, or selectively for individual processes.
*.Intel x86 systems require updated CPU microcode to allow disabling "Memory Disambiguation".
*.Spectre v4 mitigation can be completely disabled using the kernel parameter nospec_store_bypass_disable.
*.Spectre v4 mitigation is enabled/disabled/tuned using the spec_store_bypass_disable kernel commandline parameter:
`spec_store_bypass_disable`=<VALUE>

<VALUE> :
*.auto - mitigation is enabled by default when needed, prctl() is enabled for per-process selection and seccomp users are also enabled.
*.on - unconditionally enable the mitigation system-wide.
*.off - unconditionally disable the mitigation (same as nospec_store_bypass_disable).
*.seccomp - system-wide mitigation is disabled, but can be enabled by user programs through the prctl() system call, and is default enabled for applications using seccomp filtering (such as openssh, vsftpd and firefox and chromium).
*.prctl - system-wide mitigation is disabled, but can be enabled by user programs through the prctl() system call.

### Mitigations in KVM Environments

KVM hosts operate as normal, bare-metal machines and inherit both software and hardware based mitigation through support for these features in the hardware and the normal SUSE Linux kernel.

KVM guests can utilize software-based mitigation if the operating system
within the guest supports this approach. (SUSE Linux guests have such
mitigation in recently released kernels. Third party operating system
mitigation must be verified with the third party vendor.) Hardware-based
mitigation within a KVM guest depends on the hardware features (e.g.
SPEC_CTRL for Spectre v2, and (for decreased performance degradation)
PCID/INVPCID for Meltdown) being available on the host, and being
presented to the guest operating system. Passing `SPEC_CTRL`, `PCID` and
`INVPCID` CPU flags to a KVM guest is performed by `qemu`, and based on
the CPU configuration `qemu` presents to the guest. Features available
with specific CPU models can be verified through the `libvirt-libs`
provided file `/usr/share/libvirt/cpu_map.xml`. (NOTE - a QEMU update
may be required to pass `SPEC_CTRL` to KVM guests.)


#### KVM Host/Guest Vulnerabilities

he following table describes which mitigations are potentially required
to secure specific attack vectors on KVM hosts and guests:

[cols="h,3*",options="header"]
|===
|
|Bare Metal/KVM Host +
(within machine)
|KVM Guest to Host/Guests +
(across machines)
|KVM Guest +
(within machine)

|Spectre v1
|Required
|Required
|Required

|Spectre v2
|Required
|Required
|Required

|Spectre v3a
|Required
|Required
|Required

|Spectre v4
|Required
|Required
|Required

|Meltdown
|Required
|Not Required
|Required

|L1TF
|Required
|Required
|Required
|===

* "within machine" - Attacks that are confined to memory within
a single physical or virtual machine.

* "across machines" - Attacks that are launched from one virtual machine,
and access memory assigned to the hypervisor or another virtual machine.



