# apt-cacher-ng

This is a fairly simple Docker image that runs a `apt-cacher-ng` instance
which can be used to speed up the Intel NUC network installations off of the
local MacOSX workstation.

## Prerequisites

- Docker Desktop for MacOSX, version 2.2 or later

## Build

Simply build the Docker image in this directory running:

```bash
docker build . -t nuc-acng
```

## Run

In order to persist the cached APT data you'll need a Docker volume. Simply create one by running `docker volume create nuc-acng`.
Afterwards you can run a container like this:

```bash
docker run -d -p 3142:3142 --restart=always -v nuc-acng:/var/cache/apt-cacher-ng --name nuc-acng nuc-acng
```

This will run the apt-cacher-ng Docker container in the background, listening on port 3142 of the Docker host (your MacOSX workstation).

## Usage

In order to use it you can simply set the option `installation_proxy` in your Intel NUC jinja2 configuration file `nucX.json?` to `http://192.168.3.1:3142`. If you don't wanna use it, leave the value for `installation_proxy` empty.
