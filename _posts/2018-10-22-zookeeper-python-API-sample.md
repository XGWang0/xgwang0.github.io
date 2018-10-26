---
layout: post
title:  "Python sample for zookeeper controlling"
categories: zookeeper
tags:  bigdata HA cluster zookeeper
author: Root Wang
---

* content
{:toc}

## Python smaple for electing master

```python
#-*- coding: utf-8 -*-
import time
from kazoo.client import KazooClient
from kazoo.recipe.watchers import ChildrenWatch
import re
import os
import sys
import operator


class ElectionMaster(object):

    def __init__(self):
        self.current_host = sys.argv[1]
        self.zk = KazooClient(hosts='master:2181,openqa:2181,hadoop-slave2:2181')
        print(self.current_host)
        self.leadernode = '/Leader/vote'
        self.validator_children_watcher = ChildrenWatch(client=self.zk,
                                                        path=self.leadernode,
                                                        func=self.detectLeader)
        self.zk.start()

        self.host_seq_list = []

    def detectLeader(self, childrens):
        print("childern:", childrens)
        self.host_seq_list = [i.split("_") for i in childrens]
        print(self.host_seq_list)
        sorted_host_seqvalue = sorted(self.host_seq_list, key=operator.itemgetter(1))
        print("sorted_host_seqvalue", sorted_host_seqvalue)
        if sorted_host_seqvalue and sorted_host_seqvalue[0][0] == self.current_host:
            print("I am current leader :%s" %self.current_host)
            self.do_something()
        else:
            print("I am a slave :%s" % self.current_host)

    def do_something(self):
        print("I am leader, i niubility..............")

    def create_node(self):
        self.zk.create(os.path.join(self.leadernode, "%s_" % self.current_host), b"host:", ephemeral=True, sequence=True, makepath=True)

    def __del__(self):
        self.zk.close()





if __name__ == '__main__':

    detector = ElectionMaster()
    detector.create_node()
    input("wait to quit:\n")
    #time.sleep(10)

```
