
echo "======= Install SSH Server ======="
apk add openssh

echo "======= SSH Key generation ======="
ssh-keygen -A
echo "root:admin" | chpasswd

echo "======= Start SSH ======="
sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
/usr/sbin/sshd