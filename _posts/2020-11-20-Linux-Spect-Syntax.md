---
layout: post
title:  "SPECT SYNATX"
categories: Linux
tags:  Linux
author: Root Wang
---

* content
{:toc}

### The RPM system assumes five RPM directories
BUILD：rpmbuild编译软件的目录
RPMS：rpmbuild创建的binary RPM所存放的目录
SOURCES：存放源代码的目录
SPEC：存放spec文件的目录
SRPMS：rpmbuild创建的source RPM所存放的目录


### Variables and Marco

* Debug marco
%dump：打印宏的值
%{echo:message} ：打印信息到标准错误
%{error:message} ：打印信息到标准错误，然后返回BADSPEC
%{expand:expression} :like eval, expands expression
%{F:file_exp} ：扩展file_exp到一个文件名
%global name value ：定义一个全局宏
%{P:patch_exp} ：扩展patch_exp到一个补丁文件名
%{S:source_exp} ：扩展source_exp到一个源码文件名
%trace ：跟踪调试信息
%{uncompress:filename}
Tests if file filename is compressed. If so, uncompresses and includes
in the given context. If not compressed, calls cat to include file in given context.
%undefine macro ：取消给定的宏定义
%{warn:message} ：打印信息到标准错误

* macro define
%define  macro_name  value
然后可以用%macro_name或者%{macro_name}来调用，也可以扩展到shell，如
%define today %(date)  (变量定义宏)
也可以传递参数给宏
%define macro_name(option)  value
%foo 1 2 3 传递1,2,3三个参数给宏foo
在宏扩展的宏参数
%0：宏的名字
%*：传递给宏的所有参数
%#：传递给宏的参数个数
%1：第一个参数
%2：第二个参数，等等
%{-p}：Holds -p
%{-p*}：Holds the value passed with the -p parameter, if the -p parameter was passed to the macro;otherwise holds nothing
%{-p:text}：Holds text if the -p parameter was passed to the macr;otherwise holds nothing
%{?macro_to_text:expression}：如果macro_to_text存在，expand expression，如国不存在，则输出为空;也可以逆着用，:%{!?macro_to_text:expression}
%{?macro}：忽略表达式只测试该macro是否存在，如果存在就用该宏的值，如果不存在，就不用，如：./configure %{?_with_ldap}
%if %{old_5x}
%define b5x 1
%undefine b6x
%endif
or
%if %{old_5x}
%define b5x 1
%undefine b6x
%else
%define b6x 1
%undefine b5x
%endif
还可以用!，&&等符号，如：
%if %{old_5x} && %{old_6x}
%{error: you cannot build for .5x and .6x at the same time}
%quit
%endif
%ifarch sparc  alpha：判断处理器的结构
%ifnoarch i386 alpha：跟%ifarch相反
％ifos linux：测试操作系统
％ifnos linux：跟%ifos相反


* Get implement code:
```c
rpm --showrc
```

* Get specific variable or marco：
```c
rpm --eval "%{macro}"
rpm --eval "%{_bindir}"
```
* Get all marcos:

View file /usr/lib/rpm/macros

```c
%{_sysconfdir}        /etc
 
%{_prefix}            /usr
 
%{_exec_prefix}       %{_prefix}
 
%{_bindir}            %{_exec_prefix}/bin
 
%{_lib}               lib (lib64 on 64bit systems)
 
%{_libdir}            %{_exec_prefix}/%{_lib}
 
%{_libexecdir}        %{_exec_prefix}/libexec
 
%{_sbindir}           %{_exec_prefix}/sbin
 
%{_sharedstatedir}    /var/lib
 
%{_datadir}           %{_prefix}/share
 
%{_includedir}        %{_prefix}/include
 
%{_oldincludedir}     /usr/include
 
%{_infodir}           /usr/share/info
 
%{_mandir}            /usr/share/man
 
%{_localstatedir}     /var
 
%{_initddir}          %{_sysconfdir}/rc.d/init.d
 
Note: On releases older than Fedora 10 (and EPEL), %{_initddir} does not exist. Instead, you should use the deprecated %{_initrddir} macro.
```

### SPEC SYNATX
* 1     文件头

一般的spec文件头包含以下几个域：
 
** 1.1   Name

描述：

软件包的名称，后面可使用%{name}的方式引用

格式：

Name:          <software name>

 
** 1.2   Version

描述：

软件包的名称，后面可使用%{name}的方式引用软件包版本号，后面可使用%{version}引用

格式：

Version:          <software version>

 
** 1.3   Release

描述：

