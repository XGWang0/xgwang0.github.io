---
layout: post
title:  "K8S Cluster Safe Setting"
categories: k8s
tags:  docker k8s
author: Root Wang
---

* content
{:toc}


### Host env
hostA : 
	os : opensuse 42.3
	docker : 18.06.1-ce
        Go : go1.10.5

hostB : 
	os : opensuse 42.3
	docker : 18.06.1-ce
        Go : go1.10.5


### Master Node

Servers: apiserver, controller-manager, scheduler

#### Apiserver Configuration

##### Genreate CA for apiserver

1.Generate CA 
```sh
openssl genrsa -out ca.key 2048

openssl req -x509 -new -nodes -key ca.key -subj "/CN=murphy" -days 5000 -out ca.crt

openssl genrsa -out server.key 2048
```
Note: -subj "/CN"'s vaule is domain name commonly.

2.Prepare master_ssl.cnf
```doc
[req]
req_extensions = v3_req
distinguished_name      = req_distinguished_name

[ req_distinguished_name ]

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = kubernetes
DNS.2 = kubernetes.default
DNS.3 = kubernetes.default.svc
DNS.4 = kubernetes.default.cluster.local
IP.1 = 10.254.0.0 # ip range value of '--service-cluster-ip-range' in /etc/kubernetes/apiserver
IP.2 = 10.67.18.8 # ip addr of master

```

3.Generate server.csr and server.crt file via master_ssl.cnf
```sh
openssl req -new -key server.key -subj "/CN=murphy" -config master_ssl.cnf -out server.csr

openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 5000 -extensions v3_req -extfile master_ssl.cnf -out server.crt
```

4.Modify apiserver config
Under folder /etc/kubernetes/apiserver

```doc
# `The port must me 6443, or will cause connection refuse issue.`
# For insercure mode, use `--insecure-port=8080`
KUBE_API_PORT="--secure-port=6443"

# Port minions listen on
# KUBELET_PORT="--kubelet-port=10250"

# Comma separated list of nodes in the etcd cluster
KUBE_ETCD_SERVERS="--etcd-servers=http://127.0.0.1:2379"

# Address range to use for services
KUBE_SERVICE_ADDRESSES="--service-cluster-ip-range=10.254.0.0/16"

# `options `ServiceAccount` must be added.`
KUBE_ADMISSION_CONTROL="--admission-control=NamespaceLifecycle,LimitRanger,ServiceAccount,DefaultStorageClass,ResourceQuota"

# `--client_ca_file=/john/k8s/CA/ca.crt --tls-private-key-file=/john/k8s/CA/server.key --tls-cert-file=/john/k8s/CA/server.crt` need add
KUBE_API_ARGS="--logtostderr=false --log-dir=/var/log/kubenetes --v=2 --storage-backend=etcd2 --storage-media-type=application/json --client_ca_file=/john/k8s/CA/ca.crt --tls-private-key-file=/john/k8s/CA/server.key --tls-cert-file=/john/k8s/CA/server.crt"

```

