cdrom
install

lang en
keyboard uk
skipx

network --hostname=node.local

# -----------------------------------------------

network --device=enp0s3 --noipv6 --bootproto=static --ip=10.0.30.200 --netmask=255.255.255.0
network --device=enp0s8 --noipv6 --bootproto=static --ip=10.0.40.200 --netmask=255.255.255.0 --gateway=10.0.40.1 --nameserver=10.0.40.1

# -----------------------------------------------

authconfig --useshadow --passalgo=sha256 --kickstart

rootpw "letmein"
user --name=rescue --plaintext --password letmein

timezone --utc UTC

bootloader --location=mbr --append="nofb quiet splash=quiet" 

zerombr
clearpart --all

# -----------------------------------------------

part /boot --size=256 --ondisk=sda
part pv.01 --size=1   --ondisk=sda --grow

volgroup linux pv.01

logvol /              --fstype=xfs --name=root          --vgname=linux --size=2048
logvol /home          --fstype=xfs --name=home          --vgname=linux --size=2560
logvol /tmp           --fstype=xfs --name=tmp           --vgname=linux --size=256
logvol /opt           --fstype=xfs --name=opt           --vgname=linux --size=512
logvol /var           --fstype=xfs --name=var           --vgname=linux --size=512
logvol /var/log       --fstype=xfs --name=var_log       --vgname=linux --size=256
logvol /var/log/audit --fstype=xfs --name=var_log_audit --vgname=linux --size=256

# -----------------------------------------------

text
reboot --eject

%packages --ignoremissing
yum
yum-utils
dhclient
bash-completion 
bash-completion-extras
wget
vim
git
@Core
%end

%post --log=/root/kickstart-post.log
  echo "UseDNS no" >> /etc/ssh/sshd_config
  echo "10.0.40.200 node.foo.local node" >> /etc/hosts
  echo "rescue ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/rescue
%end