软件包的发行号，后面可使用%{release}引用;设置rpm包的修订号

格式：

Release:          <software release>

 
** 1.4   Packager

描述：

打包的人（一般喜欢写个人邮箱）

格式：

Packager:          youner_liucn@126.com

 
** 1.5   License

描述：

软件授权方式，通常是GPL（自由软件）或GPLv2,BSD

格式：

License:          GPL

 
** 1.6   Summary

描述：

打包的人（一般喜欢写个人邮箱）

格式：

Packager:          youner_liucn@126.com

 
** 1.7   Group

描述：

软件包所属类别

格式：

Group:       Applications/Multimedia

具体类别：

Amusements/Games（娱乐/游戏）

Amusements/Graphics（娱乐/图形）

Applications/Archiving（应用/文档）

Applications/Communications（应用/通讯）

Applications/Databases（应用/数据库）

Applications/Editors（应用/编辑器）

Applications/Emulators（应用/仿真器）

Applications/Engineering（应用/工程）

Applications/File（应用/文件）

Applications/Internet（应用/因特网）

Applications/Multimedia（应用/多媒体）

Applications/Productivity（应用/产品）

Applications/Publishing（应用/印刷）

Applications/System（应用/系统）

Applications/Text（应用/文本）

Development/Debuggers（开发/调试器）

Development/Languages（开发/语言）

Development/Libraries（开发/函数库）

Development/System（开发/系统）

Development/Tools（开发/工具）

Documentation （文档）

SystemEnvironment/Base（系统环境/基础）

SystemEnvironment/Daemons （系统环境/守护）

SystemEnvironment/Kernel （系统环境/内核）

SystemEnvironment/Libraries （系统环境/函数库）

SystemEnvironment/Shells （系统环境/接口）

UserInterface/Desktops（用户界面/桌面）

User Interface/X（用户界面/X窗口）

User Interface/XHardware Support （用户界面/X硬件支持）


** 1.7 ExcludeArch/ExclusiveArch/Excludeos/Exclusiveos
ExcludeArch: sparc s390        #rpm包不能在该系统结构下创建
ExclusiveArch: i386 ia64        #rpm包只能在给定的系统结构下创建
Excludeos:windows            #rpm包不能在该操作系统下创建
Exclusiveos: linux            #rpm包只能在给定的操作系统下创建

 
** 1.8   Source0

描述：

源代码包的名字

格式：

Source0:       %{name}-%{version}.tar.gz

 
** 1.9   BuildRoot

描述：

编译的路径。是安装或编译时使用的“虚拟目录”，考虑到多用户的环境，一般定义为：

该参数非常重要，因为在生成rpm的过程中，执行make install时就会把软件安装到上述的路径中，在打包的时候，同样依赖“虚拟目录”为“根目录”进行操作(即%files段)。

后面可使用$RPM_BUILD_ROOT 方式引用。

格式：
```c
BuildRoot：%{_tmppath}/%{name}-%{version}-%{release}-buildroot
```
 
** 1.10     URL

描述：

 软件的主页

格式：

URL: <web-site>

** 1.11     Vendor

描述：

 发行商或打包组织的信息，例如RedFlagCo,Ltd

格式：

Vendor: <RedFlag Co,Ltd>

** 1.11 Patch

Patch1:telnet-client-cvs.patch
Patch2:telnetd-0.17.diff
Patch3:telnet-0.17-env.patch    #补丁文件
 
** 1.12     Provides

描述：

 指明本软件一些特定的功能，以便其他rpm识别

格式：

Provides: <features>

* 2     依赖关系

依赖关系定义了一个包正常工作需要依赖的其他包，RPM在升级、安装和删除的时候会确保依赖关系得到满足。rpm支持4种依赖：

1  Requirements, 包依赖其他包所提供的功能
2  Provides, 这个包能提供的功能
3  Conflicts, 一个包和其他包冲突的功能
4  Obsoletes, 其他包提供的功能已经不推荐使用了，这通常是其他包的功能修改了，老版本不推荐使用了，可以在以后的版本中会被废弃。

** 2.1   定义依赖关系

定义依赖关系的语法是：

Requires: capability

Provides: capability

Obsoletes: capability

Conflicts: capability

大部分时候，capability应该是所依赖的包的名称。一行中也可以定义多个依赖，比如：

Requires: tbsys tbnet

 
** 2.2   指定依赖的版本号

在指定依赖关系的时候还可以指定版本号，比如:

Requires: tbsys >= 2.0

rpm支持的比较如下：

 
** 2.3   Requires

描述：

