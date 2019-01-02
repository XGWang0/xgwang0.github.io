---
layout: post
title:  "Linux Disk IO 调度器"
categories: disk
tags:  io-scheduler
author: Root Wang
---

* content
{:toc}

### I/O schedulers typically use the following techniques
* Request Merging : Merge 相邻的BIO请求，以较少磁盘巡道时间和提升IO系统调用。[Adjacent requests are merged to reduce disk seeking and to increase the size of the I/O syscalls (usually resulting in higher performance).]
* Elevator : 所有BIO请求（meger之后的）被顺序的排放根据磁头的运动方向（使磁头按同一方向运动，较少磁头来回寻道的开销）。[Requests are ordered on the basis of physical location on the disk so that seeks are in one direction as much as possible. This technique is sometimes referred to as “sorting.”]
* Prioritization : BIO请求被以优先级的方式排列（详细的排列需要IO scheduler 算法的参与）。[Requests are prioritized in some way. The details of the ordering are up to the I/O scheduler.]

**These techniques and others are combined to create an I/O scheduler with a few goals, with three of the top goals being:**

* Minimize disk seeks
* Ensure optimum disk performance
* Provide fairness among I/O requests

**The techniques used by I/O schedulers as they apply to `SSDs` are a bit different. **
1. SSDs are not `spinning media`, so _merging requests and ordering them might not have much of an effect on I/O_. Instead, _I/O requests to the same block can be merged_, 
2. small I/O writes can either be merged or adjusted to reduce write amplification (i.e., the need for more physical space than the logical data would imply because of the way write operations take place on SSDs).


### Linux I/O Schedulers

* Completely Fair Queuing (CFQ)
* Deadline
* NOOP
* Anticipatory

#### NOOP
The NOOP I/O scheduler is fairly simple. All incoming I/O requests for all processes running on the system, regardless of the I/O request (e.g., read, write, lseek, etc.), ***go into a simple first in, first out (FIFO) queue.*** The scheduler also ***does request merging by taking adjacent requests and merging them into a single request to reduce seek time and improve throughput***. NOOP assumes that some other device will optimize I/O performance, such as an external `RAID controller` or a `SAN controller`.

Potentially, the NOOP scheduler ***could work well with storage devices that don’t have a mechanical component*** (i.e., a drive head) to read data, because it does not make any attempts to reduce seek time beyond simple request merging (which helps throughput). Therefore, storage devices such as `flash drives`, `SSD drives`, `USB sticks`, and the like that have very little seek time could benefit from a NOOP I/O scheduler.


#### Anticipatory
The anticipatory I/O scheduler was the default scheduler a long time ago (in kernel years). As the name implies, it anticipates subsequent block requests and implements request merging, a one-way elevator (a simple elevator), and read and write request batching. After the scheduler services an I/O request, it anticipates that the next request will be for the subsequent block. If the request comes, the disk head is in the correct location, and the request is serviced very quickly. This approach does add a little latency to the system because it pauses slightly to see if the next request is for the subsequent block. However, this latency is possibly outweighed by the increased performance for neighboring requests.

Anticipatory 会批量处理read/write请求，当有read请求到来，Anticipatory 会处理此请求，并且暂停一段时间（a few milliseconds），猜测下一次的相邻BLOCK的read请求马上回来。 如果下一个相邻的read请求来了，Anticipatory 将会得到非常大的性能提升。所以此sheduler对于特定的workload将会取得非常大的好处。

Putting on your storage expert hat, you can see that the Anticipatory scheduler works really well for certain workloads. For example, one study observed that the Apache web server could achieve up to 71% more throughput using the anticipatory I/O scheduler. On the other hand, the anticipatory scheduler has been observed to result in a slowdown on a database run.


#### Deadline
The deadline I/O scheduler was written by well-known kernel developer Jens Axboe. The fundamental principle is to guarantee a start time for servicing an I/O request by combining request merging, a one-way elevator, and a deadline on all requests (hence the name). It maintains two deadline queues in addition to the sorted queues for reads and writes. The deadline queues are sorted by their deadline times (time to expiration), with shorter times moving to the head of the queue. The queues are sorted according to their sector number (the elevator approach).
Deadline 保证每个merge后的REQUIRE开始执行时间通过单路的电梯模式（保证request按照磁头行进的方向排序）和超时时间的设置。
其使用两个Deadline QUEUE和sorted QUEUE来存储read/write. Deadline QUEUE保证越是有较短的deadline，越会排在QUEUE前面，并且SORTED QUEDUE保证拥有相同sector IO REQUEST会在相邻的位置。

By moving the I/O requests that have been in the queues the longest (the same as having the shortest deadline time), they will be executed before others, which guarantees that I/O requests won’t “starve” for various reasons, resulting in a very long time to execute the request.

拥有越短的deadline时间的IO REQUEST将会被优先执行

A deadline scheduler really helps with distant reads (i.e., fairly far out on the disk or with a large sector number). Read I/O requests sometimes block applications because they have to be executed while the application waits. On the other hand, because writes are cached, execution can quickly return to the application – unless you have turned off the cache in the interest of making sure the data reaches the disk in the event of a power loss, in which case, writes would behave like read requests. Even worse, distant reads would be serviced very slowly because they are constantly moved to the back of the queue as requests for closer parts of the disk are serviced first. However, a deadline I/O scheduler makes sure that all I/O requests are serviced, even the distant read requests.

Diving into the scheduler a bit more, the concepts are surprisingly straightforward. The scheduler decides on the next request by first deciding which queue to use. It gives a higher priority to reads because, as mentioned, applications usually block on read requests. Next, it checks the first request to see if it has expired. If so, it is executed immediately; otherwise, the scheduler serves a batch of requests from the sorted queue.

处理流程：
* Deadline 会倾向于多读少写，毕竟当应用执行读的时候，需要block应用并定带读取的内容。 
* 检查deadline queue，判断第一个IO REQUEST是否过期， 如果是将有限处理它
* 否则，将会按照sorted queue的顺序处理IO REQUEST

The deadline scheduler is very useful for some applications. In particular, **real-time systems use the deadline scheduler** because, in most cases, it keeps latency low (all requests are serviced within a short time frame). It has also been suggested that it works well for database systems that have TCQ-aware disks.

### CFQ
The completely fair queue (CFQ) I/O scheduler, is the current default scheduler in the Linux kernel. It uses both request merging and elevators and is a bit more complex that the NOOP or deadline schedulers. CFQ synchronously puts requests from processes into a number of per-process queues then allocates time slices for each of the queues to access the disk. The details of the length of the time slice and the number of requests a queue is allowed to submit are all dependent on the I/O priority of the given process. Asynchronous requests for all processes are batched together into fewer queues with one per priority.

CFQ会同步地从进程中存储IO REQUEST到属于此进程的多个QUEUE中，并且赋予时间片段。 具体的时间片段产段取决于进程的IO优先级。
异步请求会批量的放到很少的几个QUEUE中。

Jens Axboe is the original author of the CFQ scheduler, incorporating elevator_linus, which adds features to prevent starvation for worst case situations, as could happen with distant reads. An article by Axboe has a good discussion on the design of the CFQ I/O scheduler (and others) and the intricacies of scheduler design.

CFQ gives all users (processes) of a particular device (storage) about the same number of I/O requests over a particular time interval, which can help multiuser systems see that all users get about the same level of responsiveness. Moreover, CFQ achieves some of the good throughput characteristics of the anticipatory scheduler because it allows a process queue to have some idle time at the end of a synchronous I/O request, creating some anticipatory time for I/O that might be close to the request just serviced.
