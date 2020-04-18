# grafana

This document describes how to install and configure a native `grafana` instance on your local MacOSX workstation.

## Software prerequites

- `brew install jq`
- `brew install gnu-tar`
- `pip3 install j2cli[yaml]` (installed globally)
- `pip3 install yq` (installed globally)

## Install

Install the `grafana` package via `brew` running:

```bash
brew install grafana
```

## Configure

Configure your local native instance of `grafana` using the following set of commands:

```bash
cp org.dhaubenr.grafana.plist ~/Library/LaunchAgents/
```

## Usage

To start and stop the `grafana` server instance, run either of the following commands:

```bash
# start grafana
launchctl load -w ~/Library/LaunchAgents/org.dhaubenr.grafana.plist
# stop grafana
launchctl unload -w ~/Library/LaunchAgents/org.dhaubenr.grafana.plist
```
