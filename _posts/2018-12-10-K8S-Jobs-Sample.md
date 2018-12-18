---
layout: post
title:  "K8S Jobs Sample"
categories: k8s
tags:  docker k8s
author: Root Wang
---

* content
{:toc}


### Host env
hostA : 
	ip : 11.11.18.8
	os : opensuse 42.3
	docker : 18.06.1-ce
        Go : go1.10.5
	flannel : 0.7.1-1.2
	etcd : 3.1.0-3.2
	etcdctl : 3.1.0-3.2

hostB : 
	ip : 11.11.19.191
	os : opensuse 42.3
	docker : 18.06.1-ce
        Go : go1.10.5
	etcd : 3.1.0-3.2
	etcdctl : 3.1.0-3.2

### Job Desc
A job creates one or more pods and ensures that a specified number of them successfully terminate. As pods successfully complete, the job tracks the successful completions. When a specified number of successful completions is reached, the job itself is complete. Deleting a Job will cleanup the pods it created.

A simple case is to create one Job object in order to reliably run one Pod to completion. The Job object will start a new Pod if the first pod fails or is deleted (for example due to a node hardware failure or a node reboot).

A Job can also be used to run multiple pods in parallel.


### Job Pattern
The Job object can be used to support reliable parallel execution of Pods. The Job object is not designed to support closely-communicating parallel processes, as commonly found in scientific computing. It does support parallel processing of a set of independent but related work items. These might be emails to be sent, frames to be rendered, files to be transcoded, ranges of keys in a NoSQL database to scan, and so on.

In a complex system, there may be multiple different sets of work items. Here we are just considering one set of work items that the user wants to manage together — a batch job.

There are several different patterns for parallel computation, each with strengths and weaknesses. The tradeoffs are:

One Job object for each work item, vs. a single Job object for all work items. The latter is better for large numbers of work items. The former creates some overhead for the user and for the system to manage large numbers of Job objects.
Number of pods created equals number of work items, vs. each pod can process multiple work items. The former typically requires less modification to existing code and containers. The latter is better for large numbers of work items, for similar reasons to the previous bullet.
Several approaches use a work queue. This requires running a queue service, and modifications to the existing program or container to make it use the work queue. Other approaches are easier to adapt to an existing containerised application.
The tradeoffs are summarized here, with columns 2 to 4 corresponding to the above tradeoffs.

|Pattern|Single Job object|Fewer pods than work items?|Use app unmodified?|Works in Kube 1.1?|
|Job Template Expansion|||✓|✓|
|Queue with Pod Per Work Item|✓||sometimes|✓|
|Queue with Variable Pod Count|✓|✓||✓|
|Single Job with Static Work Assignment|✓||✓||	


This table shows the required settings for .spec.parallelism and .spec.completions for each of the patterns. Here, W is the number of work items.
|Pattern|.spec.completions|.spec.parallelism|
|Job Template Expansion|1|should be 1|
|Queue with Pod Per Work Item|W|any|
|Queue with Variable Pod Count|1|any|
|Single Job with Static Work Assignment|W|any|



#### Job Template Expansion

*One Job  VS One Pod*

1.Preapre job yaml file
There are 3 job instance, take one of them as example:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: job-item-apple
  labels:
    jobgroup: jobexample
spec:
  template:
    metadata:
      name: jobexample
      labels:
        jobgroup: jobexample
    spec:
      containers:
      - name: c
        image: busybox
        command: ["sh", "-c", "echo job item apple && sleep 5"]
      restartPolicy: Never
