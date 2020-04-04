# nuc-cluster

Compilation of resources (scripts, snippets, instructions) to setup a multi-purpose Linux cluster on Intel NUCs

## Hardware

| Type      | Model      | CPU  | RAM    | DISK1 (NVMe) | DISK2 (SATA SSD) | Wired Ethernet Device | NODE INDEX |
|-----------|------------|------|-------:|-------------:|-----------------:|-----------------------|-----------:|
| Intel NUC | NUC5i3RYH  | 2(4) | 16GB   | 128GB        | 480GB            | enp0s25               | 1          |
| Intel NUC | NUC7i5BNH  | 2(4) | 32GB   | 256GB        | 500GB            | eno1                  | 2          |
| Intel NUC | NUC8i5BEH  | 4(8) | 32GB   | 256GB        | 512GB            | eno1                  | 3          |
| Intel NUC | NUC8i3BEH  | 2(4) | 32GB   | 256GB        | 512GB            | eno1                  | 4          |

- Netgear Gigabit Ethernet Switch GS305E (managed, 5 ports)
- UPerfect Portable HDMI Display (7 inch, resolution: 1024*600)
- SGEYR 4K HDMI Switch (4 ports in, 1 port out)
- DELOCK USB Switch (1 port in, 4 ports out)
- Logitech K400 Plus Wireless Keyboard (w/ touchpad)
- lots of cables (ethernet, power, HDMI, USB)

### Software prequisites

- `brew install wakeonlan`
- `pip3 install j2cli[yaml]` (installed globally)
- `pip3 install yq` (installed globally)

## Host workstation setup

This guide assumes that you're using your MacOSX workstation as the internet gateway host for
the Intel NUC cluster. This can be done using NAT (natural address translation) and IP forwarding between one of the workstation's internel network interfaces (e.g. Wi-Fi) and an external USB ethernet adapter (I found the only adapter to actually work is this one: [Anker USB 3.0 auf RJ45 10/100/1000 Gigabit Ethernet Adapter](https://www.amazon.de/gp/product/B00NPJV4YY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)).

Follow these steps to configure NAT and IP forwarding on your MacOSX workstation:

- one-time setup:
  - assign static IP to adapter: `networksetup -setmanual "USB 10/100/1000 LAN" 192.168.3.1 255.255.255.0`
  - permanently enable IP forwarding: `echo "net.inet.ip.forwarding=1" | sudo tee -a /private/etc/sysctl.conf`
  - install and configure DHCP server:
    - create jinja2 input file `host/config/pxe_server/dhcdp.conf.json` with the following content (insert the MAC addresses of your actual Intel NUCs):

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

    - `brew install isc-dhcp`
    - `sudo cp host/config/pxe_server/org.dhaubenr.dhcp.plist /Library/LaunchDaemons/ && sudo chown root:wheel /Library/LaunchDaemons/org.dhaubenr.dhcp.plist`
    - `j2 host/config/pxe_server/dhcpd.conf.j2 host/config/pxe_server/dhcpd.conf.json -o /usr/local/etc/dhcpd.conf`
  - setup NAT for external USB ethernet adapter:
    - `cp host/config/pxe_server/nat-pf /usr/local/bin/nat-pf && sudo chown root:wheel /usr/local/bin/nat-pf && sudo chmod 755 /usr/local/bin/nat-pf`
    - `sudo cp host/config/pxe_server/nat-rules /private/etc/nat-rules && sudo chown root:wheel /private/etc/nat-rules`
    - `sudo cp host/config/pxe_server/org.dhaubenr.nat-pf.plist /Library/LaunchDaemons/ && sudo chown root:wheel /Library/LaunchDaemons/org.dhaubenr.nat-pf.plist`

- run:
  - start required services:

    ```bash
    sudo launchctl load -w /Library/LaunchDaemons/org.dhaubenr.dhcp.plist
    sudo launchctl load -w /Library/LaunchDaemons/org.dhaubenr.nat-pf.plist
    ```

  - stop required services:

    ```bash
    sudo launchctl unload -w /Library/LaunchDaemons/org.dhaubenr.dhcp.plist
    sudo launchctl unload -w /Library/LaunchDaemons/org.dhaubenr.nat-pf.plist
    ```

If you want to use the Intel NUC's Wake-On-LAN feature (must be configured in the BIOS) you can make a copy of the included script file `host/scripts/wakenuc` and use it like this:

```bash
cp host/scripts/wakenuc /usr/local/bin/wakenuc && chmod a+x /usr/local/bin/wakenuc
wakenuc <nuc_index_number>
```

Configure your workstation's `/etc/hosts` file by adding the following entries:

```text
192.168.3.11   nuc1
192.168.3.12   nuc2
192.168.3.13   nuc3
192.168.3.14   nuc4
```

## Intel NUC Ubuntu 18.04 LTS installation

See [Install Ubuntu 18.04 LTS via PXE](host/config/pxe_server/README.md) for more information.

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
