# tftp

This document describes how to configure the native (built-in) `tftp` instance on your local MacOSX workstation.

## Software prerequites

- `brew install jq`
- `brew install gnu-tar`
- `pip3 install j2cli[yaml]` (installed globally)
- `pip3 install yq` (installed globally)

## Configure

First create jinja2 input files for each Intel NUC, named `nucX.json` (X being the index number of the respective Intel NUC) with the following content. Make sure to insert the correct index number and network device name. For reference see [Hardware overview](../../../../../README.md).

```json
{
    "host_name": "nucX",
    "network_device": "[enp0s25|eno1]"
}
```

Configure your built-in native instance of `tftp` using the following set of commands:

```bash
mkdir -p /usr/local/var/tftpboot
sudo cp org.dhaubenr.tftp.plist /Library/LaunchDaemons/ && sudo chown root:wheel /Library/LaunchDaemons/org.dhaubenr.tftp.plist
```

Copy the required netboot.xyz and Intel NUC-specific iPXE scripts to the TFTP server's root directory:

```bash
OLD_DIR=$(pwd)
# netboot.xyz installation
cp boot.cfg /usr/local/var/tftpboot
cd /tmp && git clone https://github.com/netbootxyz/netboot.xyz.git
cd /tmp/netboot.xyz && docker build -t localbuild -f Dockerfile-build . && docker run --rm -it -v /tmp/netboot.xyz:/buildout localbuild
cd /tmp/netboot.xyz/buildout && cp menu.ipxe linux.ipxe ubuntu.ipxe ipxe/netboot.xyz.efi ipxe/netboot.xyz.kpxe ipxe/netboot.xyz-undionly.kpxe /usr/local/var/tftpboot
cd $OLD_DIR
# Intel NUC-specific iPXE script installation
for i in $(seq 1 4); do j2 HOSTNAME-nuc.ipxe.j2 nuc$i.json -o /usr/local/var/tftpboot/HOSTNAME-nuc$i.ipxe; done;
```

## Usage

To start and stop the `tftp` server instance, run either of the following commands:

```bash
# start tftp
sudo launchctl load -w /Library/LaunchDaemons/org.dhaubenr.tftp.plist
# stop tftp
sudo launchctl unload -w /Library/LaunchDaemons/org.dhaubenr.tftp.plist
```
