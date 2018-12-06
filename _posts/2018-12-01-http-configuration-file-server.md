---
layout: post
title:  "Http config fiel setting for file server"
categories: web
tags:  http fileserver
author: Root Wang
---

* content
{:toc}

### Version of server

OS : opensuse 42.3
apach2 : 2.4.33


### Make directory possible to access

`/etc/apach2/httpd.conf` setting:
```doc
<Directory />
    Options Indexes FollowSymLinks
    AllowOverride None
    Order allow,deny   
    Allow from all
</Directory>
```
Note: "Require all denied" is used when apach2 version is greate then 2.2, or use "Order allow,deny Allow from all"


Add config info for directory you want to expose in `/etc/apach2/default-server.conf`:
```doc
<Directory "/aa/bb/cc/dd">
        Options Indexes MultiViews
        AllowOverride None
        Order allow,deny
        Allow from all
</Directory>
```

