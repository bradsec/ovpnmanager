# debian_ipvanish_ovpnmanager.py
(Tested with Python 3.6+ on Raspberry Pi 3/4 running Raspberry Pi OS Buster)
Should run with other Debian based OS systems.

IPVanish OpenVPN Manager and VPN Server Randomiser
- Start/stop OpenVPN service
- Fetch and sort IPVanish server list
- Rank servers based on ping latency
- Select random server from top ranked list
- Write OpenVPN configuration file

Prerequisites:
(You need to have a working existing IPVanish OpenVPN configuration file)
1. `/etc/openvpn` default openvpn installation path
2. `/etc/openvpn/client.conf` is the default openvpn configuration file
3. A valid IPVanish username and password linked to the configuration file
4. `/etc/defaults/openvpn` contains line `AUTOSTART="client"

Example of `/etc/openvpn/client.conf` file:

`
client
dev tun
proto udp
remote sjc-a14.ipvanish.com 443
resolv-retry infinite
nobind
persist-key
persist-tun
persist-remote-ip
ca ca.ipvanish.com.crt
verify-x509-name sjc-a14.ipvanish.com name
comp-lzo
verb 3
auth SHA256
cipher AES-256-CBC
keysize 256
tls-cipher TLS-DHE-RSA-WITH-AES-256-CBC-SHA:TLS-DHE-DSS-WITH-AES-256-CBC-SHA:TLS-RSA-WITH-AES-256-CBC-SHA
auth-user-pass auth.txt
script-security 2
`
