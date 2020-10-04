url --url http://pi1.mac.wales/centos7
# repo --name="os"      --baseurl=http://mirrorsnap.centos.org/20190807/centos/7/os/x86_64/ --cost=100
# repo --name="updates" --baseurl=http://mirrorsnap.centos.org/20190807/centos/7/updates/x86_64/ --cost=100
# repo --name="extras"  --baseurl=http://mirrorsnap.centos.org/20190807/centos/7/extras/x86_64/ --cost=100
install

lang en
keyboard uk
skipx

# -----------------------------------------------

network --hostname=node.local
network --device=eth0 --noipv6 --bootproto=dhcp

# -----------------------------------------------

authconfig --useshadow --passalgo=sha256 --kickstart

rootpw "letmein"
user --name=rescue --plaintext --password letmein

timezone --utc UTC

# -----------------------------------------------

bootloader --location=mbr --append="nofb quiet splash=quiet" 

zerombr
clearpart --all

part / --size=1 --ondisk=vda --grow

# -----------------------------------------------

text
reboot --eject

# %packages --ignoremissing
%packages
yum
yum-utils
dhclient
bash-completion 
bash-completion-extras
wget
vim
git
cloud-utils-growpart
@Core
%end

%post --log=/root/kickstart-post.log
  echo "UseDNS no" >> /etc/ssh/sshd_config
  echo "rescue ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/rescue
%end
