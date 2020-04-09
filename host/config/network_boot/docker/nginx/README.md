# nginx

This is a fairly simple Docker image that runs a `nginx` instance
which is used to host Ubuntu network installation files for the Intel NUCs.

## Software prerequisites

- Docker Desktop for MacOSX, version 2.2 or later
- `brew install jq`
- `brew install gnu-tar`
- `pip3 install j2cli[yaml]` (installed globally)
- `pip3 install yq` (installed globally)

## Build

Simply build the Docker image in this directory running:

```bash
docker build . -t nuc-nginx
```

## Run

Create a Docker volume to persist the HTTP data that is to be served by this container: `docker volume create nuc-nginx-www`.
Afterwards you can run a container like this:

```bash
docker run -d -p 8080:80 --restart=always -v nuc-nginx-www:/usr/share/nginx/html --name nuc-nginx nuc-nginx
```

This will run the nginx Docker container in the background, listening on port 8080 of the Docker host (your MacOSX workstation). Upon boot of your local MacOSX workstation the Docker container will automatically be started.

## Configure

First create jinja2 input files for each Intel NUC, named `nucX.json` (X being the index number of the respective Intel NUC) with the following content. Make sure to insert the correct values for the Intel NUC hardware as well as for the target user. For reference see [Hardware](../../../../../README.md).

```json
{
    "host_name": "nucX",
    "ram_size": 16384,
    "installation_proxy": "http://192.168.3.1:3142",
    "user": {
        "fullname": "John Doe",
        "login": "jdoe",
        "password": "K33pAway!",
        "ssh_pub_key": "ssh-rsa NOTAREALKEY jdoe@local-macosx"
    }
}
```

Copy the required netboot.xyz and Ubuntu 18.04 LTS netboot image files as well as the Intel NUC-specific Ubuntu 18.04 LTS preseed files to the HTTP server's root:

```bash
OLD_DIR=$(pwd)
# netboot.xyz installation
cd /tmp && git clone https://github.com/netbootxyz/netboot.xyz.git
cd /tmp/netboot.xyz && docker build -t localbuild -f Dockerfile-build . && docker run --rm -it -v /tmp/netboot.xyz:/buildout localbuild
cd /tmp/netboot.xyz/buildout && docker cp . nuc-nginx:/usr/share/nginx/html
# Ubuntu 18.04 LTS netboot image installation
docker exec -ti nuc-nginx /bin/sh -c "mkdir -p /usr/share/nginx/html/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/xen"
docker exec -ti nuc-nginx /bin/sh -c "cd /tmp && curl -sL -o netboot.tar.gz http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/netboot.tar.gz && cd /usr/share/nginx/html/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot && tar -zxf /tmp/netboot.tar.gz"
docker exec -ti nuc-nginx /bin/sh -c "cd /usr/share/nginx/html/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot && curl -sL -o mini.iso http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/mini.iso && curl -sL -o boot.img.gz http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/boot.img.gz"
docker exec -ti nuc-nginx /bin/sh -c "cd /usr/share/nginx/html/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/xen && curl -sL -o initrd.gz http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/xen/initrd.gz && curl -sL -o vmlinuz http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/xen/vmlinuz && curl -sL -o xm-debian.cfg http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/xen/xm-debian.cfg"
cd $OLD_DIR
# Intel NUC-specific preseed file installation
docker exec -ti nuc-nginx /bin/sh -c "mkdir -p /usr/share/nginx/html/ubuntu/preseed"
for i in $(seq 1 4); do j2 preseed_nuc.cfg.j2 nuc$i.json -o /tmp/preseed_nuc$i.cfg && docker cp /tmp/preseed_nuc$i.cfg nuc-nginx:/usr/share/nginx/html/ubuntu/preseed && rm -f /tmp/preseed$i.cfg; done;
```