所依赖的软件包名称, 可以用>=或<=表示大于或小于某一特定版本。 “>=”号两边需用空格隔开，而不同软件名称也用空格分开。

格式：

Requires:       libpng-devel >= 1.0.20 zlib

其它写法例如：

Requires: bzip2 = %{version}, bzip2-libs =%{version}

或

Requires: perl(Carp)>=3.2       #需要perl模块Carp

还有例如PreReq、Requires(pre)、Requires(post)、Requires(preun)、Requires(postun)、BuildRequires等都是针对不同阶段的依赖指定。

例如：

     PreReq: capability>=version      #capability包必须先安装

     Conflicts:bash>=2.0                 #该包和所有不小于2.0的bash包有冲突

*** 2.3.1 PreReq

PreReq: capability >=version    #capability包必须先安装

** 2.4   BuildRequires

描述：

编译时的包依赖

格式：

BuildRequires: zlib-devel

* 3     说明%description

软件包详细说明，可写在多个行上。

%description

Consul feature - Service Discovery, HealthChecking, KV, Multi Datacenter

 
* 4     预处理%prep

预处理通常用来执行一些解开源程序包的命令，为下一步的编译安装作准备。%prep和下面的%build，%install段一样，除了可以执行RPM所定义的宏命令（以%开头）以外，还可以执行SHELL命令。功能上类似于./configure。

作用：

用来准备要编译的软件。通常，这一段落将归档中的源代码解压，并应用补丁。这些可以用标准的 shell 命令完成，但是更多地使用预定义的宏。

检查标签语法是否正确，删除旧的软件源程序，对包含源程序的tar文件进行解码。如果包含补丁（patch）文件，将补丁文件应用到解开的源码中。它一般包含%setup与%patch两个命令。%setup用于将软件包打开，执行%patch可将补丁文件加入解开的源程序中。

 
** 4.1   宏%setup

这个宏解压源代码，将当前目录改为源代码解压之后产生的目录。这个宏还有一些选项可以用。例如，在解压后，%setup 宏假设产生的目录是%{name}-%{version}

 如果 tar 打包中的目录不是这样命名的，可以用 -n 选项来指定要切换到的目录。例如：

%setup -n%{name}-April2003Rel

%setup -q 将 tar 命令的繁复输出关闭。

%setup -n newdir -将压缩的软件源程序在newdir目录下解开。

%setup -c 在解开源程序之前先创建目录。

%setup -b num 在包含多个源程序时，将第num个源程序解压缩。

%setup -T 不使用缺省的解压缩操作。

例如：

%setup -T -b 0

//解开第一个源程序文件。

%setup -c -nnewdir

//创建目录newdir，并在此目录之下解开源程序。

 
** 4.2   宏%patch

这个宏将头部定义的补丁应用于源代码。如果定义了多个补丁，它可以用一个数字的参数来指示应用哪个补丁文件。它也接受 -b extension 参数，指示 RPM 在打补丁之前，将文件备份为扩展名是 extension 的文件。

%patch N 这里N是数字，表示使用第N个补丁文件，等价于%patch-P N

-p0 指定使用第一个补丁文件，-p1指定使用第二个补丁文件。

-s 在使用补丁时，不显示任何信息。

-b name 在加入补丁文件之前，将源文件名上加入name。若为指定此参数，则缺省源文件加入.orig。

-T 将所有打补丁时产生的输出文件删除

* 5     编译%build

定义编译软件包所要执行的命令， 这一节一般由多个make命令组成。

作用：

在这个段落中，包含用来配置和编译已配置的软件的命令。与 Prep 段落一样，这些命令可以是 shell 命令，也可以是宏。

如果要编译的宏使用了 autoconf，那么应当用 %configure 宏来配置软件。这个宏自动为 autoconf 指定了安装软件的正确选项，编译优化的软件。

如果软件不是用 autoconf 配置的，那么使用合适的 shell 命令来配置它。

软件配置之后，必须编译它。由于各个应用程序的编译方法都各自不同，没有用来编译的宏。只要写出要用来编译的 shell 命令就可以了。

环境变量 $RPM_OPT_FLAGS 在编译软件时很常用。这个 shell 变量包含针对 gcc 编译器套件的正确的优化选项，使用这样的语法：

makeCC="gcc $RPM_OPT_FLAGS"

或者

makeCFLAGS="$RPM_OPT_FLAGS"

就可以保证总是使用合适的优化选项。也可以使用其他编译器标志和选项。默认的 $RPM_OPT_FLAGS 是：

-O2 -g-march=i386 -mcpu=i686

* 6     安装%install

