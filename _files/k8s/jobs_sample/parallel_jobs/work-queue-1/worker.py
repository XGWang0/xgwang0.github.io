#!/usr/bin/env python

# Just prints standard out and sleeps for 10 seconds.
import sys
import time
import os
print("porcess id : [%d]" %os.getpid() + "\n" + "Processing " + ''.join(sys.stdin.readlines()))

time.sleep(60)
