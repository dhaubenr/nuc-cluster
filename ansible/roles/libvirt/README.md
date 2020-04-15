# Networking overview for libvirt

## How it works

- topology:
  - each NUC has one primary wired ethernet device `enp0s25` or `eno1` (depending on NUC hardware)
  - primary ethernet device has two assigned IP addresses:
    - 192.168.3.1X (DHCP, assigned by DHCP server running on MacOSX workstation)
    - 192.168.10.10X (static, created by Ansible role `common`)
  - two libvirt networks per NUC:
    - default (mode `nat`, bridge `virbr0`, subnet `192.168.122.0/24`, installation default)
    - kubernetes (mode `nat`, bridge `virbr1`, subnet `192.168.20X.0/24`, created by Ansible role `libvirt_guests`):
      - supports DHCP with IP range `192.168.20X.50` to `192.168.20X.254`
      - support fixed DHCP addresses for guests based on their MAC addresses:
        - MAC address `52:54:00:b0:0X:0Y` -> guest name `nucX-k8s-Y` -> IP address `192.168.20X.1Y`
  - each libvirt guest uses network `kubernetes` only, with target device `vnet0`

- routing:
  - every NUC must have a route to each other NUC's `kubernetes` libvirt network via the other NUC's secondary static IP address, e.g.:
    - `ip -4 route add 192.168.20X.0/24 via 192.168.10.10X`

## How it's configured

- Ansible role `libvirt_guests` takes care of creating the libvirt network as well as the guests (aka 'domains')