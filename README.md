# nuc-cluster

Compilation of resources (scripts, snippets, instructions) to setup a multi-purpose Linux cluster on Intel NUCs

## Hardware overview

| Type      | Model      | CPU  | RAM    | DISK1 (NVMe) | DISK2 (SATA SSD) | Wired Ethernet Device | NODE INDEX |
|-----------|------------|-----:|-------:|-------------:|-----------------:|----------------------:|-----------:|
| Intel NUC | NUC7i5DNHE | 2(4) | 32GB   | 256GB        | 512GB            | eno1                  | 1          |
| Intel NUC | NUC7i5BNH  | 2(4) | 32GB   | 256GB        | 500GB            | eno1                  | 2          |
| Intel NUC | NUC8i5BEH  | 4(8) | 32GB   | 256GB        | 512GB            | eno1                  | 3          |
| Intel NUC | NUC8i3BEH  | 2(4) | 32GB   | 256GB        | 512GB            | eno1                  | 4          |

- Netgear Gigabit Ethernet Switch GS305E (managed, 5 ports)
- UPerfect Portable HDMI Display (7 inch, resolution: 1024*600)
- SGEYR 4K HDMI Switch (4 ports in, 1 port out)
- DELOCK USB Switch (1 port in, 4 ports out)
- Logitech K400 Plus Wireless Keyboard (w/ touchpad)
- lots of cables (ethernet, power, HDMI, USB)

## Host workstation setup

This guide assumes that you're using your MacOSX workstation as the internet gateway host for
the Intel NUC cluster. This can be done using NAT (natural address translation) and IP forwarding between one of the workstation's internel network interfaces (e.g. Wi-Fi) and an external USB ethernet adapter (I found the only adapter to actually work is this one: [Anker USB 3.0 auf RJ45 10/100/1000 Gigabit Ethernet Adapter](https://www.amazon.de/gp/product/B00NPJV4YY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)).

Follow the instructions outlined in the following READMEs to setup NAT and DHCP on your MacOSX workstation:

- [nat-pf](./host/config/network_boot/native/nat-pf/README.md)
- [isc-dhcp](./host/config/network_boot/native/isc-dhcp/README.md)

## Intel NUC Ubuntu 18.04 LTS installation

See [Install Ubuntu 18.04 LTS via iPXE](host/config/network_boot/README.md) for more information.

## MacOSX workstation setup

Whenever you want to use your Intel NUC cluster and thus share the network connection of your MacOSX workstation's primary network adapter with the cluster nodes make sure the following services are running:

- LaunchDaemon `org.dhaubenr.nat-pf.plist`
- LaunchDaemon `org.dhaubenr.dhcp.plist`

If you want to use the Intel NUC's Wake-On-LAN feature (must be configured in the BIOS) you can make a copy of the included script file `host/scripts/wakenuc` and use it like this:

```bash
brew install wakeonlan
cp host/scripts/wakenuc /usr/local/bin/wakenuc && chmod a+x /usr/local/bin/wakenuc
wakenuc <nuc_index_number>
```

To be able to address individual Intel NUCs with a logical network name, configure your workstation's `/etc/hosts` file by adding the following entries:

```text
192.168.3.11   nuc1
192.168.3.12   nuc2
192.168.3.13   nuc3
192.168.3.14   nuc4
```

To be able to SSH into the Intel NUC's operating system you can use the `host/config/ssh_config` file included in this repository as an example to adapt your workstation's `$HOME/.ssh/config` file.

In case you want to use `tmuxinator` (<https://github.com/tmuxinator/tmuxinator>) to administer your Intel NUC cluster make a copy of the included file `host/config/tmuxinator.yml` on your workstation:

```bash
cp config/tmuxinator.yml .tmuxinator.yml
```

In case you want to use `dsh` (<https://www.ostechnix.com/dsh-run-linux-command-multiple-hosts-time/>) configure it on your workstation using the following commands:

```bash
mkdir -p $HOME/.dsh/group
cp host/config/dsh.conf $HOME/.dsh
touch $HOME/.dsh/machines.list
for i in $(seq 1 4); do echo "nuc$i" >> $HOME/.dsh/machines.list; done
ln -sf ../machines.list $HOME/.dsh/group/all
echo "nuc1" >> $HOME/.dsh/group/nuc.master
for i in $(seq 2 4); do echo "nuc$i" >> $HOME/.dsh/group/nuc.worker; done
```

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
  
  # provision everything (setup and libvirt)
  ansible-playbook -v -i inventory site.yml --extra-vars "nuc_user=$(whoami)" --ask-become-pass [--limit nucs[0]]

  # provision setup only
  ansible-playbook -v -i inventory setup.yml --extra-vars "nuc_user=$(whoami)" --ask-become-pass [--limit nucs[0]]
  # or use tags
  ansible-playbook -v -i inventory site.yml --extra-vars "nuc_user=$(whoami)" --tags "common,development,docker,vagrant,kubernetes,user,finish" --ask-become-pass [--limit nucs[0]]

  # provision libvirt only (requires 'setup')
  ansible-playbook -v -i inventory libvirt.yml --extra-vars "nuc_user=$(whoami)" --ask-become-pass [--limit nucs[0]]
  # or use tags
  ansible-playbook -v -i inventory site.yml --extra-vars "nuc_user=$(whoami)" --tags "libvirt" --ask-become-pass [--limit nucs[0]]

  # de-provision (rollback) libvirt
  ansible-playbook -v -i inventory rollback.yml --extra-vars "nuc_user=$(whoami)" --ask-become-pass [--limit nucs[0]]
  ```
