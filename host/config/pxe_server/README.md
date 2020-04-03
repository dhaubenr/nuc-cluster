# Install Ubuntu 18.04 LTS via PXE

These are setup instructions for a custom PXE server on MacOSX for Ubuntu 18.04 LTS.

## Host workstation setup

### Software prequisites

- `brew install jq`
- `pip3 install j2cli[yaml]` (installed globally)
- `pip3 install yq` (installed globally)

### Guide

This guide assumes that you're using your MacOSX workstation as the internet gateway host for
the Intel NUC cluster. This can be done using NAT (natural address translation) and IP forwarding between one of the workstation's internel network interfaces (e.g. Wi-Fi) and an external USB ethernet adapter (I found the only adapter to actually work is this one: [Anker USB 3.0 auf RJ45 10/100/1000 Gigabit Ethernet Adapter](https://www.amazon.de/gp/product/B00NPJV4YY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)).

The following steps will help you setting up the various required components on your MacOSX workstation to allow netbooting clients in Legacy (BIOS) and UEFI mode.

- used network interfaces: en0 (Wi-Fi) -> en11 (USB 10/100/1000 LAN))

- one-time setup:
  - assign static IP to adapter: `networksetup -setmanual "USB 10/100/1000 LAN" 192.168.3.1 255.255.255.0`
  - permanently enable IP forwarding: `echo "net.inet.ip.forwarding=1" | sudo tee -a /private/etc/sysctl.conf`
  - install and configure DHCP server:
    - create jinja2 input file `dhcdp.conf.json` with the following content (insert the MAC addresses of your actual Intel NUCs):

      ```json
      {
          "mac": {
              "nuc1": "aa:bb:cc:dd:ee:ff",
              "nuc2": "ff:ee:dd:cc:bb:aa",
              "nuc3": "aa:ff:bb:ee:cc:dd",
              "nuc4": "cc:dd:bb:ee:ff:aa"
          }
      }
      ```

    - `brew install isc-dhcp`
    - `sudo cp org.dhaubenr.dhcp.plist /Library/LaunchDaemons/ && sudo chown root:wheel /Library/LaunchDaemons/org.dhaubenr.dhcp.plist`
    - `j2 dhcpd.conf.j2 dhcpd.conf.json -o /usr/local/etc/dhcpd.conf`
  - install HTTP server:
    - `brew install nginx`
    - `sudo cp org.dhaubenr.nginx.plist /Library/LaunchDaemons/ && sudo chown root:wheel /Library/LaunchDaemons/org.dhaubenr.nginx.plist`
  - setup NAT for external USB ethernet adapter:
    - `cp nat-pf /usr/local/bin/nat-pf && sudo chown root:wheel /usr/local/bin/nat-pf && sudo chmod 755 /usr/local/bin/nat-pf`
    - `sudo cp nat-rules /private/etc/nat-rules && sudo chown root:wheel /private/etc/nat-rules`
    - `sudo cp org.dhaubenr.nat-pf.plist /Library/LaunchDaemons/ && sudo chown root:wheel /Library/LaunchDaemons/org.dhaubenr.nat-pf.plist`

- netboot.xyz configuration:
  - download netboot.xyz source: `cd /tmp && git clone https://github.com/netbootxyz/netboot.xyz.git`
  - build netboot.xyz using Docker: `cd /tmp/netboot.xyz && docker build -t localbuild -f Dockerfile-build . && docker run --rm -it -v $(pwd):/buildout localbuild`
  - copy netboot.xyz build artifacts to HTTP server root: `cd /tmp/netboot.xyz/buildout && cp -R * /usr/local/var/www`
  - put Legacy PXE bootloader file in tftp server root: `sudo cp /usr/local/var/www/ipxe/netboot.xyz.kpxe /private/tftpboot`
  - put UEFI PXE bootloader file in tftp server root: `sudo cp /usr/local/var/www/ipxe/netboot.xyz.efi /private/tftpboot`

- Ubuntu 18.04 LTS preseeded installation configuration:
  - create jinja2 input files `nucX.json` where X is the Intel NUC's corresponding index number (please note that you have to fill in the `user` values with something that actually makes sense):

    ```json
    {
        "host_name": "nucX",
        "ram_size": 16384,
        "user": {
            "fullname": "John Doe",
            "login": "jdoe",
            "password": "K33pAway!",
            "ssh_pub_key": "ssh-rsa NOTAREALKEY jdoe@workstation"
        }
    }
    ```
  
  - transform the preseed configuration template file using jinja2:

    ```bash
    mkdir -p /usr/local/var/www/preseed
    for i in $(seq 1 4); do j2 preseed.cfg.j2 nuc$i.json -o /usr/local/var/www/preseed/preseed_nuc$i.cfg; done;
    ```

- run:
  - start required services:

    ```bash
    sudo launchctl load -w /System/Library/LaunchDaemons/tftp.plist
    sudo launchctl load -w /Library/LaunchDaemons/org.dhaubenr.nginx.plist
    # before starting the nat-pf and dhcp services we need to connect the external ethernet adapter
    sudo launchctl load -w /Library/LaunchDaemons/org.dhaubenr.dhcp.plist
    sudo launchctl load -w /Library/LaunchDaemons/org.dhaubenr.nat-pf.plist
    ```

  - stop required services:

    ```bash
    sudo launchctl unload -w /System/Library/LaunchDaemons/tftp.plist
    sudo launchctl unload -w /Library/LaunchDaemons/org.dhaubenr.nginx.plist
    sudo launchctl unload -w /Library/LaunchDaemons/org.dhaubenr.dhcp.plist
    sudo launchctl unload -w /Library/LaunchDaemons/org.dhaubenr.nat-pf.plist
    ```

- operate:
  - inspect DHCP server logs: `sudo log stream --info --debug --predicate "process == 'dhcpd'"`

## Launch network installation on Intel NUC

- start the Intel NUC and enter it's BIOS using **F2**
- uncheck option 'Boot Network Devices Last'
- either enable 'Legacy Boot' or 'PXE Boot'
- reboot the Intel NUC and press **F12** to initiate booting from the network using your workstation as PXE server