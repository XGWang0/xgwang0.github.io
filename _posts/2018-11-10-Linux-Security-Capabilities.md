---
layout: post
title:  "Capabilitys Of Linux"
categories: Security
tags:  security capability
author: Root Wang
---

* content
{:toc}

### BackGround
I came across Linux Capabilities while researching PID namespaces in the Linux Kernel. They are certainly nothing new (they came out in the 2.2 kernel), but they are currently getting more attention, as a means of security for containers. Capabilities are essentially a system for limiting execution privilege in the kernel space.

To understand capabilities, we need to do a quick refresher on standard linux process access control.

Linux processes can be of two types, privileged or unprivileged. Privileged processes traditionally bypass all kernel permission checks, whereas unprivileged processes are subject to full permission checking based on the process’s credentials (usually: effective UID, effective GID, and supplementary group list).

In kernel release 2.2, Linux started to divide the privileges associated with superuser into distinct units, known as capabilities, which can be independently enabled and disabled.

Capabilities are a per-thread attribute. They are the go to standard now, for allowing a binary to execute with a raised privilege in a bite size manner.

Prior to capabilities, developers would use setuid to allow normal users to call an executable at root level.

### SETUID
A good example of setuid would be for the ping command. Ping required root so it can open a socket in raw mode.

```c
icmp_sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
```

However, for ping to be useful, you really want the tool to be available for all users to execute. To achieve this, setuid is assigned, which allows an object to execute with User ID 0 (root)

On older pre capability systems, you could view the setuid bit in the permissions of the ping binary.

```sh
$ ls -l /bin/ping
 -rwsr-xr-x 1 root root 44168 Jan  2 13:43 /bin/ping
```
The ‘s’ denotes the setuid bit.

>Note: Most binaries are now ported over to using capabilities, but a good number to do still exist, you can find a list using the following:

```sh
$ sudo find /usr/bin /usr/lib -perm /4000 -user root
To show what happens, when ping has no setuid, let’s revoke the setuid..

$ sudo chmod u-s /bin/ping
$ ls -l /bin/ping
 -rwxr-xr-x 1 root root 44168 Jan&nbsp; 2 13:43 /bin/ping
Now when we try to use ping, without setuid providing us sufficient permissions to open a unix socket, we get permission denied

$ ping localhost
 ping: icmp open socket: Operation not permitted
Note: to add back, just use ‘u+s’.
```

### SETUID SECURITY
There is a slight problem with using setuid, in that you are opening a window to possible exploits. Bad code can allow an attacker to use setuid to elevate permissions to a root level. I have seen people use c-wrappers before to execute a script with setuid, something like the following

```c
int main(void) {        
    setuid(0);
    clearenv();
    system("/absolute/path/to/your/script.sh");
}
```

> Never do this for obvious reasons! Use sudo if you have to or of course capabilities coupled with SELinux assignments.


### INTRODUCING CAPABILITIES
Let’s look at the same example, ‘ping’, but instead using capabilities (which are now the standard in most Linux distributions)

We will use two commands, getcap (retrieve capabilities) and setcap (set capabilities)
```
$ getcap /bin/ping
/bin/ping = cap_net_admin,cap_net_raw+ep
So two grants are made, CAP_NET_ADMIN

CAP_NET_ADMIN
              Perform various network-related operations:
              * interface configuration;
              * administration of IP firewall, masquerading, and accounting;
              * modify routing tables;
              * bind to any address for transparent proxying;
              * set type-of-service (TOS)
              * clear driver statistics;
              * set promiscuous mode;
              * enabling multicasting;
              * use setsockopt(2) to set the following socket options:
                SO_DEBUG, SO_MARK, SO_PRIORITY (for a priority outside the
                range 0 to 6), SO_RCVBUFFORCE, and SO_SNDBUFFORCE.
And CAP_NET_RAW+EP

CAP_NET_RAW
              * use RAW and PACKET sockets;
              * bind to any address for transparent proxying.
```

> Note: +EP means that the capability is permitted and effective.

So now lets try to remove a capability from ping, and see the result.

First to save messing with my own generic ping, lets make a copy (copying will copy the binary, but not the capabilities)

```
$ sudo cp /bin/ping /tmp/newping
And let’s try it out

$ /tmp/newping localhost
ping: icmp open socket: Operation not permitted
```

So essentially, it fails as it does not have the needed capability assigned to allow a raw socket needed to send the ICMP packets.

So using ‘setcap’, lets grant it cap_net_raw+ep

```
$ sudo setcap cap_net_raw+ep /tmp/newping
$ /tmp/newping localhost
PING localhost.localdomain (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost.localdomain (127.0.0.1): icmp_seq=1 ttl=64 time=0.043 ms
64 bytes from localhost.localdomain (127.0.0.1): icmp_seq=2 ttl=64 time=0.039 ms
For a full list of capabilities, refer to the man page or in the capabilities header file.
```

### SELINUX
A quick note, SELinux and Capabilities are not mutually exclusive. Both systems should be utilized, to provide a defense in depth type approach. As it stands SELinux will provide more granular level of control, but capabilities still very much have their place in kernel security
