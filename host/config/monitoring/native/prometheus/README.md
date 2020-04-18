# prometheus

This document describes how to install and configure a native `prometheus` instance on your local MacOSX workstation.

## Software prerequites

- `brew install jq`
- `brew install gnu-tar`
- `pip3 install j2cli[yaml]` (installed globally)
- `pip3 install yq` (installed globally)

## Install

Install the `prometheus` package via `brew` running:

```bash
brew install prometheus
```

## Configure

First create a jinja2 input file `prometheus.yml.json` with the following content (insert the IP addresses of your actual Intel NUCs):

```json
{
    "endpoints": [
        { "host": "nuc1", "ip": "192.168.3.XXX", "port": 9100 },
        { "host": "nuc2", "ip": "192.168.3.XXX", "port": 9100 },
        { "host": "nuc3", "ip": "192.168.3.XXX", "port": 9100 },
        { "host": "nuc4", "ip": "192.168.3.XXX", "port": 9100 }
    ]
}
```

Configure your local native instance of `prometheus` using the following set of commands:

```bash
mkdir -p /usr/local/var/prometheus
cp org.dhaubenr.prometheus.plist ~/Library/LaunchAgents/
j2 prometheus.yml.j2 prometheus.yml.json -o /usr/local/etc/prometheus.yml
```

## Usage

To start and stop the `prometheus` server instance, run either of the following commands:

```bash
# start prometheus
launchctl load -w ~/Library/LaunchAgents/org.dhaubenr.prometheus.plist
# stop prometheus
launchctl unload -w ~/Library/LaunchAgents/org.dhaubenr.prometheus.plist
```

The Prometheus time series database is stored at `/usr/local/var/prometheus`.
