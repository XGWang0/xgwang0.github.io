---
layout: post
title:  "Process Thread, LWP(light weight process)"
categories: hive
tags:  process thread lwp
author: Root Wang
---

* content
{:toc}

`Thread Local Storage`，线程本地存储，大神Ulrich Drepper有篇PDF文档是讲TLS的，我曾经努力过三次尝试搞清楚TLS的原理，均没有彻底搞清楚。这一次是第三次，我沉浸glibc的源码和kernel的源码中，做了一些实验，也有所得。对Linux的线程有了进一步的理解。
   线程是有栈的，我们知道，普通的一个进程，它的栈空间是8M，我们可以通过ulmit -a查看：

>stack size (kbytes, -s) 8192

   线程也不例外，线程也是需要栈空间的这句话是废话，呵呵。对于属于同一个进程（或者说是线程组）的多个线程他们是共享一份虚拟内存地址的，如下图所示。这也就决定了，你不能无限制创建线，因为纵然你什么都不做，每个线程默认耗费8M的空间（事实上还不止，还有管理结构，后面陈述）。Ulrich Drepper大神有篇文章《Thread numbers and stacks》，分析了线程栈空间方面的计算。如果我们真的需要很多个线程的话，幸好我们还是可以做一些事情。我们可以通过pthread_attr_setstacksize,设定好stack size属性然后在pthread_create.

```c
1.int pthread_attr_setstacksize(pthread_attr_t *attr, size_t stacksize);
2. 
3.int pthread_create(pthread_t *thread, const pthread_attr_t *attr,
4.void *(*start_routine) (void *), void *arg);
```

