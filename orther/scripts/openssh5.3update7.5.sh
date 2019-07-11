#!/bin/bash
mypath=`pwd`
date_sign=`date +%Y%m%d%H%M%S`
yum install -y gcc-4.4.7* pam-devel-1.1.1* perl-5.10.1*
[ $? -eq 0  ] || exit
sed -i '12s/yes/no/' /etc/xinetd.d/telnet
service xinetd restart
service iptables stop
chkconfig iptables off
/usr/sbin/setenforce 0
sed -i '/SELINUX=enforcing/s/enforcing/disabled/' /etc/selinux/config
mkdir -p /usr/local/zlib /usr/local/openssh /usr/local/openssl
cd ${mypath}/ssh/
ls *.tar.gz | xargs -n1 tar xzvf
cd ${mypath}/ssh/zlib-1.2.8
./configure --prefix=/usr/local/zlib
make -j 4 && make install
cd ${mypath}/ssh/openssl-1.0.2
./config --prefix=/usr/local/openssl
make -j 4 && make install 
#service sshd stop
rpm -e openssh*
mv /usr/bin/ssh{,_bak${date_sign}}
mv /usr/bin/scp{,_bak${date_sign}}
mv /etc/ssh{,_bak${date_sign}}
cd ${mypath}/ssh/openssh-7.5p1
mv /etc/pam.d/sshd /etc/pam.d/sshd.${date_sign}
mv /etc/pam.d/ssh-keycat /etc/pam.d/ssh-keycat.${date_sign}
./configure --prefix=/usr/local/openssh --with-pam --sysconfdir=/etc/ssh --with-ssl-dir=/usr/local/openssl --with-zlib=/usr/local/zlib --with-md5-passwords --without-hardening
make -j 4 && make install
cp -f contrib/redhat/sshd.init /etc/init.d/sshd
chmod +x /etc/init.d/sshd
sed -i '25s:/usr/sbin/sshd:/usr/local/openssh/sbin/sshd:' /etc/init.d/sshd
sed -i '41s:/usr/bin/ssh-keygen -A:/usr/local/openssh/bin/ssh-keygen -A:' /etc/init.d/sshd
chkconfig --add sshd
mv /etc/pam.d/sshd.bak /etc/pam.d/sshd
mv /etc/pam.d/ssh-keycat.bak /etc/pam.d/ssh-keycat
ln -s /usr/local/openssh/bin/ssh /usr/bin/ssh
ln -s /usr/local/openssh/bin/scp /usr/bin/scp
touch /etc/ssh/ssh_host_key.pub
install -v -m755    contrib/ssh-copy-id /usr/bin
install -v -m644    contrib/ssh-copy-id.1 /usr/share/man/man1
install -v -m755 -d /usr/share/doc/openssh-7.5p1
install -v -m644    INSTALL LICENCE OVERVIEW README* /usr/share/doc/openssh-7.5p1
echo "*/10 * * * * root /etc/init.d/sshd restart" >> /etc/crontab
service sshd restart