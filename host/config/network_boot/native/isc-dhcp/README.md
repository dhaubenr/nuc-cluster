# isc-dhcp

This document describes how to install and configure a native `isc-dhcp` instance on your local MacOSX workstation.

## Software prerequites

- `brew install jq`
- `brew install gnu-tar`
- `pip3 install j2cli[yaml]` (installed globally)
- `pip3 install yq` (installed globally)

## Install

Install the `isc-dhcp` package via `brew` running:

```bash
brew install isc-dhcp
```

## Configure

First create a jinja2 input file `dhcdp.conf.json` with the following content (insert the MAC addresses of your actual Intel NUCs):

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

Configure your local native instance of `isc-dhcp` using the following set of commands:

```bash
sudo cp org.dhaubenr.dhcp.plist /Library/LaunchDaemons/ && sudo chown root:wheel /Library/LaunchDaemons/org.dhaubenr.dhcp.plist
j2 dhcpd.conf.j2 dhcpd.conf.json -o /usr/local/etc/dhcpd.conf
```

## Usage

To start and stop the `isc-dhcp` server instance, run either of the following commands:

```bash
# start isc-dhcp
sudo launchctl load -w /Library/LaunchDaemons/org.dhaubenr.dhcp.plist
# stop isc-dhcp
sudo launchctl unload -w /Library/LaunchDaemons/org.dhaubenr.dhcp.plist
```

To inspect the `isc-dhcp` server instance logs, run:

```bash
sudo log stream --info --debug --predicate "process == 'dhcpd'"
```