![](https://github.com/XGWang0/wiki/raw/master/_images/process_thread_threadgroup_1.png)

线程栈如上图所示，共享进程（或者称之为线程组）的虚拟地址空间。既然多个线程聚集在一起，我怎么知道我要操作的那个线程栈的地址呢。要解决这个问题，必须要领会线程和进程以及线程组的概念。我不想写一堆片汤话，下面我运行我的测试程序，然后结合现象分析原因：

```c
#include <stdio.h>
#include <pthread.h>
#include <sys/syscall.h>
#include <assert.h>

#define gettid() syscall(__NR_gettid)

pthread_key_t key;
__thread int count = 2222;
__thread unsigned long long count2 ;
static __thread int count3;
void echomsg(int t)
{
    printf("destructor excuted in thread %x,param=%x\n",pthread_self(),t);
}

void * child1(void *arg)
{
    int b;
    int tid=pthread_self();

    printf("I am the child1 pthread_self return %p gettid return %d\n",tid,gettid());

    char* key_content = malloc(8);
    if(key_content != NULL)
    {
        strcpy(key_content,"ACACACA");
    }
    pthread_setspecific(key,(void *)key_content);
    
    count=666666;
    count2=1023;
    count3=2048;
    printf("I am child1 , tid=%x ,count (%p) = %10d,count2(%p) = %10llu,count3(%p) = %6d\n",tid,&count,count,&count2,count2,&count3,count3);
    asm volatile("movl %%gs:0, %0;"
            :"=r"(b) /* output */ 
            );

    printf("I am child1 , GS address %x\n",b);
    
    sleep(2);
    printf("thread %x returns %x\n",tid,pthread_getspecific(key));
    sleep(50);
}

void * child2(void *arg)
{
    int b;
    int tid=pthread_self();

    printf("I am the child2 pthread_self return %p gettid return %d\n",tid,gettid());

    char* key_content = malloc(8);
    if(key_content != NULL)
    {
        strcpy(key_content,"ABCDEFG");
    }
    pthread_setspecific(key,(void *)key_content);
    count=88888888;
    count2=1024;
    count3=2047;
    printf("I am child2 , tid=%x ,count (%p) = %10d,count2(%p) = %10llu,count3(%p) = %6d\n",tid,&count,count,&count2,count2,&count3,count3);
    
    
    asm volatile("movl %%gs:0, %0;"
            :"=r"(b) /* output */ 
            );

    printf("I am child2 , GS address %x\n",b);
    
    sleep(1);
    printf("thread %x returns %x\n",tid,pthread_getspecific(key));
    sleep(50);
}


int main(void)
{
    int b;
    pthread_t tid1,tid2;
    printf("hello\n");

    
    pthread_key_create(&key,echomsg);

    asm volatile("movl %%gs:0, %0;"
            :"=r"(b) /* output */ 
            );

    printf("I am the main , GS address %x\n",b);
    
    pthread_create(&tid1,NULL,child1,NULL);
    pthread_create(&tid2,NULL,child2,NULL);

    printf("pthread_create tid1 = %p\n",tid1);
    printf("pthread_create tid2 = %p\n",tid2);

    sleep(60);
    pthread_key_delete(key);
    printf("main thread exit\n");
    return 0;
} 
```

这是一个比较综合的程序，因为我下面要多次从不同的侧面分析。对于现在，我们要展示的是进程 线程 线程组的关系。在一个终端运行编译出来的test2程序，显示的信息如下：

![](https://github.com/XGWang0/wiki/raw/master/_images/process_thread_threadgroup_2.png)

另一个终端看ps信息，ps显示的信息如下：

![](https://github.com/XGWang0/wiki/raw/master/_images/process_thread_threadgroup_3.png)

  直接ps，是看不到我们创建的线程的。只有3658一个进程。当我们采用ps -eLf的时候，我们看到了三个线程3658/3659/3660，或者称之为轻量级进程（LWP）。Linux到底是怎么看待这三者的关系的呢：
    Linux下多线程程序，一般都是有一个主进程通过调用pthread_create创建了一个或者多个子线程，如同我们的程序，主进程在main中创建了两个子进程。那么Linux到底是怎么看待这些事情的呢？

```c
    pid_t pid;
    pid_t tgid; 
     ...
    struct task_struct *group_leader; /* threadgroup leader */ 
```

上面三个变量是进程描述符的三个成员变量。pid字面意思是process id，其实叫thread id会更合适。tgid 字面含义是thread group ID。对于存在多个线程的程序而言，每个线程都有自己的pid，没错pid，如同我们例子中的3658/3659/3660,但是都有个共同的线程组ID （TGID）：3658 。
   好吧，我们再重新说一遍，对于普通进程而言，我们可以称之为只有一个LWP的线程组，pid是它自己的pid，tgid还是它自己，线程组里面只有他自己一个光杆司令，自然group_leader也是它自己。但是多线程的进程（线程组更恰当）则不然。开天辟地的main函数所在的进程会有自己的PID，也会有也TGID，group_leader,都是他自己。注意，它自己也是LWP。后面他使用ptherad_create创建了2个线程，或者LWP，这两个新创建的线程会有自己的PID，但是TGID会沿用创建自己的那个进程的TGID，group_leader也会尊创建自己的进程的进程描述符（task_struct)为自己的group_leader。copy_process函数中有如下代码：

```c
p->pid = pid_nr(pid);
    p->tgid = p->pid;//普通进程
    if (clone_flags & CLONE_THREAD)
        p->tgid = current->tgid；//线程选择叫起它的进程的tgid作为自己的tgid 
    .... 
    p->group_leader = p;//普通进程
    INIT_LIST_HEAD(&p->thread_group); 
    ... 
    if (clone_flags & CLONE_THREAD) {
       current->signal->nr_threads++;
       atomic_inc(&current->signal->live);
       atomic_inc(&current->signal->sigcnt);
       p->group_leader = current->group_leader;//线程选择叫起它的进程作为它的group_leader
       list_add_tail_rcu(&p->thread_group, &p->group_leader->thread_group);
}

```

OK,ps -eLf中有个字段叫NLWP，就是线程组中LWP的个数，对于我们的例子，main函数所在LWP+两个线程 = 3.
   我们传说的getpid函数，本质取得是进程描述符的TGID，而gettid系统调用，取得才是每个LWP各自的PID。请看上面的图片输出，上面连个线程gettid返回的是3873和3874,是自己的PID。稍微有点毁三观
   除此外，需要指出的是用户态pthread_create出来的线程，在内核态，也拥有自己的进程描述符task_struct（copy_process里面调用dup_task_struct创建）。这是什么意思呢。意思是我们用户态所说的线程，一样是内核进程调度的实体。进程调度，严格意义上说应该叫LWP调度，进程调度，不是以前面提到的线程组为单位调度的，本质是以LWP为单位调度的。这个结论乍一看惊世骇俗，细细一想，其是很合理。我们为什么多线程？因为多CPU，多核，我们要充分利用多核,同一个线程组的不同LWP是可以同时跑在不同的CPU之上的，因为这个并发，所以我们有线程锁的设计，这从侧面证明了，LWP是调度的实体。
   我们用systemtap去观察下test2程序相关的调度：systemtap脚本如下：

```sh
#! /usr/bin/env stap
#
#
global time_offset

probe begin
{
    time_offset = gettimeofday_us() 
    printf("monitor begin==========\n")
}
probe scheduler.cpu_off
{
   if(task_execname(task_next)=="test2")
   {
       t = gettimeofday_us();
       printf("%9d : %20s(%6d)->%10s(%6d:%6d)\n",
            t-time_offset,
            task_execname(task_prev),
            task_pid(task_prev), 
            task_execname(task_next),
            task_pid(task_next),   #返回的是内核中的TGID
            task_tid(task_next))   #返回的内核中的PID 
   }
} 
```

我们的二进制可执行程序叫做 test2, 一个终端叫起systemtap，另一个终端叫起test2,查看下输出：

![](https://github.com/XGWang0/wiki/raw/master/_images/process_thread_threadgroup_4.png)

![](https://github.com/XGWang0/wiki/raw/master/_images/process_thread_threadgroup_5.png)

上面三个LWP都是CPU友好型的，如果同属一个线程组的多个线程（或者称之为LWP）都是CPU消耗型，你可以看到激烈的争夺CPU资源。

Refer to http://www.it165.net/os/html/201305/5123.html#about
