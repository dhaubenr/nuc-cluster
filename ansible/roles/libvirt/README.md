# Networking overview for libvirt

## How it works

- topology:
  - MacOSX host provides one class-c subnet:
    - 192.168.3.0/24
    - 192.168.3.1 is assigned to the external USB ethernet adapter `USB 10/100/1000 LAN`
  - host subnet is divided into 8 blocks, using the subnet mask `/27`:
    - 192.168.3.0/27   (192.168.3.0   - 192.168.3.31)  [ reserved for MacOSX host ]
    - 192.168.3.32/27  (192.168.3.32  - 192.168.3.63)
    - 192.168.3.64/27  (192.168.3.64  - 192.168.3.95)
    - 192.168.3.96/27  (192.168.3.96  - 192.168.3.127)
    - 192.168.3.128/27 (192.168.3.128 - 192.168.3.159)
    - 192.168.3.160/27 (192.168.3.160 - 192.168.3.191)
    - 192.168.3.192/27 (192.168.3.192 - 192.168.3.223)
    - 192.168.3.224/27 (192.168.3.224 - 192.168.3.255) [ reserved for MacOSX host ]
  - each NUC has one primary wired ethernet device `eno1` (device name depends on actual NUC hardware)
  - each NUC is assigned to one of the _free_ host subnet blocks (excluding the reserved blocks)
  - NUC primary ethernet device has one assigned IP address:
    - 192.168.3.XXX (_static_ DHCP, assigned by DHCP server running on MacOSX workstation using the NUC's ethernet device MAC address)
    - `XXX` refers to the starting address of the assigned subnet block
  - two libvirt networks per NUC:
    - default (mode `nat`, bridge `virbr0`, subnet `192.168.122.0/24`, installation default)
    - kubernetes (mode `routed`, bridge `virbr1`, subnet `192.168.3.XXX/27`, created by Ansible role `libvirt_guests`):
      - supports DHCP with IP range according to the mapping listed above
      - supports _static_ DHCP addresses for guests based on their MAC addresses:
        - MAC address `52:54:00:7e:0X:0Y` -> guest name `nucX-k8s-Y`
  - each libvirt guest uses network `kubernetes` only

## Maximum supported hosts and guests

- theoretically the above setup enables the use of the following hosts and guest domains:
  - 6 Intel NUCs
  - 28 libvirt guests per Intel NUC

## How it's configured

- Ansible role `libvirt` takes care of creating the libvirt network as well as the guests (aka 'domains')
