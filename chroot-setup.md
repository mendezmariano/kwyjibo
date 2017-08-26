## Chroot setup for running corrections

apt-get install schroot debootstrap

# Edit /etc/schroot/schroot.conf
[xenial]
description=Ubuntu Xenial
location=/var/chroot
priority=3
users=your_username
groups=sbuild
root-groups=root

debootstrap --variant=buildd --arch=amd64 xenial /var/chroot/ http://archive.ubuntu.com/ubuntu/


# Referencies
* https://help.ubuntu.com/community/BasicChroot
* https://gist.github.com/niflostancu/03810a8167edc533b1712551d4f90a14
* https://stackoverflow.com/questions/45829757/python-django-working-on-a-chroot-jail-to-run-a-single-bash-script
