url --url http://pi1.mac.wales/centos7
install

lang en
keyboard uk
skipx

network --hostname=node.local

# -----------------------------------------------

network --device=eth0 --noipv6 --bootproto=dhcp

# -----------------------------------------------

authconfig --useshadow --passalgo=sha256 --kickstart

rootpw "letmein"
user --name=rescue --plaintext --password letmein

timezone --utc UTC

bootloader --location=mbr --append="nofb quiet splash=quiet" 

zerombr
clearpart --all

# -----------------------------------------------

part /boot --size=256 --ondisk=vda
part pv.01 --size=1   --ondisk=vda --grow

volgroup linux pv.01

logvol /              --fstype=xfs --name=root          --vgname=linux --size=3192
logvol /home          --fstype=xfs --name=home          --vgname=linux --size=2048
logvol /tmp           --fstype=xfs --name=tmp           --vgname=linux --size=256
logvol /opt           --fstype=xfs --name=opt           --vgname=linux --size=2048
logvol /var           --fstype=xfs --name=var           --vgname=linux --size=1024
logvol /var/log       --fstype=xfs --name=var_log       --vgname=linux --size=256
logvol /var/log/audit --fstype=xfs --name=var_log_audit --vgname=linux --size=256

# -----------------------------------------------

text
reboot

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
  echo "rescue ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/rescue
%end
