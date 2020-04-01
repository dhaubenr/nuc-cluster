# nuc-cluster

Compilation of resources (scripts, snippets, instructions) to setup a multi-purpose Linux cluster on Intel NUCs

## Hardware

| Type      | Model      | CPU  | RAM    | DISK1 (NVMe) | DISK2 (SATA SSD) | NODE INDEX |
|-----------|------------|------|-------:|-------------:|-----------------:|-----------:|
| Intel NUC | NUC5i3RYH  | 2(4) | 16GB   | 128GB        | 480GB            | 1          |
| Intel NUC | NUC7i5BNH  | 2(4) | 32GB   | 256GB        | 500GB            | 2          |
| Intel NUC | NUC8i5BEH  | 4(8) | 32GB   | 256GB        | 512GB            | 3          |
| Intel NUC | NUC8i3BEH  | 2(4) | 32GB   | 256GB        | 512GB            | 4          |

- Netgear Gigabit Ethernet Switch GS305E (managed, 5 ports)
- UPerfect Portable HDMI Display (7 inch, resolution: 1024*600)
- SGEYR 4K HDMI Switch (4 ports in, 1 port out)
- DELOCK USB Switch (1 port in, 4 ports out)
- Logitech K400 Plus Wireless Keyboard (w/ touchpad)
- lots of cables (ethernet, power, HDMI, USB)

### Software prequisites

- pip3 install j2cli[yaml] (installed globally)

## Host workstation setup

This guide assumes that you're using your MacOSX workstation as the internet gateway host for
the Intel NUC cluster. This can be done using MacOSX's 'Internet Sharing' feature using an external USB Ethernet adapter (I found the only adapter to actually work is this one: [Anker USB 3.0 auf RJ45 10/100/1000 Gigabit Ethernet Adapter](https://www.amazon.de/gp/product/B00NPJV4YY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)).
The Internet Sharing feature of MacOSX hands out DHCP addresses to connected clients for the subnet `192.168.2.X/24`. The DHCP server uses the following files for configuration and lease recording:

- /etc/bootpd.plist
- /etc/bootptab
- /private/var/db/dhcpd_leases

In order to ensure that all Intel NUCs that are attached via a switch to the workstation's external USB ethernet adapter get a static IP address assigned by the 'Internet Sharing' feature do this:

```bash
# backup the original /etc/bootptab file
test -f /etc/bootptab && sudo cp /etc/bootptab /etc/bootptab.bak
# the bootptab jinja2 template file
export BOOTPTAB_J2_TEMPLATE=$(pwd)/host/config/bootptab.j2
# the jinja2 input data for the preseed.cfg template
export BOOTPTAB_J2_INPUT=$(pwd)/host/config/bootptab.json
sudo j2 $BOOTPTAB_J2_TEMPLATE $BOOTPTAB_J2_INPUT -o /etc/bootptab
sudo chown root:wheel /etc/bootptab
```

The jinja2 input data file `bootptab.json` needs to look like this for things to work properly (please note that you have to fill in the `mac` values with something that actually makes sense):

```json
{
    "mac": {
        "nuc1": "aa:bb:00:cc:11:dd",
        "nuc2": "dd:11:cc:00:bb:aa",
        "nuc3": "aa:00:bb:11:cc:dd",
        "nuc4": "00:bb:aa:dd:11:cc"
    }
}
```

If you want to use the Intel NUC's Wake-On-LAN feature (must be configured in the BIOS) you can make a copy of the included script file `host/scripts/wakenuc` and use it like this:

```bash
cp host/scripts/wakenuc /usr/local/bin/wakenuc && chmod a+x /usr/local/bin/wakenuc
wakenuc <nuc_index_number>
```

Configure your workstation's `/etc/hosts` file by adding the following entries:

```text
192.168.2.101   nuc1
192.168.2.102   nuc2
192.168.2.103   nuc3
192.168.2.104   nuc4
```

## Intel NUC Ubuntu 18.04 LTS installation

See [Install Ubuntu 18.04 LTS via PXE](host/pxe_server/README.md) for more information.

## Provision Intel NUCs using Ansible

- ensure you have Python 3 and the module `virtualenv` installed globally
- create a new Python virtualenv in this repository's root directory:

```bash
python3 -m virtualenv env
```

- activate the newly created Python virtualenv and install required Python modules:

```bash
source env/bin/activate
pip3 install ansible ansible-lint
```

- use Ansible to provision Intel NUCs:

```bash
source env/bin/activate
cd ansible
# if you want to provision specific NUCs use the '--limit' option
# make sure 'nuc_user' refers to the preseeded user in Ubuntu 18.04 LTS
ansible-playbook -i inventory nucs.yml --extra-vars "nuc_user=$(whoami)" --ask-become-pass [--limit nucs[0]]
```

- afterwards run the following steps on your workstation:
  - use the `host/config/ssh_config` file in this repository as an example to adapt your workstation's `$HOME/.ssh/config` file to include all Intel NUCs
  - copy the SSH helper scripts `host/scripts/ssh-colorizer` and `host/scripts/pwait` to a directory that is included in your local workstation's PATH variable:

  ```bash
  cp scripts/pwait /usr/local/bin/pwait && chmod a+x /usr/local/bin/pwait
  cp scripts/ssh-colorizer /usr/local/bin/ssh-colorizer && chmod a+x /usr/local/bin/ssh-colorizer
  ```

  - if you want to use `tmuxinator` (optional), make a copy of the file `host/config/tmuxinator.yml` on your workstation:

  ```bash
  cp config/tmuxinator.yml .tmuxinator.yml
  ```

  - if you want to use `dsh` (optional), configure it on your workstation using the following commands:

  ```bash
  mkdir -p $HOME/.dsh/group
  cp host/config/dsh.conf $HOME/.dsh
  touch $HOME/.dsh/machines.list
  for i in $(seq 1 4); do echo "nuc$i" >> $HOME/.dsh/machines.list; done
  ln -sf ../machines.list $HOME/.dsh/group/all
  echo "nuc1" >> $HOME/.dsh/group/nuc.master
  for i in $(seq 2 4); do echo "nuc$i" >> $HOME/.dsh/group/nuc.worker; done
  ```