[Get apiserver config](https://github.com/XGWang0/wiki/raw/master/_files/k8s/cluster_safe_setting/master/apiserver)

5.Restart apiserver


#### Controller-Manager Configuration

1.Setting CA, private key for client of controller-manager
```sh
openssl genrsa -out cs_client.key 2048
openssl req -new -key cs_client.key -subj "/CN=node-1" -out cs_client.csr
openssl x509 -req -in cs_client.csr  -CA ca.crt -CAkey ca.key -CAcreateserial -days 5000   -out cs_client.crt
```

2.New kubeconfig file (controller-manager, scheduler share this file), set client CA parameters

```doc
current-context: my-context
apiVersion: v1
clusters:
- cluster:
    api-version: v1
    server: https://localhost:6443 # `This option is needed. or will cause "no server for cluster local" issue`
    certificate-authority: /john/k8s/CA/ca.crt
  name: local
contexts:
- context:
    cluster: local
    user: controllermanager
  name: my-context
kind: Config
users:
- name: controllermanager
  user:
    client-certificate: /john/k8s/CA/cs_client.crt
    client-key: /john/k8s/CA/cs_client.key

```

[Get kubeconfig file of master](https://github.com/XGWang0/wiki/raw/master/_files/k8s/cluster_safe_setting/master/kubeconfig)

3.Modify controller-manager config file
File /etc/kubernetes/controller-manager
```doc
# `--address=127.0.0.1` is compulsory
# `--service-account-private-key-file=/john/k8s/CA/server.key --root-ca-file=/john/k8s/CA/ca.crt --kubeconfig=/etc/kubernetes/kubeconfig` is added newly
KUBE_CONTROLLER_MANAGER_ARGS="--address=127.0.0.1 --logtostderr=false --log-dir=/var/log/kubernetes --v=0 --service-account-private-key-file=/john/k8s/CA/server.key --root-ca-file=/john/k8s/CA/ca.crt --kubeconfig=/etc/kubernetes/kubeconfig"
```

[Get controller-manager config](https://github.com/XGWang0/wiki/raw/master/_files/k8s/cluster_safe_setting/master/controller-manager)

#### Modify scheduler config file
File /etc/kubernetes/scheduler

```doc
# `--address 127.0.0.1` is compulsory, kubernetes hope the controller-manager and scheduler loact in same machine 
KUBE_SCHEDULER_ARGS="--address 127.0.0.1 --logtostderr=true --v=0 --kubeconfig=/etc/kubernetes/kubeconfig
```

[Get scheduler config](https://github.com/XGWang0/wiki/raw/master/_files/k8s/cluster_safe_setting/master/scheduler)


#### Verify all components

```sh
#> kubectl get componentstatus
-------------------------------
NAME                 STATUS    MESSAGE              ERROR
controller-manager   Healthy   ok                   
scheduler            Healthy   ok                   
etcd-0               Healthy   {"health": "true"}

### Node CA setting

#### Setting client CA private key for kubelet

1.Generate CA 
Copy all CA, keys to Node (HostB)
```sh
openssl genrsa -out kubelet_client.key 2048

openssl req -new -key kubelet_client.key -subj "/CN=10.67.19.191" -out kubelet_client.csr

openssl x509 -req -in kubelet_client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out kubelet_client.crt -days 5000
```

2.New kubeconfig file for Node
```doc
current-context: my-context
apiVersion: v1
clusters:
- cluster:
    certificate-authority: /etc/kubernetes/CA/ca.crt
  name: local
contexts:
- context:
    cluster: local
    user: kubelet
  name: my-context
kind: Config
users:
- name: kubelet
  user:
    client-certificate: /etc/kubernetes/CA/kubelet_client.crt
    client-key: /etc/kubernetes/CA/kubelet_client.key
```

[Get kubeconfig of node](https://github.com/XGWang0/wiki/raw/master/_files/k8s/cluster_safe_setting/node/kubeconfig)

3.Modify kubelet config file
File /etc/kubernetes/kubelet
```doc
KUBELET_HOSTNAME="--hostname-override=10.67.19.191"

# location of the api-server
# Use `https`, `6443` port defined in apiserver of master
KUBELET_API_SERVER="--api-servers=https://10.67.18.8:6443 --kubeconfig=/etc/kubernetes/kubeconfig"
```

[Get kubelet config](https://github.com/XGWang0/wiki/raw/master/_files/k8s/cluster_safe_setting/node/kubelet)

4.Restart kubelet server

#### Set proxy server
1.File /etc/kubernetes/proxy
```doc
KUBE_PROXY_ARGS="--master=https://10.67.18.8:6443 --kubeconfig=/etc/kubernetes/kubeconfig"
```

[Get proxy config](https://github.com/XGWang0/wiki/raw/master/_files/k8s/cluster_safe_setting/node/proxy)

2.Restart proxy server

#### Verify setting

Access server from node
```sh
kubectl --server=https://10.67.18.8:6443 --certificate-authority=/etc/kubernetes/CA/ca.crt --client-certificate=/etc/kubernetes/CA/cs_client.crt --client-key=/etc/kubernetes/CA/cs_client.key get nodes

NAME           STATUS     AGE       VERSION
10.67.19.191   Ready      1d        v1.6.1
127.0.0.1      NotReady   1d        v1.6.1
```


