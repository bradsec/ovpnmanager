# OVPNMANAGER
### ovpnmanager.py for IPVanish
A terminal OpenVPN manager currently IPVanish.    
This file is compatable with Debian based systems including Ubuntu and Raspberry Pi OS.  
(Tested with Python 3.6+ on Raspberry Pi 3/4 running Raspberry Pi OS Buster). 
Also compatable with pfSense (FreeBSD) firewall.

### Features:
- Uses Python 3.6+ (built in modules only required).
- Start/stop OpenVPN service
- Fetch and sort IPVanish server list
- Rank servers based on ping latency
- Select random server from top ranked list
- Updates OpenVPN configuration file
- Includes other network functions which can be customised
- Can be run via a cron job at scheduled intervals

### Usage:
- Run `sudo python3 ovpnmanager.py` to will default to setup number of servers with no country filter.
- `-s` specifies how many servers to test `sudo python3 ovpnmanager.py -s 10` will rank from 10 servers
- `-f` specifies a country filter ie. To rank only servers from US for example run `sudo python3 ovpnmanager -f us`
- pfSense depending on version `python3` command may be `python3.7`

## Prerequisites Debian OS / Raspberry Pi:  
(You need to have a working existing IPVanish OpenVPN configuration file)
1. `/etc/openvpn` default openvpn installation path
2. `/etc/openvpn/client.conf` is the default openvpn configuration file
3. A valid IPVanish username and password linked to the configuration file
4. `/etc/defaults/openvpn` contains line `AUTOSTART="client"

Example of `/etc/openvpn/client.conf` file:

```
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
```

#### Example of Debian / Raspberry Pi OS root crontab - example show how to run every 4 hours with US only servers
Presumes ovpnmanager.py has been copied to `/etc/openvpn`  
`0 */4 * * * /usr/bin/python3 /etc/openvpn/ovpnmanager.py -f us`

## Prerequisites pfSense
#### Note: pfSense version recommended for advanced users
Note: There are still some issues with pfSense caching last server. Currently a work around has been added restart the client 3 times to flush out old server. Also depending on your configuration the get_ip_info() function may return your public service provider WAN address and not the VPN address.
1. Recommend backup of pfSense configuration prior to using.  
2. Setup a working OpenVPN IPVanish client through the web admin interface.
3. pfSense Openvpn configuration files are located in `/var/etc/openvpn`.
4. Client files will start with client followed by a number, identify the number and edit the main() function in ovpnmanager.py

#### Example of pfSense root crontab - example show how to run every 4 hours with US only servers
Presumes ovpnmanager.py has been copied to `/var/etc/openvpn`  
`0 */4 * * * /usr/local/bin/python3.7 /var/etc/openvpn/ovpnmanager.py -f us`
