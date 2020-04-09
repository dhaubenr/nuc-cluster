# Install Ubuntu 18.04 LTS via iPXE

These are setup instructions for a custom iPXE server on MacOSX for Ubuntu 18.04 LTS.

## Guide

This guide assumes that you're using your MacOSX workstation as the internet gateway host for
the Intel NUC cluster. This can be done using NAT (natural address translation) and IP forwarding between one of the workstation's internal network interfaces (e.g. Wi-Fi) and an external USB ethernet adapter (I found the only adapter to actually work is this one: [Anker USB 3.0 auf RJ45 10/100/1000 Gigabit Ethernet Adapter](https://www.amazon.de/gp/product/B00NPJV4YY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)).

Once setup and activated the iPXE server allows netboot requests from Legacy (BIOS) and UEFI clients. The type of client is determined automatically by the DHCP server and handled by the TFTP server accordingly.

To setup the individual components of the iPXE server please follow the instructions in this folder's submodules. The following components are **mandatory**:

- [isc-dhcp](./native/isc-dhcp/README.md)
- [nat-pf](./native/nat-pf/README.md)
- [tftp](./native/tftp/README.md)
- [nginx](./docker/nginx/README.md)

The following components are **optional** (but recommended):

- [apt-cacher-ng](./docker/apt-cacher-ng/README.md)

Once you've installed and configured the individual components of the iPXE server make sure the following services are running whenever you want to use it for installing the attached Intel NUCs from the network:

- LaunchDaemon `org.dhaubenr.nat-pf.plist`
- LaunchDaemon `org.dhaubenr.dhcp.plist`
- LaunchDaemon `org.dhaubenr.tftp.plist`
- Docker container `nuc-nginx`
- Docker container `nuc-acng` (optional)
