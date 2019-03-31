---
layout: post
title:  "KVM Device Passthrough"
categories: Virtualization
tags:  kvm vfio-pci pci-stub
author: Root Wang
---

* content
{:toc}

### vfio
VFIO is a new method of doing PCI device assignment ("PCI passthrough" aka "") available in newish kernels (3.6?; it\'s in Fedora 18 at
any rate) and via the "vfio-pci" device in qemu-1.4+. In contrast to the traditional KVM PCI device assignment (available via the "pci-assign" device in qemu), VFIO works properly on systems using UEFI "Secure Boot"; it also offers other advantages, such as `grouping of related devices that must all be assigned to the same guest` (or not at all).
Here's some useful reading on the subject.


 https://lwn.net/Articles/474088/
 https://lwn.net/Articles/509153/

Sample:
1. Add parameter "intel_iommu=on" for intel cpu to kernel command line option.

2. Assume this is the device you want to assign:
    Take network card `02:00.0 Ethernet controller: Broadcom Limited NetXtreme BCM5720 Gigabit Ethernet PCIe` as example

3. Find the iommu group of this device

```sh
/sys/bus/pci/devices/0000:02:00.0 # readlink iommu_group
../../../../kernel/iommu_groups/16
```

4. Find all devices belonging to iommu_groups 16
```sh
/sys/bus/pci/devices/0000:02:00.0 # ls ../../../../kernel/iommu_groups/16/devices/

0000:02:00.0  0000:02:00.1
```
> There are 2 devices in 16 iommu group, so the both devices are need to be unbinded, add to new driver.

5. Get vendor id and device id 
```sh
#> lspci -n -s 02:00.0 
#> lspci -n -s 02:00.1 

02:00.1 0200: 14e4:165f
```

6. Unbind the 2 devices from them driver.
```sh
# Get driver of device
/sys/bus/pci/devices/0000:02:00.0 # readlink  driver

../../../../bus/pci/drivers/tg3

--------------------------------

# Unbind device from driver
echo 0000:02:00.0 > /sys/bus/pci/devices/0000\:02\:00.0/driver/unbind
echo 0000:02:00.1 > /sys/bus/pci/devices/0000\:02\:00.1/driver/unbind

# Add device to vfio-pci driver
echo 14e4 165f > /sys/bus/pci/drivers/vfio-pci/new_id

# Verify device's driver
/sys/bus/pci/devices/0000:02:00.0 # readlink  driver

../../../../bus/pci/drivers/vfio-pci

```

7. Edit guest xml and add following content to device section
```xml
    <hostdev mode='subsystem' type='pci' managed='yes'>
      <source>
        <address domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>
      </source>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x0a' function='0x0'/>
    </hostdev>
    <hostdev mode='subsystem' type='pci' managed='yes'>
      <source>
        <address domain='0x0000' bus='0x02' slot='0x00' function='0x1'/>
      </source>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x0b' function='0x0'/>
    </hostdev>
```

Note: You can also get right device BSF(bus,slot,function) from virsh

```sh
virsh nodedev-dumpxml pci_0000_02_00_1
```
```xml
<device>
  <name>pci_0000_02_00_1</name>
  <path>/sys/devices/pci0000:00/0000:00:03.0/0000:02:00.1</path>
  <parent>pci_0000_00_03_0</parent>
  <driver>
    <name>tg3</name>
  </driver>
  <capability type='pci'>
    <domain>0</domain>
    <bus>2</bus>
    <slot>0</slot>
    <function>1</function>
    <product id='0x165f'>NetXtreme BCM5720 Gigabit Ethernet PCIe</product>
    <vendor id='0x14e4'>Broadcom Limited</vendor>
    <iommuGroup number='16'>
      <address domain='0x0000' bus='0x02' slot='0x00' function='0x1'/>
      <address domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>
    </iommuGroup>
    <numa node='0'/>
    <pci-express>
      <link validity='cap' port='0' speed='5' width='2'/>
      <link validity='sta' speed='5' width='1'/>
    </pci-express>
  </capability>
</device>
```

8. Restart guest

9. Check if devices are added to guest
Will get devices via "lspci" and "ip a"