```

2.Move all jobs to single folder
```sh
$ ls jobs/
job-apple.yaml
job-banana.yaml
job-cherry.yaml
```

[Get job-apple.yaml](https://github.com/XGWang0/wiki/raw/master/_files/k8s/jobs_sample/jobs/job_apple.yaml)

3.Run jobs

```sh
$ kubectl create -f ./jobs
job "process-item-apple" created
job "process-item-banana" created
job "process-item-cherry" created
```
Note: All job instance under folder ./jobs will be launched.

4.Check jobs status
```sh
$ kubectl get jobs -l jobgroup=jobexample
NAME                  DESIRED   SUCCESSFUL   AGE
process-item-apple    1         1            31s
process-item-banana   1         1            31s
process-item-cherry   1         1            31s
```

#### Queue with Pod Per Work Item
*One Job VS N Pod*

How many work items need to be processed depend on setting of .spec.completions, it is 8 in sample, altogether 8 itmes will be handled.

1. Start a message queue and store work items.
    * rabbitmq rc

        ```yaml
        metadata:
          labels:
            component: rabbitmq
          name: rabbitmq-controller
        spec:
          replicas: 1
          template:
            metadata:
              labels:
                app: taskQueue
                component: rabbitmq
            spec:
              containers:
              - image: rabbitmq
                name: rabbitmq
                ports:
                - containerPort: 5672
                resources:
                  limits:
                    cpu: 100m
        
        ```
        
    * rabbitmq server

        ```yaml
        apiVersion: v1
        kind: Service
        metadata:
          labels:
            component: rabbitmq
          name: rabbitmq-service
        spec:
          ports:
          - port: 5672
          selector:
            app: taskQueue
            component: rabbitmq
        ```
        
    * Launch rc and svc of rabbitmq

        ```sh
        kubectl create -f rabbitmq_rc.yaml
        kubectl create -f rabbitmq_service.yaml
        ```

[Get rabbitmq rc](https://github.com/XGWang0/wiki/raw/master/_files/k8s/jobs_sample/parallel_jobs/rabbitmq_rc.yaml)

[Get rabbitmq svc](https://github.com/XGWang0/wiki/raw/master/_files/k8s/jobs_sample/parallel_jobs/rabbitmq_server.yaml)

2. Testing message queue server

    * Create a temporary interactive container

        >$ kubectl run -i --tty temp --image ubuntu:18.04

    * Install some tools

        >root@temp-loe07:/# apt-get update
        >.... [ lots of output ] ....
        >root@temp-loe07:/# apt-get install -y curl ca-certificates amqp-tools python dnsutils
        >.... [ lots of output ] ....

    * Verify mq

        ```sh
        # You can also get value of RABBITMQ_SERVICE_SERVICE_HOST from kubectl get pod, the cluster_ip column
        root@temp-loe07:/# BROKER_URL=amqp://guest:guest@$RABBITMQ_SERVICE_SERVICE_HOST:5672
        
        # Now create a queue:
        
        root@temp-loe07:/# /usr/bin/amqp-declare-queue --url=$BROKER_URL -q foo -d
        foo
        
        # Publish one message to it:
        
        root@temp-loe07:/# /usr/bin/amqp-publish --url=$BROKER_URL -r foo -p -b Hello
        
        # And get it back.
        
        root@temp-loe07:/# /usr/bin/amqp-consume --url=$BROKER_URL -q foo -c 1 cat && echo
        Hello
        root@temp-loe07:/#
        ```

    * Fill the mq

        ```sh
        $ /usr/bin/amqp-declare-queue --url=$BROKER_URL -q job1  -d
        job1
        $ for f in apple banana cherry date fig grape lemon melon
        do
          /usr/bin/amqp-publish --url=$BROKER_URL -r job1 -p -b $f
        done
        ```

3. Create a image which is used by the sample

    * Prepare worker.py program to handle stdin from mq

    ```python
    #!/usr/bin/env python
    
    # Just prints standard out and sleeps for 10 seconds.
    import sys
    import time
    import os
    print("porcess id : [%d]" %os.getpid())
    print("Processing " + ''.join(sys.stdin.readlines()))
    
    time.sleep(60)
    ```

    * Prepare dockerfile

    ```doc
    # Specify BROKER_URL and QUEUE when running
    FROM ubuntu:18.04
    
    RUN apt-get update && \
        apt-get install -y curl ca-certificates amqp-tools python \
           --no-install-recommends \
        && rm -rf /var/lib/apt/lists/*
    COPY ./worker.py /worker.py
    RUN  chmod a+x /worker.py
    
    CMD  /usr/bin/amqp-consume --url=$BROKER_URL -q $QUEUE -c 1 /worker.py
    ```

    * Build image and push to docker hub

    ```sh
    $ docker build -t job-wq-1 .

    $ docker login

    $ docker tag job-wq-1 <username>/job-wq-1
    $ docker push <username>/job-wq-1
    ```
[Get Dockerfile](https://github.com/XGWang0/wiki/raw/master/_files/k8s/jobs_sample/parallel_jobs/work-queue-1/Dockerfile)
[Get worker.py](https://github.com/XGWang0/wiki/raw/master/_files/k8s/jobs_sample/parallel_jobs/work-queue-1/worker.py)

4. Define a job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: job-wq-1
spec:
  #completions: 4
  parallelism: 2
  template:
    metadata:
      name: job-wq-1
    spec:
      containers:
      - name: c
        image: john1wang/job-wq-1:latest
        #command: ["/bin/bash", "-c", "echo tttttttttttttttttt & sleep 100"]
        #command: ["/usr/bin/amqp-consume", "--url=amqp://guest:guest@10.254.244.224:5672", "-q", "job1", "-c", "1", "/worker.py"]
        env:
        - name: BROKER_URL
          value: amqp://guest:guest@10.254.244.224:5672
        - name: QUEUE
          value: job1
      restartPolicy: OnFailure
      nodeSelector:
        nodename: local
```

[Get job yaml](https://github.com/XGWang0/wiki/raw/master/_files/k8s/jobs_sample/parallel_jobs/parallel_jobs.yaml)

5. Start the job

```sh
$ kubectl create -f ./parallel_jobs.yaml
```

6. Wait a moment and check the job

```sh
$ kubectl describe jobs/job-wq-1
Name:             job-wq-1
Namespace:        default
Selector:         controller-uid=41d75705-92df-11e7-b85e-fa163ee3c11f
Labels:           controller-uid=41d75705-92df-11e7-b85e-fa163ee3c11f
                  job-name=job-wq-1
Annotations:      <none>
Parallelism:      2
Completions:      8
Start Time:       Wed, 06 Sep 2017 16:42:02 +0800
Pods Statuses:    0 Running / 8 Succeeded / 0 Failed
Pod Template:
  Labels:       controller-uid=41d75705-92df-11e7-b85e-fa163ee3c11f
                job-name=job-wq-1
  Containers:
   c:
    Image:      gcr.io/causal-jigsaw-637/job-wq-1
    Port:
    Environment:
      BROKER_URL:       amqp://guest:guest@rabbitmq-service:5672
      QUEUE:            job1
    Mounts:             <none>
  Volumes:              <none>
Events:
  FirstSeen  LastSeen   Count    From    SubobjectPath    Type      Reason              Message
  ─────────  ────────   ─────    ────    ─────────────    ──────    ──────              ───────
  27s        27s        1        {job }                   Normal    SuccessfulCreate    Created pod: job-wq-1-hcobb
  27s        27s        1        {job }                   Normal    SuccessfulCreate    Created pod: job-wq-1-weytj
  27s        27s        1        {job }                   Normal    SuccessfulCreate    Created pod: job-wq-1-qaam5
  27s        27s        1        {job }                   Normal    SuccessfulCreate    Created pod: job-wq-1-b67sr
  26s        26s        1        {job }                   Normal    SuccessfulCreate    Created pod: job-wq-1-xe5hj
  15s        15s        1        {job }                   Normal    SuccessfulCreate    Created pod: job-wq-1-w2zqe
  14s        14s        1        {job }                   Normal    SuccessfulCreate    Created pod: job-wq-1-d6ppa
  14s        14s        1        {job }                   Normal    SuccessfulCreate    Created pod: job-wq-1-p17e0
```

7. Check pod result

```sh
$ kubectl logs pod/job-wq-1-hcobb

Result:
porcess id : [7]
Processing apple
```

#### Queue with Variable Pod Count
*One Job VS N Pod*

How many work items need to be processed depend on program itself, program will handle all situations like if mq is empty etc.

All operations are same as `Queue with Pod Per Work Item`, the diff is the job yaml file and worker.py

* Job Yaml
Do not need to specify .spec.completions item.

* worker.py
Need to handle multiple situations, like mq is empty, wait item comming, and so on.