定义在安装软件包时将执行命令，类似于make install命令。有些spec文件还有%post-install段，用于定义在软件安装完成后的所需执行的配置工作。

作用：

这个段落用于将已编译的软件安装到虚拟的目录结构中，从而可以打包成一个 RPM。

在 Header 段落，可以定义 Buildroot，它定义了虚拟目录树的位置，软件将安装到那里。通常，它是这样的：

```c
Buildroot:%{_tmppath}/%{name}-buildroot
```
使用 RPM 内建的宏来指定 /var/tmp 目录中一个私用的目录。

在 spec 文件的其余部分可以用 shell 变量 $RPM_BUILD_ROOT 获取 Buildroot 的值。

mkdir -p $RPM_BUILD_ROOT/usr/share/icons/

cp %{SOURCE3} $RPM_BUILD_ROOT/usr/share/icons/

Install 段落通常列出要将已编译的软件安装到 Buildroot 中的命令

宏 %makeinstall 可以用于安装支持 autoconf 的软件。这个软件自动地将软件安装到 $RPM_BUILD_ROOT 下的正确的子目录中。

有时，软件包必须被构建多次，由于打包错误或其他原因。每次构建时，Install 段落将复制文件到 Buildroot 中。要防止由于 Buildroot 中的旧文件而导致错误的打包，必须在安装新文件之前将 Buildroot 中任何现有的文件删除。为此，可以使用一个 clean 脚本。这个脚本通常以 %clean 标记表示，通常仅仅包含这样一句：

rm -rf $RPM_BUILD_ROOT

如果有的话，在制作了在 Install 段落中安装的文件的打包之后，将运行 %clean，保证下次构建之前 Buildroot 被清空。

 
* 7     清理%clean

%clean

rm-rf $RPM_BUILD_ROOT

 
* 8     文件%files

定义软件包所包含的文件，分为三类：说明文档（doc），配置文件（config）及执行程序，还可定义文件存取权限，拥有者及组别。

这里会在虚拟根目录下进行，千万不要写绝对路径，而应用宏或变量表示相对路径。 如果描述为目录，表示目录中除%exclude外的所有文件。
%defattr (-,root,root) 指定包装文件的属性，分别是(mode,owner,group)，-表示默认值，对文本文件是0644，可执行文件是0755

%dir   /etc/xtoolwait    #包含一个空目录/etc/xtoolwait
%doc README NEWS            #安装这些文档到/usr/share/doc/ or /usr/doc
%docdir                    #定义存放文档的目录
%config /etc/yp.conf            #标志该文件是一个配置文件
%ghost  /etc/yp.conf            #该文件不应该包含在包中
%attr(mode, user, group)  filename    #控制文件的权限如%attr(0644,root,root) /etc/yp.conf，如果你不想指定值，可以用-
%defattr(-,root,root)            #设置文件的默认权限
%lang(en) %{_datadir}/locale/en/LC_MESSAGES/tcsh*    #用特定的语言标志文件
%verify(owner group size) filename    #只测试owner,group,size，默认测试所有
%verify(not owner) filename        #不测试owner
                    #所有的认证如下：
                    #group：认证文件的组
                    #maj：认证文件的主设备号
                    #md5：认证文件的MD5
                    #min：认证文件的辅设备号
                    #mode：认证文件的权限
                    #mtime：认证文件最后修改时间
                    #owner：认证文件的所有者
                    #size：认证文件的大小
                    #symlink：认证符号连接


* 9  %post 
定义安装之后执行的脚本

* 10 %preun
定义卸载软件之前执行的脚本

* 11 %postun
定义卸载软件之后执行的脚本

* 12 subpackage
%package sub_package_name   #定义一个子包，名字为package-subpackage
       -n sub_package_name  #定义一个子包，名字为sub_package_name
当定义一个子包时，必须至少包含Summary:,Group:,%description选项，任何没有指定的选项将用父包的选项，如版本等，如：
%package server
Requires: xinetd
Group: System Environment/Daemons
Summary:The server program for the telnet remote login protocol
%description server
Telnet is a popular protocol for logging into remote systems
如果在%package时用-n选项，那么在%description时也要用，如：
%description -n my-telnet-server
%files server
%defattr(-,root,root)
%{_sbindir}/in.telnetd
如果在%package时用-n选项，那么在%files时也要用，如：
%files -n my-telnet-server，也可以定义安装或卸载脚本，像定义%files和%description 一样

 
* 13     更新日志%changelog

每次软件的更新内容可以记录在此到这里，保存到发布的软件包中，以便查询之用。
