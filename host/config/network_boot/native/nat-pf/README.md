# nat-pf

This document describes how to install and configure a native `nat-pf` service on your local MacOSX workstation.
This service will handle NAT (natural adress translation) for the Intel NUCs attached to you local workstation
via the external USB ethernet adapter for as long as it's activated.

The service configuration assumes that you want NAT to happen between the network interface `en0` (typically your MacOSX workstation's primary wireless etherner adapter) and the Intel NUC subnet `192.168.3.0/24`.

## Configure

First make sure that the external USB ethernet adapter has been configured with a static IP address for the subnet you want to use for your Intel NUCs:

```bash
networksetup -setmanual "USB 10/100/1000 LAN" 192.168.3.1 255.255.255.0
```

This will set the IP address and subnet mask for the adapter accordingly. In case you're not sure whether this configuration is correct and has been applied to the adapter you can always check using MacOSX's System Preferences panel. Simply navigate to `System Preferences -> Network -> USB 10/100/1000 LAN` and compare the active settings with the ones from the given command. Make sure they match.

Afterwards put the service configuration files in place using the following set of commands:

```bash
sudo cp org.dhaubenr.nat-pf.plist /Library/LaunchDaemons/ && sudo chown root:wheel /Library/LaunchDaemons/org.dhaubenr.nat-pf.plist
sudo cp nat-rules /private/etc/nat-rules
cp nat-pf /usr/local/bin/nat-pf && chmod a+x /usr/local/bin/nat-pf
```

## Usage

To start and stop the `nat-pf` service, run either of the following commands:

```bash
# start nat-pf
sudo launchctl load -w /Library/LaunchDaemons/org.dhaubenr.nat-pf.plist
# stop nat-pf
sudo launchctl unload -w /Library/LaunchDaemons/org.dhaubenr.nat-pf.plist
```
