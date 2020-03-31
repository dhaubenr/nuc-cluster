# Install Ubuntu 18.04 LTS via Legacy PXE

These are setup instructions for a Legacy PXE bootp/tftp server on MacOSX for Ubuntu 18.04 LTS.

## Host workstation setup

### Software prequisites

- brew install core-process/gnucpio/gnucpio
- brew install jq
- pip3 install j2cli[yaml] (installed globally)
- pip3 install yq (installed globally)

### Guide

This guide assumes that you're using your MacOSX workstation as the internet gateway host for
the Intel NUC cluster. This can be done using MacOSX's 'Internet Sharing' feature using an external USB ethernet adapter (I found the only adapter to actually work is this one: [Anker USB 3.0 auf RJ45 10/100/1000 Gigabit Ethernet Adapter](https://www.amazon.de/gp/product/B00NPJV4YY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)).
The Internet Sharing feature of MacOSX hands out DHCP addresses to connected clients for the subnet `192.168.2.X/24`. The MacOSX bootp server uses the following files for configuration and lease recording:

- /etc/bootpd.plist
- /etc/bootptab
- /private/var/db/dhcpd_leases

The built-in tftp server of MacOSX is hosting files out of this directory:

- /private/tftpboot

For the purpose of this project, Ubuntu 18.04 LTS (amd64) is the only installation source that is being offered by the Legacy PXE bootp/tftp server. Files can be downloaded from <http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/hwe-netboot/>, with `netboot.tar.gz` being the only file of interest (as it contains everything we need). Download and extract it like so:

```bash
cd /private/tftpboot
# download the latest Ubuntu 18.04 LTS netboot image
sudo wget http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/hwe-netboot/netboot.tar.gz
# extract the image
sudo tar -zxf netboot.tar.gz
# generate required data for bootpd
export PXELINUX0_DATA=$(printf %s00 `echo -n pxelinux.0 | xxd -p` | xxd -r -p | openssl base64)
```

## Starting the Legacy PXE bootp/tftp server

- starting point:
  - workstation is turned on and connected to Wi-Fi or primary ethernet landline
  - 'System Preferences -> Network -> Internet Sharing' is turned off
  - Netgear switch and Intel NUCs attached to external USB ethernet adapter are turned off

- ensure the external USB ethernet adapter is set to a static IP address in 'System Preferences -> Network -> USB 10/100/1000 LAN':
  - IP: 192.168.2.254
  - subnet: 255.255.255.0
  - gateway: 192.168.2.1

- connect external USB ethernet adapter
- turn on on Netgear switch
- turn on 'System Preferences -> Network -> Internet Sharing' from the primary network connection (either Wi-Fi or primary ethernet landline) to the external USB ethernet adapter 'USB 10/100/1000 LAN'
- append the following lines to the `<key>Subnets</key><array><dict>` element in file `/etc/bootpd.plist`:

  ```xml
                        <key>dhcp_option_66</key>
                        <string>192.168.2.254</string>
                        <key>dhcp_option_67</key>
                        <!-- the following value is identical
                             to $PXELINUX0_DATA (see prior instructions)
                        -->
                        <data>cHhlbGludXguMAA=</data>
  ```

- reload / restart bootp and tftp system daemons:

  ```bash
  sudo launchctl unload -w /System/Library/LaunchDaemons/{bootps,tftp}.plist
  sudo launchctl load -w /System/Library/LaunchDaemons/{bootps,tftp}.plist
  ```

## Launch network installation on Intel NUC

- start the Intel NUC and enter it's BIOS using **F2**
- uncheck option 'Boot Network Devices Last'
- make sure 'Legacy Boot' is enabled
- reboot the Intel NUC and press **F12** to initiate booting from the network using your workstation as Legacy PXE server

## Install Ubuntu 18.04 LTS on Intel NUC manually

- internationalization settings:
  - language: English
  - country: Germany
  - keyboard: auto-detect
  - language_code: en_US.UTF8
  - timezone: Europe/Berlin
- Ubuntu package server:
  - Germany
- disk layout:
  - auto-layout using whole disk using lvm
  - use internal NVMe disk as system drive
- use package auto updates:
  - no
- packages to be installed:
  - OpenSSH server
  - Basic Ubuntu server
- install GRUB boot loader to master boot record:
  - yes
  - use internal NVMe disk
- system clock is set to UTC:
  - yes

## Install Ubuntu 18.04 LTS on a (specific) Intel NUC using a preseed configuration

To be able to preseed (provide default installation presets) the Ubuntu 18.04 LTS installation we are modifiying the original Ubuntu netboot image that we've downloaded and extracted to `/private/tftpboot` (see instructions above). The netboot's `initrd.gz` file contains the preseed configuration files `preseed.cfg` that we will replace with our own file. Here's how to do it:

```bash
# the preseed.cfg jinja2 template file
export PRESEED_J2_TEMPLATE=$(pwd)/preseed-ubuntu-18.04-server-amd64.cfg.j2
# the jinja2 input data for the preseed.cfg template
export PRESEED_J2_INPUT=$(pwd)/nuc1.json
cd /private/tftpboot
test -d preseeded || sudo mkdir preseeded
cd preseeded
# extract the original initrd.gz from the Ubuntu netboot image (needs to be done only once, hence the 'test' safeguard)
test -d usr || (gzip -d < ../ubuntu-installer/amd64/initrd.gz | sudo gnucpio -id)
# create the final preseed.cfg file from the jinja2 template
sudo j2 $PRESEED_J2_TEMPLATE $PRESEED_J2_INPUT -o preseed.cfg
# backup the original initrd.gz file (only done once, hence the 'test' safeguard)
test -f ../ubuntu-installer/amd64/initrd.gz.orig || sudo cp ../ubuntu-installer/amd64/initrd.gz ../ubuntu-installer/amd64/initrd.gz.orig
# package the new initrd.gz file and replace the original one
(find . | sudo gnucpio -o -H newC | sudo gzip) | sudo tee ../ubuntu-installer/amd64/initrd.gz > /dev/null
```

The jinja2 input data file `nuc1.json` needs to look like this for things to work properly (please note that you have to fill in the `user` values with something that actually makes sense):

```json
{
    "host_name": "nuc1",
    "ram_size": 16384,
    "user": {
        "fullname": "John Doe",
        "login": "jdoe",
        "password": "K33pAway!",
        "ssh_pub_key": "ssh-rsa NOTAREALKEY jdoe@workstation"
    }
}
```

## Shutdown tftp server after Ubuntu installation on Intel NUC is done

```bash
sudo launchctl unload -w /System/Library/LaunchDaemons/tftp.plist
```
