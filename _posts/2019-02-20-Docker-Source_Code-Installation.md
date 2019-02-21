---
layout: post
title:  "Docker Source Code Installation"
categories: DOCKER
tags:  
author: Root Wang
---

* content
{:toc}

'''因为docker的源码需要在容器中进行编译，因此必须要有docker安装在host上。'''


### step 1：clone源码

git clone https://github.com/moby/moby.git

这里你只是得到了docker daemon的源码，在项目发生迁移后docker的源码被拆分成client端和daemon端，client的源码路径为：

git clone https://github.com/docker/cli.git


### step 2：以下是在daemon端的操作，可以编译出除docker 之外的所有binary（7个以docker开头的binary）
在源码的根目录执行make build，这一步会调用Makefile中的build分支代码：

build: bundles init-go-pkg-cache
        docker build ${BUILD_APT_MIRROR} ${DOCKER_BUILD_ARGS} -t "$(DOCKER_IMAGE)" -f "$(DOCKERFILE)" 

这一步会使用docker创建一个临时的容器，并在容器中基于DOCKERFILE创建image，这个image包含了docker源码编译所需的依赖文件。这一步会下载很多依赖的文件需要访问很多国外的网站，由于国内的网络问题经常会因访问不到而失败。本人所在的公司可以访问国外的大部分网站，在两次编译源码时第一次一次成功，第二次经过不同时间的多次尝试才成功，不知道国内的网站是否能够靠多次尝试成功。

### step 3：执行make binary，这会调用Makefile中的binary分支代码：

binary: build ## build the linux binaries
        $(DOCKER_RUN_DOCKER) hack/make.sh binary

这一步是在上一步创建的image中创建容器并在容器中运行hack/make.sh
在hack/make.sh 中会调用/hack/make/binary，

在hack/make/binary中会调用/hack/make/binary-client 和binary-daemon，这两个脚本会分别调用同目录下的.binary文件，这个.binary是一个隐藏文件。在.binary文件中会执行go build 语句实现源码的最终的编译：

go build \
        -o "$DEST/$BINARY_FULLNAME" \
        "${BUILDFLAGS[@]}" \
        -ldflags "
                $LDFLAGS
                $LDFLAGS_STATIC_DOCKER
        " \
        $GO_PACKAGE

我们可以追踪GO_PACKAGE，发现它就是docker/cmd/dockerd/docker.go两个文件，也就是docker源码的入口文件。要继续搞清楚源码都做了些什么就要从这两个文件入手一步步查看。

make binary需要较长的时间，在完成之后你就可以在bundles目录下看到两个目录,进去binary-daemon，可以看到很多文件，将以docker开头的ELF文件copy至/usr/bin下（之前先要移除原先的docker binary），注意dockerd-dev要改成dockerd，重启docker（可以用systemctl）运行docker version，你就会发现你的dockerd已经升级到最新了，但是你的docker还是老样子。接下来编译docker client。其实版本不一致一般不影响使用。

其实不执行上一部直接make binary也是可以成功编译的，这里重在介绍过程。

### step4：编译docker client

进入源码目录运行：

# make -f docker.Makefile
完成之后在build目录下会生成docker binary，注意不要把docker的链接当成docker，将其替换原有的docker binary，替换是注意名字要和原先保持一致，名字为docker
重启docker，再运行docker version，你会发现都已经升级到最新了。
