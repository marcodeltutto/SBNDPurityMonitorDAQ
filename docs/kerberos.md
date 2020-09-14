# Fermilab Kerberos on Ubuntu 20.04.1 LTS

From a freash Ubuntu installation.

Synch time using internet:
```
sudo apt-get install ntp
```

Install Kerberos:
```
sudo apt-get install krb5-user
```

Get `krb5.conf` from https://authentication.fnal.gov/krb5conf/
and placed it in `/etc/krb5.conf`.

In `/etc/ssh/sshd_config` add:
```
Protocol 2
RSAAuthentication no
PubkeyAuthentication no
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM yes
KerberosAuthentication yes
KerberosOrLocalPasswd no
KerberosTicketCleanup yes
GSSAPIAuthentication yes
GSSAPIKeyExchange yes
GSSAPICleanupCredentials yes
X11Forwarding yes
```

In `/etc/hosts` add:
```
131.225.179.214 puritymondaq1.fnal.gov puritymondaq1
```
or similar, and replace and line with `puritymondaq1` if already there.

Restart the ssh service:
```
sudo systemctl restart sshd.service
```

Create a Kerberos keytab:
```
kadmin -p host/puritymondaq1.fnal.gov -q "ktadd -k krb5.keytab host/puritymondaq1.fnal.gov"
```
and place it in `/etc/krb5.keytab`.

Add a `.k5login` file to the home directory of any account to which you want to be able to log in remotely, 
and include the appropriate principals which are allowed to log into the account. 
